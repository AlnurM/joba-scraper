#!/usr/bin/env python3
"""
Script to create __init__.py files in all directories.
"""

import os
import sys
import argparse

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_init_files(force=False):
    """Create __init__.py files in all directories."""
    # Directories to create __init__.py files in
    directories = [
        'src',
        'src/services',
        'src/models',
        'src/utils',
        'src/config',
        'tests',
    ]
    
    created_files = []
    
    for directory in directories:
        dir_path = os.path.join(PROJECT_ROOT, directory)
        
        if not os.path.exists(dir_path):
            print(f"Directory does not exist: {directory}")
            continue
            
        init_file = os.path.join(dir_path, '__init__.py')
        
        if os.path.exists(init_file) and not force:
            print(f"__init__.py file already exists in {directory}")
            continue
            
        try:
            with open(init_file, 'w') as f:
                f.write('"""Package initialization."""\n')
            
            created_files.append(init_file)
            print(f"Created __init__.py file in {directory}")
        except Exception as e:
            print(f"Error creating __init__.py file in {directory}: {str(e)}")
            return False
    
    if created_files:
        print(f"Created {len(created_files)} __init__.py files")
    else:
        print("All __init__.py files already exist")
    
    return True


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create __init__.py files in all directories')
    parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing __init__.py files')
    args = parser.parse_args()
    
    # Create the __init__.py files
    success = create_init_files(args.force)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)