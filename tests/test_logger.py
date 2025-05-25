"""
Test suite for DataBridge logger utility.
Tests logger setup, configuration, and functionality.
"""
import unittest
import logging
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.databridge_logger import setup_databridge_logger


class TestLogger(unittest.TestCase):
    """Test DataBridge logger functionality."""
    
    def test_setup_databridge_logger_basic(self):
        """Test basic logger setup without config."""
        logger = setup_databridge_logger()
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'databridge')
        self.assertEqual(logger.level, logging.INFO)
    
    def test_setup_databridge_logger_with_config(self):
        """Test logger setup with configuration."""
        config = {
            'logging': {
                'level': 'DEBUG',
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'file': 'test.log'
            }
        }
        
        logger = setup_databridge_logger(config)
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.DEBUG)
    
    def test_logger_file_output(self):
        """Test logger writes to file correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            config = {
                'logging': {
                    'file': log_file,
                    'level': 'INFO'
                }
            }
            
            logger = setup_databridge_logger(config)
            test_message = "Test log message"
            logger.info(test_message)
              # Force flush and close handlers
            for handler in logger.handlers[:]:
                if hasattr(handler, 'flush'):
                    handler.flush()
                if hasattr(handler, 'close'):
                    handler.close()
                logger.removeHandler(handler)
            
            # Check if message was written to file
            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn(test_message, content)
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_logger_levels(self):
        """Test different logging levels."""
        logger = setup_databridge_logger()
        
        # Test that logger accepts different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_logger_with_none_config(self):
        """Test logger setup with None config."""
        logger = setup_databridge_logger(None)
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'databridge')
    
    def test_logger_prevents_duplicate_handlers(self):
        """Test that multiple calls don't create duplicate handlers."""
        logger1 = setup_databridge_logger()
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_databridge_logger()
        final_handler_count = len(logger2.handlers)
        
        # Should not have more handlers after second call
        self.assertEqual(initial_handler_count, final_handler_count)


if __name__ == '__main__':
    unittest.main()
