#!/usr/bin/env python3
"""
Test runner for Google ADK with Vertex Search grounding.

This script runs the test suite and provides a summary of results.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests for Google ADK with Vertex Search grounding")
    print("=" * 60)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"], check=True)
    
    # Run tests
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ Tests directory not found")
        return False
    
    print("🔍 Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--color=yes"
    ])
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


def run_examples():
    """Run example scripts to verify functionality."""
    print("\n📚 Running examples...")
    print("=" * 30)
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("❌ Examples directory not found")
        return False
    
    example_files = [
        "basic_usage.py",
        "conversation_example.py", 
        "custom_search.py"
    ]
    
    success_count = 0
    
    for example_file in example_files:
        example_path = examples_dir / example_file
        if example_path.exists():
            print(f"🔄 Running {example_file}...")
            try:
                # Run with timeout to avoid hanging
                result = subprocess.run([
                    sys.executable, str(example_path)
                ], timeout=30, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {example_file} completed successfully")
                    success_count += 1
                else:
                    print(f"❌ {example_file} failed")
                    print(f"Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {example_file} timed out")
            except Exception as e:
                print(f"❌ {example_file} failed: {e}")
        else:
            print(f"⚠️  {example_file} not found")
    
    print(f"\n📊 Examples completed: {success_count}/{len(example_files)}")
    return success_count == len(example_files)


def check_imports():
    """Check if all modules can be imported."""
    print("\n📦 Checking imports...")
    print("=" * 20)
    
    modules = [
        "agent",
        "config", 
        "cli"
    ]
    
    success_count = 0
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imports successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
    
    print(f"\n📊 Imports successful: {success_count}/{len(modules)}")
    return success_count == len(modules)


def main():
    """Main test runner function."""
    print("🚀 Google ADK Test Suite")
    print("=" * 40)
    
    # Check imports
    imports_ok = check_imports()
    
    # Run tests
    tests_ok = run_tests()
    
    # Run examples (optional, may require configuration)
    examples_ok = run_examples()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 20)
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"Unit Tests: {'✅' if tests_ok else '❌'}")
    print(f"Examples: {'✅' if examples_ok else '⚠️'}")
    
    if imports_ok and tests_ok:
        print("\n🎉 Core functionality is working!")
        if not examples_ok:
            print("⚠️  Examples may require proper configuration")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 