#!/usr/bin/env python3
"""
Script to run the application in production mode.
"""

import sys
import os
import argparse
import signal
import time
import subprocess
import atexit

# Add the parent directory to the path so we can import the application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_config import setup_logging
from loguru import logger


def run_prod(daemon=False):
    """Run the application in production mode."""
    # Setup logging
    setup_logging()
    
    logger.info("Starting Job Scraper in production mode")
    
    if daemon:
        # Run as a daemon process
        logger.info("Running as a daemon process")
        
        # Create a subprocess
        process = subprocess.Popen(
            [sys.executable, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'main.py')],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            start_new_session=True
        )
        
        # Register a function to terminate the process on exit
        def cleanup():
            if process.poll() is None:
                logger.info("Terminating daemon process")
                process.terminate()
                process.wait()
        
        atexit.register(cleanup)
        
        # Write the PID to a file
        pid_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'joba-scraper.pid')
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        logger.info(f"Daemon process started with PID {process.pid}")
        logger.info(f"PID file written to {pid_file}")
        
        # Exit the parent process
        return 0
    else:
        # Run in the foreground
        logger.info("Running in the foreground")
        
        # Import the main module
        from src.main import main
        
        # Run the main function
        return main()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the application in production mode')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as a daemon process')
    args = parser.parse_args()
    
    # Run the application
    sys.exit(run_prod(args.daemon))