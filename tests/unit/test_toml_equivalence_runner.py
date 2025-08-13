# ABOUTME: Test runner for SEP TOML-INI equivalence test cases
# ABOUTME: Validates that TOML and INI configurations produce identical parsed results
import json
import os
import shutil
import tempfile
from unittest import mock

import pytest

import botocore.session


def load_equivalence_test_cases():
    """Load equivalence test cases from SEP JSON file."""
    test_file = os.path.join(
        os.path.dirname(__file__), 
        '../../.amazonq/rules/toml-sep/toml-ini-equivalence-tests.json'
    )
    with open(test_file) as f:
        data = json.load(f)
    return data['tests']


@pytest.mark.parametrize("test_case", load_equivalence_test_cases())
def test_toml_ini_equivalence(test_case):
    """Execute TOML-INI equivalence test cases from SEP."""
    ini_input = test_case['iniInput']
    toml_input = test_case['tomlInput']
    expected_output = test_case['expectedOutput']
    
    # Test INI configuration
    ini_temp_dir = tempfile.mkdtemp()
    try:
        with mock.patch.dict(os.environ, {}, clear=True):
            if 'configFile' in ini_input:
                ini_config_path = os.path.join(ini_temp_dir, 'config')
                with open(ini_config_path, 'w') as f:
                    f.write(ini_input['configFile'])
                os.environ['AWS_CONFIG_FILE'] = ini_config_path
            
            if 'credentialsFile' in ini_input:
                ini_creds_path = os.path.join(ini_temp_dir, 'credentials')
                with open(ini_creds_path, 'w') as f:
                    f.write(ini_input['credentialsFile'])
                os.environ['AWS_SHARED_CREDENTIALS_FILE'] = ini_creds_path
            
            ini_session = botocore.session.Session()
            ini_config = ini_session.full_config
    finally:
        shutil.rmtree(ini_temp_dir, ignore_errors=True)
    
    # Test TOML configuration
    toml_temp_dir = tempfile.mkdtemp()
    try:
        with mock.patch.dict(os.environ, {}, clear=True):
            if 'tomlFile' in toml_input:
                toml_config_path = os.path.join(toml_temp_dir, 'config.toml')
                with open(toml_config_path, 'w') as f:
                    f.write(toml_input['tomlFile'])
                os.environ['AWS_CONFIG_FILE_TOML'] = toml_config_path
            
            toml_session = botocore.session.Session()
            toml_config = toml_session.full_config
    finally:
        shutil.rmtree(toml_temp_dir, ignore_errors=True)
    
    # Validate equivalence
    if 'profiles' in expected_output:
        assert ini_config.get('profiles', {}) == toml_config.get('profiles', {})
        assert ini_config.get('profiles', {}) == expected_output['profiles']
    
    if 'ssoSessions' in expected_output:
        assert ini_config.get('sso_sessions', {}) == toml_config.get('sso_sessions', {})
        assert ini_config.get('sso_sessions', {}) == expected_output['ssoSessions']
        
    if 'services' in expected_output:
        assert ini_config.get('services', {}) == toml_config.get('services', {})
        assert ini_config.get('services', {}) == expected_output['services']
