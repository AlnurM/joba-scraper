#!/usr/bin/env python3
"""
Script to create a .env file from .env.example.
"""

import os
import sys
import argparse

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_env(force=False):
    """Create a .env file from .env.example."""
    env_file = os.path.join(PROJECT_ROOT, '.env')
    env_example_file = os.path.join(PROJECT_ROOT, '.env.example')
    
    # Check if .env file already exists
    if os.path.exists(env_file) and not force:
        print(f".env file already exists at {env_file}")
        print("Use --force to overwrite it")
        return False
    
    # Check if .env.example file exists
    if not os.path.exists(env_example_file):
        print(f".env.example file not found at {env_example_file}")
        return False
    
    try:
        # Read the .env.example file
        with open(env_example_file, 'r') as f:
            env_example_content = f.readlines()
        
        # Create the .env file
        with open(env_file, 'w') as f:
            for line in env_example_content:
                f.write(line)
        
        print(f".env file created at {env_file}")
        print("Please edit it with your configuration")
        return True
        
    except Exception as e:
        print(f"Error creating .env file: {str(e)}")
        return False


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create a .env file from .env.example')
    parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing .env file')
    args = parser.parse_args()
    
    # Create the .env file
    success = create_env(args.force)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)