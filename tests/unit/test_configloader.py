#!/usr/bin/env
# Copyright (c) 2012-2013 Mitch Garnaat http://garnaat.org/
# Copyright 2012-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import pytest
import botocore.exceptions
from botocore.configloader import (
    load_config,
    multi_file_load_config,
    raw_config_parse,
)
from tests import mock, unittest


def path(filename):
    directory = os.path.join(os.path.dirname(__file__), 'cfg')
    if isinstance(filename, bytes):
        directory = directory.encode('latin-1')
    return os.path.join(directory, filename)


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def create_config_file(self, filename):
        contents = (
            '[default]\n'
            'aws_access_key_id = foo\n'
            'aws_secret_access_key = bar\n\n'
            '[profile "personal"]\n'
            'aws_access_key_id = fie\n'
            'aws_secret_access_key = baz\n'
            'aws_security_token = fiebaz\n'
        )

        directory = self.tempdir
        if isinstance(filename, bytes):
            directory = directory.encode('latin-1')
        full_path = os.path.join(directory, filename)

        with open(full_path, 'w') as f:
            f.write(contents)
        return full_path

    def test_config_not_found(self):
        with self.assertRaises(botocore.exceptions.ConfigNotFound):
            raw_config_parse(path('aws_config_notfound'))

    def test_config_parse_error(self):
        filename = path('aws_config_bad')
        with self.assertRaises(botocore.exceptions.ConfigParseError):
            raw_config_parse(filename)

    def test_config_parse_error_bad_unicode(self):
        filename = path('aws_config_badbytes')
        with self.assertRaises(botocore.exceptions.ConfigParseError):
            raw_config_parse(filename)

    def test_config_parse_error_filesystem_encoding_none(self):
        filename = path('aws_config_bad')
        with mock.patch('sys.getfilesystemencoding') as encoding:
            encoding.return_value = None
            with self.assertRaises(botocore.exceptions.ConfigParseError):
                raw_config_parse(filename)

    def test_config(self):
        loaded_config = raw_config_parse(path('aws_config'))
        self.assertIn('default', loaded_config)
        self.assertIn('profile "personal"', loaded_config)

    def test_profile_map_conversion(self):
        loaded_config = load_config(path('aws_config'))
        self.assertIn('profiles', loaded_config)
        self.assertEqual(
            sorted(loaded_config['profiles'].keys()), ['default', 'personal']
        )

    def test_bad_profiles_are_ignored(self):
        filename = path('aws_bad_profile')
        loaded_config = load_config(filename)
        self.assertEqual(len(loaded_config['profiles']), 3)
        profiles = loaded_config['profiles']
        self.assertIn('my profile', profiles)
        self.assertIn('personal1', profiles)
        self.assertIn('default', profiles)

    def test_nested_hierarchy_parsing(self):
        filename = path('aws_config_nested')
        loaded_config = load_config(filename)
        config = loaded_config['profiles']['default']
        self.assertEqual(config['aws_access_key_id'], 'foo')
        self.assertEqual(config['region'], 'us-west-2')
        self.assertEqual(config['s3']['signature_version'], 's3v4')
        self.assertEqual(config['cloudwatch']['signature_version'], 'v4')

    def test_nested_hierarchy_with_no_subsection_parsing(self):
        filename = path('aws_config_nested')
        raw_config = raw_config_parse(filename, False)['default']
        self.assertEqual(raw_config['aws_access_key_id'], 'foo')
        self.assertEqual(raw_config['region'], 'us-west-2')
        # Specifying False for pase_subsections in raw_config_parse
        # will make sure that indented sections such as singature_version
        # will not be treated as another subsection but rather
        # its literal value.
        self.assertEqual(raw_config['cloudwatch'], '\nsignature_version = v4')
        self.assertEqual(
            raw_config['s3'],
            '\nsignature_version = s3v4\naddressing_style = path',
        )

    def test_nested_bad_config(self):
        filename = path('aws_config_nested_bad')
        with self.assertRaises(botocore.exceptions.ConfigParseError):
            load_config(filename)

    def test_nested_bad_config_filesystem_encoding_none(self):
        filename = path('aws_config_nested_bad')
        with mock.patch('sys.getfilesystemencoding') as encoding:
            encoding.return_value = None
            with self.assertRaises(botocore.exceptions.ConfigParseError):
                load_config(filename)

    def test_multi_file_load(self):
        filenames = [
            path('aws_config_other'),
            path('aws_config'),
            path('aws_third_config'),
            path('aws_config_notfound'),
        ]
        loaded_config = multi_file_load_config(*filenames)
        config = loaded_config['profiles']['default']
        self.assertEqual(config['aws_access_key_id'], 'other_foo')
        self.assertEqual(config['aws_secret_access_key'], 'other_bar')
        second_config = loaded_config['profiles']['personal']
        self.assertEqual(second_config['aws_access_key_id'], 'fie')
        self.assertEqual(second_config['aws_secret_access_key'], 'baz')
        self.assertEqual(second_config['aws_security_token'], 'fiebaz')
        third_config = loaded_config['profiles']['third']
        self.assertEqual(third_config['aws_access_key_id'], 'third_fie')
        self.assertEqual(third_config['aws_secret_access_key'], 'third_baz')
        self.assertEqual(third_config['aws_security_token'], 'third_fiebaz')

    def test_unicode_bytes_path_not_found(self):
        with self.assertRaises(botocore.exceptions.ConfigNotFound):
            with mock.patch('sys.getfilesystemencoding') as encoding:
                encoding.return_value = 'utf-8'
                load_config(path(b'\xe2\x9c\x93'))

    def test_unicode_bytes_path_not_found_filesystem_encoding_none(self):
        with mock.patch('sys.getfilesystemencoding') as encoding:
            encoding.return_value = None
            with self.assertRaises(botocore.exceptions.ConfigNotFound):
                load_config(path(b'\xe2\x9c\x93'))

    def test_unicode_bytes_path(self):
        filename = self.create_config_file(b'aws_config_unicode\xe2\x9c\x93')
        with mock.patch('sys.getfilesystemencoding') as encoding:
            encoding.return_value = 'utf-8'
            loaded_config = load_config(filename)
        self.assertIn('default', loaded_config['profiles'])
        self.assertIn('personal', loaded_config['profiles'])

    def test_sso_session_config(self):
        filename = path('aws_sso_session_config')
        loaded_config = load_config(filename)
        self.assertIn('profiles', loaded_config)
        self.assertIn('default', loaded_config['profiles'])
        self.assertIn('sso_sessions', loaded_config)
        self.assertIn('sso', loaded_config['sso_sessions'])
        sso_config = loaded_config['sso_sessions']['sso']
        self.assertEqual(sso_config['sso_region'], 'us-east-1')
        self.assertEqual(sso_config['sso_start_url'], 'https://example.com')

    def test_services_config(self):
        filename = path('aws_services_config')
        loaded_config = load_config(filename)
        self.assertIn('profiles', loaded_config)
        self.assertIn('default', loaded_config['profiles'])
        self.assertIn('services', loaded_config)
        self.assertIn('my-services', loaded_config['services'])
        services_config = loaded_config['services']['my-services']
        self.assertIn('s3', services_config)
        self.assertIn('dynamodb', services_config)
        self.assertEqual(
            services_config['s3']['endpoint_url'], 'https://localhost:5678/'
        )
        self.assertEqual(
            services_config['dynamodb']['endpoint_url'],
            'https://localhost:8888/',
        )

    def create_toml_config_file(self, filename, content):
        """Helper method to create TOML config files for testing."""
        full_path = os.path.join(self.tempdir, filename)
        with open(full_path, 'w') as f:
            f.write(content)
        return full_path

    def test_raw_toml_parse_valid_file(self):
        # Test parsing a valid TOML file with normalized types
        toml_content = '''
[profile.dev]
region = "us-west-2"
output = "json"
use_fips = true
timeout = 30

[profile.prod]
region = "us-east-1"
use_fips = false
'''
        filename = self.create_toml_config_file('test_config.toml', toml_content)
        
        # Import here to avoid import errors if tomllib not available
        from botocore.configloader import raw_toml_parse
        
        result = raw_toml_parse(filename)
        
        # Verify structure and normalized types (should match INI format)
        self.assertIn('profile', result)
        self.assertIn('dev', result['profile'])
        self.assertIn('prod', result['profile'])
        
        dev_config = result['profile']['dev']
        self.assertEqual(dev_config['region'], 'us-west-2')
        self.assertEqual(dev_config['output'], 'json')
        self.assertEqual(dev_config['use_fips'], 'true')  # Normalized to string
        self.assertEqual(dev_config['timeout'], '30')     # Normalized to string
        
        prod_config = result['profile']['prod']
        self.assertEqual(prod_config['region'], 'us-east-1')
        self.assertEqual(prod_config['use_fips'], 'false')  # Normalized to string

    def test_raw_toml_parse_file_not_found(self):
        # Test that ConfigNotFound is raised for non-existent files
        from botocore.configloader import raw_toml_parse
        
        with self.assertRaises(botocore.exceptions.ConfigNotFound):
            raw_toml_parse('/path/to/nonexistent/file.toml')

    def test_raw_toml_parse_syntax_error(self):
        # Test that ConfigParseError is raised for malformed TOML
        invalid_toml = '''
[profile.dev
region = "us-west-2"  # Missing closing bracket
'''
        filename = self.create_toml_config_file('invalid.toml', invalid_toml)
        
        from botocore.configloader import raw_toml_parse
        
        with self.assertRaises(botocore.exceptions.ConfigParseError):
            raw_toml_parse(filename)

    def test_load_toml_config_structure(self):
        # Test that load_toml_config returns proper structure
        toml_content = '''
[profile.dev]
region = "us-west-2"
output = "json"

[sso-session.my-session]
sso_start_url = "https://example.com"

[services.my-service]
endpoint_url = "https://localhost:8000"
'''
        filename = self.create_toml_config_file('structured.toml', toml_content)
        
        from botocore.configloader import load_toml_config
        
        result = load_toml_config(filename)
        
        # Should have same structure as INI config
        self.assertIn('profiles', result)
        self.assertIn('sso_sessions', result)
        self.assertIn('services', result)
        
        # Check profile mapping
        self.assertIn('dev', result['profiles'])
        self.assertEqual(result['profiles']['dev']['region'], 'us-west-2')
        
        # Check sso-session mapping
        self.assertIn('my-session', result['sso_sessions'])
        self.assertEqual(result['sso_sessions']['my-session']['sso_start_url'], 'https://example.com')
        
        # Check services mapping
        self.assertIn('my-service', result['services'])
        self.assertEqual(result['services']['my-service']['endpoint_url'], 'https://localhost:8000')

    def test_toml_data_type_preservation(self):
        # Test that TOML native data types are normalized to INI format
        toml_content = '''
[profile.test]
string_val = "hello"
int_val = 42
float_val = 3.14
bool_true = true
bool_false = false
array_val = ["a", "b", "c"]
'''
        filename = self.create_toml_config_file('types.toml', toml_content)
        
        from botocore.configloader import raw_toml_parse
        
        result = raw_toml_parse(filename)
        config = result['profile']['test']
        
        # Verify data types are normalized to match INI format
        self.assertIsInstance(config['string_val'], str)
        self.assertEqual(config['string_val'], 'hello')
        
        self.assertIsInstance(config['int_val'], str)  # Normalized to string
        self.assertEqual(config['int_val'], '42')
        
        self.assertIsInstance(config['float_val'], str)  # Normalized to string
        self.assertEqual(config['float_val'], '3.14')
        
        self.assertIsInstance(config['bool_true'], str)  # Normalized to string
        self.assertEqual(config['bool_true'], 'true')
        
        self.assertIsInstance(config['bool_false'], str)  # Normalized to string
        self.assertEqual(config['bool_false'], 'false')
        
        self.assertIsInstance(config['array_val'], str)  # Normalized to string
        self.assertEqual(config['array_val'], 'a,b,c')

    def test_build_toml_profile_map_profile_sections(self):
        # Test profile section parsing with dot notation
        toml_config = {
            'profile': {
                'default': {
                    'region': 'us-east-1',
                    'output': 'json'
                },
                'dev': {
                    'region': 'us-west-2',
                    'use_fips': True
                }
            }
        }
        
        from botocore.configloader import build_toml_profile_map
        
        result = build_toml_profile_map(toml_config)
        
        # Verify profiles structure
        self.assertIn('profiles', result)
        self.assertIn('default', result['profiles'])
        self.assertIn('dev', result['profiles'])
        
        # Verify profile content
        self.assertEqual(result['profiles']['default']['region'], 'us-east-1')
        self.assertEqual(result['profiles']['default']['output'], 'json')
        self.assertEqual(result['profiles']['dev']['region'], 'us-west-2')
        self.assertIs(result['profiles']['dev']['use_fips'], True)

    def test_build_toml_profile_map_sso_sessions(self):
        # Test SSO session parsing
        toml_config = {
            'sso-session': {
                'my-sso': {
                    'sso_start_url': 'https://example.com',
                    'sso_region': 'us-east-1'
                },
                'dev-sso': {
                    'sso_start_url': 'https://dev.example.com'
                }
            }
        }
        
        from botocore.configloader import build_toml_profile_map
        
        result = build_toml_profile_map(toml_config)
        
        # Verify sso_sessions structure
        self.assertIn('sso_sessions', result)
        self.assertIn('my-sso', result['sso_sessions'])
        self.assertIn('dev-sso', result['sso_sessions'])
        
        # Verify sso session content
        self.assertEqual(result['sso_sessions']['my-sso']['sso_start_url'], 'https://example.com')
        self.assertEqual(result['sso_sessions']['my-sso']['sso_region'], 'us-east-1')
        self.assertEqual(result['sso_sessions']['dev-sso']['sso_start_url'], 'https://dev.example.com')

    def test_build_toml_profile_map_services(self):
        # Test services section parsing
        toml_config = {
            'services': {
                's3': {
                    'endpoint_url': 'https://localhost:9000',
                    'signature_version': 's3v4'
                },
                'dynamodb': {
                    'endpoint_url': 'https://localhost:8000'
                }
            }
        }
        
        from botocore.configloader import build_toml_profile_map
        
        result = build_toml_profile_map(toml_config)
        
        # Verify services structure
        self.assertIn('services', result)
        self.assertIn('s3', result['services'])
        self.assertIn('dynamodb', result['services'])
        
        # Verify services content
        self.assertEqual(result['services']['s3']['endpoint_url'], 'https://localhost:9000')
        self.assertEqual(result['services']['s3']['signature_version'], 's3v4')
        self.assertEqual(result['services']['dynamodb']['endpoint_url'], 'https://localhost:8000')

    def test_build_toml_profile_map_top_level_preservation(self):
        # Test that custom top-level sections are preserved
        toml_config = {
            'profile': {
                'default': {'region': 'us-east-1'}
            },
            'custom_section': {
                'custom_key': 'custom_value'
            },
            'another_section': {
                'nested': {
                    'key': 'value'
                }
            }
        }
        
        from botocore.configloader import build_toml_profile_map
        
        result = build_toml_profile_map(toml_config)
        
        # Verify standard sections
        self.assertIn('profiles', result)
        self.assertIn('sso_sessions', result)
        self.assertIn('services', result)
        
        # Verify custom sections are preserved
        self.assertIn('custom_section', result)
        self.assertIn('another_section', result)
        
        # Verify custom section content
        self.assertEqual(result['custom_section']['custom_key'], 'custom_value')
        self.assertEqual(result['another_section']['nested']['key'], 'value')

    def test_build_toml_profile_map_output_structure_compatibility(self):
        # Test that output structure matches INI build_profile_map format
        toml_config = {
            'profile': {
                'default': {'region': 'us-east-1'},
                'dev': {'region': 'us-west-2'}
            },
            'sso-session': {
                'my-session': {'sso_start_url': 'https://example.com'}
            },
            'services': {
                's3': {'endpoint_url': 'https://localhost:9000'}
            },
            'custom': {'key': 'value'}
        }
        
        from botocore.configloader import build_toml_profile_map
        
        result = build_toml_profile_map(toml_config)
        
        # Verify exact structure matches INI format
        expected_keys = {'profiles', 'sso_sessions', 'services', 'custom'}
        self.assertEqual(set(result.keys()), expected_keys)
        
        # Verify profiles structure
        self.assertIsInstance(result['profiles'], dict)
        self.assertEqual(set(result['profiles'].keys()), {'default', 'dev'})
        
        # Verify sso_sessions structure
        self.assertIsInstance(result['sso_sessions'], dict)
        self.assertEqual(set(result['sso_sessions'].keys()), {'my-session'})
        
        # Verify services structure
        self.assertIsInstance(result['services'], dict)
        self.assertEqual(set(result['services'].keys()), {'s3'})

    def test_normalize_toml_to_ini_types(self):
        """Test TOML to INI type normalization for various data types."""
        from botocore.configloader import _normalize_toml_to_ini_types
        
        test_cases = [
            # Array conversion
            (
                {'sigv4a_signing_region_set': ['us-east-1', 'us-west-2'], 'other_array': ['a', 'b', 'c']},
                {'sigv4a_signing_region_set': 'us-east-1,us-west-2', 'other_array': 'a,b,c'},
                "array_conversion"
            ),
            # Boolean conversion
            (
                {'use_dualstack_endpoint': True, 'use_fips': False},
                {'use_dualstack_endpoint': 'true', 'use_fips': 'false'},
                "boolean_conversion"
            ),
            # Integer conversion
            (
                {'duration_seconds': 3600, 'timeout': 30},
                {'duration_seconds': '3600', 'timeout': '30'},
                "integer_conversion"
            ),
            # String preservation
            (
                {'region': 'us-west-2', 'output': 'json'},
                {'region': 'us-west-2', 'output': 'json'},
                "string_preservation"
            ),
            # Empty array handling
            (
                {'sigv4a_signing_region_set': []},
                {'sigv4a_signing_region_set': ''},
                "empty_array_handling"
            ),
        ]
        
        for input_data, expected_output, test_name in test_cases:
            with self.subTest(test_case=test_name):
                result = _normalize_toml_to_ini_types(input_data)
                for key, expected_value in expected_output.items():
                    self.assertEqual(result[key], expected_value)

    def test_normalize_toml_to_ini_types_nested_processing(self):
        # Test that nested dictionaries are processed recursively
        config = {
            'profile': {
                'dev': {
                    'sigv4a_signing_region_set': ['us-east-1', 'us-west-2'],
                    'use_fips': True,
                    'timeout': 30,
                    'region': 'us-west-2'
                }
            },
            'services': {
                's3': {
                    'use_dualstack_endpoint': False
                }
            }
        }
        
        from botocore.configloader import _normalize_toml_to_ini_types
        
        result = _normalize_toml_to_ini_types(config)
        
        # Should process nested dictionaries recursively
        dev_profile = result['profile']['dev']
        self.assertEqual(dev_profile['sigv4a_signing_region_set'], 'us-east-1,us-west-2')
        self.assertEqual(dev_profile['use_fips'], 'true')
        self.assertEqual(dev_profile['timeout'], '30')
        self.assertEqual(dev_profile['region'], 'us-west-2')
        
        s3_service = result['services']['s3']
        self.assertEqual(s3_service['use_dualstack_endpoint'], 'false')

    def test_raw_toml_parse_missing_library(self):
        # Test that ConfigParseError is raised when TOML library is unavailable
        toml_content = '''
[profile.dev]
region = "us-west-2"
'''
        filename = self.create_toml_config_file('test.toml', toml_content)
        
        from botocore.configloader import raw_toml_parse
        import botocore.configloader
        
        # Mock TOML_AVAILABLE to simulate missing library
        with mock.patch.object(botocore.configloader, 'TOML_AVAILABLE', False):
            with self.assertRaises(botocore.exceptions.ConfigParseError) as cm:
                raw_toml_parse(filename)
            
            # Should include helpful message about Python version requirements
            error_msg = cm.exception.kwargs['error']
            self.assertIn('Python 3.11+', error_msg)
            self.assertIn('tomli package', error_msg)

    def test_raw_toml_parse_file_path_expansion(self):
        # Test that file paths are properly expanded (expandvars, expanduser)
        toml_content = '''
[profile.test]
region = "us-west-2"
'''
        filename = self.create_toml_config_file('path_test.toml', toml_content)
        
        from botocore.configloader import raw_toml_parse
        
        # Test with environment variable expansion
        with mock.patch.dict(os.environ, {'TEST_CONFIG': filename}):
            result = raw_toml_parse('$TEST_CONFIG')
            self.assertIn('profile', result)
            self.assertEqual(result['profile']['test']['region'], 'us-west-2')
        
        # Test with user home expansion (mock expanduser)
        with mock.patch('os.path.expanduser', return_value=filename):
            with mock.patch('os.path.isfile', return_value=True):
                result = raw_toml_parse('~/config.toml')
                self.assertIn('profile', result)
                self.assertEqual(result['profile']['test']['region'], 'us-west-2')

    def test_raw_toml_parse_empty_file(self):
        # Test parsing an empty TOML file
        empty_toml = ''
        filename = self.create_toml_config_file('empty.toml', empty_toml)
        
        from botocore.configloader import raw_toml_parse
        
        result = raw_toml_parse(filename)
        
        # Should return empty structure but not crash
        self.assertIsInstance(result, dict)

    def test_raw_toml_parse_special_characters(self):
        # Test parsing TOML with special characters and unicode
        toml_content = '''
[profile."special-name"]
region = "us-west-2"
description = "Test with special chars: éñ中文"

[profile.unicode]
name = "测试"
emoji = "🚀"
'''
        filename = self.create_toml_config_file('special.toml', toml_content)
        
        from botocore.configloader import raw_toml_parse
        
        result = raw_toml_parse(filename)
        
        # Should handle special characters correctly
        self.assertIn('special-name', result['profile'])
        self.assertEqual(result['profile']['special-name']['region'], 'us-west-2')
        self.assertIn('éñ中文', result['profile']['special-name']['description'])
        
        self.assertIn('unicode', result['profile'])
        self.assertEqual(result['profile']['unicode']['name'], '测试')
        self.assertEqual(result['profile']['unicode']['emoji'], '🚀')

    def test_raw_toml_parse_complex_nested_structure(self):
        # Test parsing complex nested TOML structures
        toml_content = '''
[profile.dev]
region = "us-west-2"
sigv4a_signing_region_set = ["us-west-2", "us-east-1"]

[profile.dev.s3]
use_dualstack_endpoint = true
max_bandwidth = 1000

[sso-session.my-sso]
sso_start_url = "https://example.com"
sso_region = "us-east-1"

[services.s3]
max_concurrent_requests = 20
signature_version = "s3v4"
'''
        filename = self.create_toml_config_file('complex.toml', toml_content)
        
        from botocore.configloader import raw_toml_parse
        
        result = raw_toml_parse(filename)
        
        # Verify complex structure is parsed correctly
        self.assertIn('profile', result)
        self.assertIn('sso-session', result)
        self.assertIn('services', result)
        
        # Check nested profile structure
        dev_profile = result['profile']['dev']
        self.assertEqual(dev_profile['region'], 'us-west-2')
        self.assertEqual(dev_profile['sigv4a_signing_region_set'], 'us-west-2,us-east-1')
        
        # Check nested s3 config (should be flattened in normalized output)
        self.assertIn('s3', dev_profile)
        self.assertEqual(dev_profile['s3']['use_dualstack_endpoint'], 'true')
        self.assertEqual(dev_profile['s3']['max_bandwidth'], '1000')

    def test_load_toml_config_with_none_filename(self):
        # Test load_toml_config behavior with None filename (should raise ConfigNotFound)
        from botocore.configloader import load_toml_config
        
        # TOML version raises ConfigNotFound for None filename (different from INI)
        with self.assertRaises(botocore.exceptions.ConfigNotFound):
            load_toml_config(None)


if __name__ == "__main__":
    unittest.main()
