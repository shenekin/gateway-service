"""
Unit tests for run.py unified entry point
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestRunEntryPoint:
    """Test cases for run.py entry point"""
    
    def test_parse_arguments_default(self):
        """Test parsing arguments with default values"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py']):
            args = parse_arguments()
            
            assert args.env is None
            assert args.host is None
            assert args.port is None
            assert args.reload is False
            assert args.workers == 1
            assert args.deployment_mode is None
    
    def test_parse_arguments_with_env(self):
        """Test parsing arguments with environment specified"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--env', 'dev']):
            args = parse_arguments()
            
            assert args.env == 'dev'
    
    def test_parse_arguments_with_host_port(self):
        """Test parsing arguments with host and port"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--host', '127.0.0.1', '--port', '9000']):
            args = parse_arguments()
            
            assert args.host == '127.0.0.1'
            assert args.port == 9000
    
    def test_parse_arguments_with_reload(self):
        """Test parsing arguments with reload flag"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--reload']):
            args = parse_arguments()
            
            assert args.reload is True
    
    def test_parse_arguments_with_workers(self):
        """Test parsing arguments with workers"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--workers', '4']):
            args = parse_arguments()
            
            assert args.workers == 4
    
    def test_parse_arguments_with_deployment_mode(self):
        """Test parsing arguments with deployment mode"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--deployment-mode', 'cluster']):
            args = parse_arguments()
            
            assert args.deployment_mode == 'cluster'
    
    def test_parse_arguments_with_create_env(self):
        """Test parsing arguments with create-env flag"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--create-env']):
            args = parse_arguments()
            
            assert args.create_env is True
    
    def test_parse_arguments_with_init_db(self):
        """Test parsing arguments with init-db flag"""
        from run import parse_arguments
        
        with patch('sys.argv', ['run.py', '--init-db']):
            args = parse_arguments()
            
            assert args.init_db is True
    
    def test_initialize_environment_with_create_env(self):
        """Test environment initialization with auto-creation"""
        from run import initialize_environment
        from unittest.mock import patch
        
        args = Mock()
        args.create_env = True
        args.env = 'dev'
        args.deployment_mode = 'single'
        
        with patch('run.EnvironmentLoader.load_environment_with_auto_create') as mock_load:
            initialize_environment(args)
            
            mock_load.assert_called_once_with(
                env_name='dev',
                deployment_mode='single'
            )
    
    def test_initialize_environment_without_create_env(self):
        """Test environment initialization without auto-creation"""
        from run import initialize_environment
        from unittest.mock import patch
        
        args = Mock()
        args.create_env = False
        args.env = 'dev'
        
        with patch('run.EnvironmentLoader.load_environment') as mock_load:
            initialize_environment(args)
            
            mock_load.assert_called_once_with(env_name='dev')
    
    def test_initialize_database_success(self):
        """Test database initialization success"""
        from run import initialize_database
        import asyncio
        
        args = Mock()
        args.init_db = True
        args.env = 'dev'
        
        with patch('run.asyncio.run') as mock_run, \
             patch('run.DatabaseInitializer') as mock_db:
            
            mock_run.return_value = True
            
            initialize_database(args)
            
            # Should attempt to initialize
            assert mock_run.called
    
    def test_initialize_database_failure(self):
        """Test database initialization failure handling"""
        from run import initialize_database
        
        args = Mock()
        args.init_db = True
        args.env = 'dev'
        
        with patch('run.asyncio.run', side_effect=Exception("DB Error")):
            # Should not raise exception, just print warning
            try:
                initialize_database(args)
            except Exception:
                pytest.fail("initialize_database should handle exceptions gracefully")
    
    def test_get_server_config_default(self):
        """Test getting server configuration with defaults"""
        from run import get_server_config
        
        args = Mock()
        args.host = None
        args.port = None
        args.reload = False
        args.workers = 1
        args.log_level = None
        args.env = None
        
        settings = Mock()
        settings.host = "0.0.0.0"
        settings.port = 8001
        settings.debug = False
        settings.log_level = "INFO"
        
        with patch('run.get_settings', return_value=settings):
            config = get_server_config(args)
            
            assert config['host'] == "0.0.0.0"
            assert config['port'] == 8001
            assert config['reload'] is False
            assert config['workers'] == 1
    
    def test_get_server_config_with_args(self):
        """Test getting server configuration with arguments"""
        from run import get_server_config
        
        args = Mock()
        args.host = "127.0.0.1"
        args.port = 9000
        args.reload = True
        args.workers = 4
        args.log_level = "debug"
        args.env = None
        
        settings = Mock()
        settings.host = "0.0.0.0"
        settings.port = 8001
        settings.debug = False
        settings.log_level = "INFO"
        
        with patch('run.get_settings', return_value=settings):
            config = get_server_config(args)
            
            assert config['host'] == "127.0.0.1"
            assert config['port'] == 9000
            assert config['reload'] is True
            assert config['workers'] == 4
            assert config['log_level'] == "debug"
    
    def test_get_server_config_with_env(self):
        """Test getting server configuration with environment"""
        from run import get_server_config
        
        args = Mock()
        args.host = None
        args.port = None
        args.reload = False
        args.workers = 1
        args.log_level = None
        args.env = 'dev'
        
        settings = Mock()
        settings.host = "0.0.0.0"
        settings.port = 8001
        settings.debug = True
        settings.log_level = "DEBUG"
        
        with patch('run.get_settings', return_value=settings), \
             patch('run.reload_settings', return_value=settings):
            config = get_server_config(args)
            
            assert config['host'] == "0.0.0.0"
            assert config['port'] == 8001
    
    @patch('run.uvicorn.run')
    @patch('run.get_server_config')
    @patch('run.initialize_database')
    @patch('run.initialize_environment')
    @patch('run.parse_arguments')
    def test_main_success(
        self,
        mock_parse,
        mock_init_env,
        mock_init_db,
        mock_get_config,
        mock_uvicorn_run
    ):
        """Test main function success"""
        from run import main
        
        args = Mock()
        args.env = None
        args.init_db = False
        mock_parse.return_value = args
        
        mock_config = {
            'app': 'app.main:app',
            'host': '0.0.0.0',
            'port': 8001,
            'reload': False,
            'workers': 1,
            'log_level': 'info'
        }
        mock_get_config.return_value = mock_config
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_parse.assert_called_once()
            mock_init_env.assert_called_once()
            mock_get_config.assert_called_once()
            mock_uvicorn_run.assert_called_once_with(**mock_config)
    
    @patch('run.parse_arguments')
    def test_main_keyboard_interrupt(self, mock_parse):
        """Test main function with keyboard interrupt"""
        from run import main
        
        mock_parse.side_effect = KeyboardInterrupt()
        
        with patch('sys.exit') as mock_exit:
            result = main()
            
            assert result == 0
    
    @patch('run.parse_arguments')
    def test_main_exception(self, mock_parse):
        """Test main function with exception"""
        from run import main
        
        mock_parse.side_effect = Exception("Test error")
        
        with patch('sys.exit') as mock_exit:
            result = main()
            
            assert result == 1

