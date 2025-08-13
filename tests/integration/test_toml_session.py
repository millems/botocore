# Copyright 2025 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import os
import shutil
import tempfile

import botocore.session
from tests import BaseEnvVar


class TestTOMLSessionIntegration(BaseEnvVar):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_config_file(self, filename, content):
        """Create a config file (TOML or INI) in the temp directory."""
        full_path = os.path.join(self.temp_dir, filename)
        with open(full_path, 'w') as f:
            f.write(content)
        return full_path

    def test_toml_file_discovery_integration(self):
        # Test that TOML configuration is loaded when environment variable is set
        toml_content = '''
[profile.dev]
region = "us-west-2"
output = "json"
use_fips = true
'''
        toml_file = self.create_config_file('config.toml', toml_content)
        
        # Set environment variable to point to TOML file
        self.environ['AWS_CONFIG_FILE_TOML'] = toml_file
        
        session = botocore.session.Session()
        config = session.full_config
        
        # Verify TOML configuration is loaded
        self.assertIn('profiles', config)
        self.assertIn('dev', config['profiles'])
        
        dev_profile = config['profiles']['dev']
        self.assertEqual(dev_profile['region'], 'us-west-2')
        self.assertEqual(dev_profile['output'], 'json')
        self.assertEqual(dev_profile['use_fips'], 'true')  # Normalized to string

    def test_precedence_logic_integration(self):
        # Test that TOML takes precedence over INI when both exist
        toml_content = '''
[profile.test]
region = "us-west-2"
source = "toml"
'''
        ini_content = '''
[profile test]
region = us-east-1
source = ini
'''
        
        toml_file = self.create_config_file('config.toml', toml_content)
        ini_file = self.create_config_file('config', ini_content)
        
        # Set both environment variables
        self.environ['AWS_CONFIG_FILE_TOML'] = toml_file
        self.environ['AWS_CONFIG_FILE'] = ini_file
        
        session = botocore.session.Session()
        config = session.full_config
        
        # Verify TOML takes precedence
        self.assertIn('profiles', config)
        self.assertIn('test', config['profiles'])
        
        test_profile = config['profiles']['test']
        self.assertEqual(test_profile['region'], 'us-west-2')
        self.assertEqual(test_profile['source'], 'toml')

    def test_credentials_not_merged_with_toml_integration(self):
        # Test that credentials file is NOT merged with TOML configuration
        toml_content = '''
[profile.dev]
region = "us-west-2"
output = "json"
'''
        
        credentials_content = '''
[dev]
aws_access_key_id = AKIATEST
aws_secret_access_key = secret
'''
        
        toml_file = self.create_config_file('config.toml', toml_content)
        creds_file = self.create_config_file('credentials', credentials_content)
        
        # Set environment variables
        self.environ['AWS_CONFIG_FILE_TOML'] = toml_file
        self.environ['AWS_SHARED_CREDENTIALS_FILE'] = creds_file
        
        session = botocore.session.Session()
        config = session.full_config
        
        # Verify TOML config is loaded but credentials are NOT merged
        self.assertIn('profiles', config)
        self.assertIn('dev', config['profiles'])
        
        dev_profile = config['profiles']['dev']
        self.assertEqual(dev_profile['region'], 'us-west-2')
        self.assertEqual(dev_profile['output'], 'json')
        
        # Credentials should NOT be merged with TOML
        self.assertNotIn('aws_access_key_id', dev_profile)
        self.assertNotIn('aws_secret_access_key', dev_profile)

    def test_client_creation_integration(self):
        # Test that clients can be created using TOML configuration
        toml_content = '''
[profile.test]
region = "us-west-2"
output = "json"

[services.s3]
signature_version = "s3v4"
max_concurrent_requests = 20
'''
        
        toml_file = self.create_config_file('config.toml', toml_content)
        self.environ['AWS_CONFIG_FILE_TOML'] = toml_file
        
        session = botocore.session.Session()
        
        # Create a client using the session with TOML config
        # Note: This will fail without credentials, but we're testing config loading
        try:
            client = session.create_client('s3', region_name='us-west-2')
            # If we get here, the client was created successfully
            self.assertEqual(client.meta.region_name, 'us-west-2')
        except Exception:
            # Expected to fail without credentials, but config should be loaded
            config = session.full_config
            self.assertIn('profiles', config)
            self.assertIn('services', config)
            self.assertEqual(config['services']['s3']['signature_version'], 's3v4')

    def test_environment_variable_warning_integration(self):
        # Test that warning is logged when both environment variables are set
        toml_content = '''
[profile.test]
region = "us-west-2"
'''
        ini_content = '''
[profile test]
region = us-east-1
'''
        
        toml_file = self.create_config_file('config.toml', toml_content)
        ini_file = self.create_config_file('config', ini_content)
        
        # Set both environment variables
        self.environ['AWS_CONFIG_FILE_TOML'] = toml_file
        self.environ['AWS_CONFIG_FILE'] = ini_file
        
        # Capture logging
        from tests import mock
        
        with mock.patch('botocore.session.logger') as mock_logger:
            session = botocore.session.Session()
            config = session.full_config
            
            # Verify warning was logged
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            self.assertIn('Both AWS_CONFIG_FILE_TOML and INI', warning_call)
            self.assertIn('Using TOML configuration', warning_call)
            
            # Verify TOML was used
            self.assertEqual(config['profiles']['test']['region'], 'us-west-2')

    def test_default_file_location_integration(self):
        # Test that default TOML file location is discovered
        # Create TOML file at default location (mocked)
        default_toml_path = '~/.aws/config.toml'
        
        # Mock the default file existing
        from tests import mock
        
        with mock.patch('os.path.exists') as mock_exists:
            with mock.patch('botocore.configloader.raw_toml_parse') as mock_parse:
                # Mock file exists at default location
                def exists_side_effect(path):
                    return path == os.path.expanduser(default_toml_path)
                
                mock_exists.side_effect = exists_side_effect
                
                # Mock parsing to return expected structure
                mock_parse.return_value = {
                    'profile': {
                        'default': {
                            'region': 'us-east-1',
                            'output': 'table'
                        }
                    }
                }
                
                session = botocore.session.Session()
                config = session.full_config
                
                # Verify default TOML file was discovered and parsed
                mock_parse.assert_called_once_with(default_toml_path)
                self.assertIn('profiles', config)
                self.assertIn('default', config['profiles'])
                self.assertEqual(config['profiles']['default']['region'], 'us-east-1')

    def test_toml_fallback_to_ini_integration(self):
        # Test that system falls back to INI when TOML file doesn't exist
        ini_content = '''
[profile test]
region = us-east-1
output = json
'''
        
        ini_file = self.create_config_file('config', ini_content)
        
        # Set INI file but no TOML file
        self.environ['AWS_CONFIG_FILE'] = ini_file
        
        # Mock default TOML file not existing
        from tests import mock
        
        with mock.patch('os.path.exists', return_value=False):
            session = botocore.session.Session()
            config = session.full_config
            
            # Verify INI configuration is loaded as fallback
            self.assertIn('profiles', config)
            self.assertIn('test', config['profiles'])
            self.assertEqual(config['profiles']['test']['region'], 'us-east-1')
            self.assertEqual(config['profiles']['test']['output'], 'json')

    def test_toml_complex_configuration_integration(self):
        # Test complex TOML configuration with multiple sections
        toml_content = '''
[profile.dev]
region = "us-west-2"
output = "json"
sigv4a_signing_region_set = ["us-west-2", "us-east-1"]

[profile.prod]
region = "us-east-1"
output = "table"
use_fips = true

[sso-session.my-sso]
sso_start_url = "https://example.com"
sso_region = "us-east-1"

[services.s3]
signature_version = "s3v4"
max_concurrent_requests = 20
'''
        
        toml_file = self.create_config_file('complex.toml', toml_content)
        self.environ['AWS_CONFIG_FILE_TOML'] = toml_file
        
        session = botocore.session.Session()
        config = session.full_config
        
        # Verify all sections are loaded correctly
        self.assertIn('profiles', config)
        self.assertIn('sso_sessions', config)
        self.assertIn('services', config)
        
        # Check profiles
        self.assertIn('dev', config['profiles'])
        self.assertIn('prod', config['profiles'])
        
        dev_profile = config['profiles']['dev']
        self.assertEqual(dev_profile['region'], 'us-west-2')
        self.assertEqual(dev_profile['sigv4a_signing_region_set'], 'us-west-2,us-east-1')
        
        prod_profile = config['profiles']['prod']
        self.assertEqual(prod_profile['region'], 'us-east-1')
        self.assertEqual(prod_profile['use_fips'], 'true')
        
        # Check SSO sessions
        self.assertIn('my-sso', config['sso_sessions'])
        sso_session = config['sso_sessions']['my-sso']
        self.assertEqual(sso_session['sso_start_url'], 'https://example.com')
        
        # Check services
        self.assertIn('s3', config['services'])
        s3_service = config['services']['s3']
        self.assertEqual(s3_service['signature_version'], 's3v4')
        self.assertEqual(s3_service['max_concurrent_requests'], '20')
