#!/usr/bin/env python3
"""
Run all configuration-related tests
Tests settings, environment loading, cluster configuration, etc.
"""
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests(test_files, description):
    """Run a list of test files"""
    print("=" * 70)
    print(f"Running {description}")
    print("=" * 70)
    print()
    
    results = []
    for test_file in test_files:
        test_path = project_root / "tests" / test_file
        if not test_path.exists():
            print(f"⚠️  Test file not found: {test_file}")
            results.append((test_file, False, "File not found"))
            continue
        
        print(f"Running: {test_file}")
        print("-" * 70)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
                results.append((test_file, True, "Passed"))
            else:
                print(f"❌ {test_file} - FAILED")
                print(result.stdout)
                print(result.stderr)
                results.append((test_file, False, "Failed"))
        except Exception as e:
            print(f"❌ {test_file} - ERROR: {e}")
            results.append((test_file, False, str(e)))
        
        print()
    
    return results

def main():
    """Main function to run all configuration tests"""
    print("=" * 70)
    print("Configuration Tests Runner")
    print("=" * 70)
    print()
    print("This script runs all configuration-related tests:")
    print("  - Settings module tests")
    print("  - Environment loader tests")
    print("  - Environment switching tests")
    print("  - Cluster configuration tests")
    print("  - Circular import fix tests")
    print("  - Run script configuration tests")
    print()
    
    # Define test categories
    test_categories = {
        "Settings Tests": [
            "test_settings.py",
        ],
        "Environment Loader Tests": [
            "test_env_loader.py",
            "test_env_auto_create.py",
        ],
        "Environment Switching Tests": [
            "test_settings_env_switching.py",
        ],
        "Cluster Configuration Tests": [
            "test_settings_cluster.py",
        ],
        "Import and Integration Tests": [
            "test_circular_import_fix.py",
            "test_run.py",
        ],
    }
    
    all_results = []
    
    # Run each category
    for category, test_files in test_categories.items():
        results = run_tests(test_files, category)
        all_results.extend(results)
        print()
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, success, _ in all_results if success)
    failed = sum(1 for _, success, _ in all_results if not success)
    total = len(all_results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()
    
    if failed > 0:
        print("Failed Tests:")
        for test_file, success, message in all_results:
            if not success:
                print(f"  - {test_file}: {message}")
        print()
    
    # Exit with appropriate code
    if failed == 0:
        print("✅ All configuration tests passed!")
        sys.exit(0)
    else:
        print(f"❌ {failed} test file(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
