#!/usr/bin/env python3
"""
Test runner script for Spotify Pipeline
Run this to execute all tests with coverage reporting
"""

import subprocess
import sys
import os

def run_tests():
    """Run the complete test suite"""
    print("🎵 Running Spotify Pipeline Test Suite 🎵")
    print("=" * 50)
    
    # Change to project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Run tests with coverage
    cmd = [
        "pytest", 
        "tests/",
        "-v",
        "--tb=short",
        "--strict-markers"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return False

def run_tests_with_coverage():
    """Run tests with coverage reporting"""
    print("🎵 Running Spotify Pipeline Test Suite with Coverage 🎵")
    print("=" * 60)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    cmd = [
        "pytest",
        "tests/",
        "--cov=scripts",
        "--cov=app", 
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report saved to htmlcov/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest-cov not found. Install with: pip install pytest pytest-cov")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        success = run_tests_with_coverage()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)