# ABOUTME: Test runner for SEP TOML configuration test cases
# ABOUTME: Executes official SEP test suite to validate TOML implementation compliance
import json
import os
import shutil
import tempfile
from unittest import mock

import pytest

import botocore.exceptions
import botocore.session


def load_test_cases():
    """Load test cases from SEP JSON file."""
    test_file = os.path.join(
        os.path.dirname(__file__), 
        'toml/toml-configuration-test-cases.json'
    )
    with open(test_file) as f:
        data = json.load(f)
    return data['tests']


@pytest.mark.parametrize("test_case", load_test_cases())
def test_toml_configuration_cases(test_case):
    """Execute individual TOML configuration test cases from SEP."""
    test_input = test_case['input']
    expected_output = test_case['output']
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        with mock.patch.dict(os.environ, {}, clear=True):
            # Set up environment variables if specified
            if 'environmentVariables' in test_input:
                for key, value in test_input['environmentVariables'].items():
                    os.environ[key] = value
            
            # Create temporary files
            if 'tomlFile' in test_input:
                toml_path = os.path.join(temp_dir, 'config.toml')
                with open(toml_path, 'w') as f:
                    f.write(test_input['tomlFile'])
                if 'AWS_CONFIG_FILE_TOML' not in os.environ:
                    os.environ['AWS_CONFIG_FILE_TOML'] = toml_path
            
            if 'configFile' in test_input:
                ini_path = os.path.join(temp_dir, 'config')
                with open(ini_path, 'w') as f:
                    f.write(test_input['configFile'])
                os.environ['AWS_CONFIG_FILE'] = ini_path
                
            if 'credentialsFile' in test_input:
                creds_path = os.path.join(temp_dir, 'credentials')
                with open(creds_path, 'w') as f:
                    f.write(test_input['credentialsFile'])
                os.environ['AWS_SHARED_CREDENTIALS_FILE'] = creds_path
            
            # Execute test
            if 'errorContaining' in expected_output:
                # Test expects an error
                with pytest.raises(Exception) as exc_info:
                    session = botocore.session.Session()
                    session.full_config
                
                assert expected_output['errorContaining'] in str(exc_info.value)
            else:
                # Test expects successful parsing
                session = botocore.session.Session()
                config = session.full_config
                
                # Validate expected output structure
                if 'profiles' in expected_output:
                    assert 'profiles' in config
                    assert config['profiles'] == expected_output['profiles']
                
                if 'ssoSessions' in expected_output:
                    assert 'sso_sessions' in config
                    assert config['sso_sessions'] == expected_output['ssoSessions']
                    
                if 'services' in expected_output:
                    assert 'services' in config
                    assert config['services'] == expected_output['services']
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
