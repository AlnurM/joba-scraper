#!/usr/bin/env python3
"""
Script to set up the project directories.
"""

import os
import sys
import argparse

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_project():
    """Create the necessary directories for the project."""
    directories = [
        'logs',
        'data',
        'data/mongodb',
        'data/redis',
    ]
    
    created_dirs = []
    
    for directory in directories:
        dir_path = os.path.join(PROJECT_ROOT, directory)
        
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                created_dirs.append(directory)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Error creating directory {directory}: {str(e)}")
                return False
        else:
            print(f"Directory already exists: {directory}")
    
    if created_dirs:
        print(f"Created {len(created_dirs)} directories")
    else:
        print("All directories already exist")
    
    # Create .env file if it doesn't exist
    env_file = os.path.join(PROJECT_ROOT, '.env')
    env_example_file = os.path.join(PROJECT_ROOT, '.env.example')
    
    if not os.path.exists(env_file) and os.path.exists(env_example_file):
        try:
            # Run the create_env.py script
            create_env_script = os.path.join(PROJECT_ROOT, 'scripts', 'create_env.py')
            if os.path.exists(create_env_script):
                print("Creating .env file from .env.example")
                os.system(f"python {create_env_script}")
        except Exception as e:
            print(f"Error creating .env file: {str(e)}")
    
    print("Project setup complete")
    return True


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Set up the project directories')
    args = parser.parse_args()
    
    # Set up the project
    success = setup_project()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)