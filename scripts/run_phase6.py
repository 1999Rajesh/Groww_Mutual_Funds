"""
Phase 6 Test Runner
Comprehensive testing suite for all phases
"""
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_tests():
    """Run comprehensive test suite"""
    print("\n" + "="*80)
    print("PHASE 6: COMPREHENSIVE TESTING")
    print("="*80)
    print(f"\nTest Execution Started: {datetime.now().isoformat()}")
    print("="*80)
    
    # Run main test suite
    print("\nRunning Unit Tests...")
    print("-"*80)
    
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_comprehensive", "-v"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # Generate coverage report (if coverage installed)
    print("\nGenerating Coverage Report...")
    print("-"*80)
    
    try:
        coverage_result = subprocess.run(
            [sys.executable, "-m", "coverage", "run", "-m", "unittest", "tests.test_comprehensive"],
            capture_output=True,
            text=True
        )
        
        html_result = subprocess.run(
            [sys.executable, "-m", "coverage", "html", "-d", "htmlcov"],
            capture_output=True,
            text=True
        )
        
        print("Coverage HTML report generated at: htmlcov/index.html")
        
        # Print coverage summary
        report_result = subprocess.run(
            [sys.executable, "-m", "coverage", "report"],
            capture_output=True,
            text=True
        )
        print(report_result.stdout)
        
    except Exception as e:
        print(f"Coverage not available: {e}")
        print("Install with: pip install coverage")
    
    # Run performance benchmarks
    print("\nRunning Performance Benchmarks...")
    print("-"*80)
    
    try:
        from tests.test_performance import run_benchmarks
        benchmark_results = run_benchmarks()
        
        print("\nPerformance Benchmark Results:")
        print("-"*80)
        for metric, value in benchmark_results.items():
            print(f"{metric}: {value}")
        
        # Save benchmark results
        benchmark_file = Path("tests/benchmark_results.json")
        benchmark_file.parent.mkdir(exist_ok=True)
        
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        
        print(f"\nBenchmark results saved to: {benchmark_file}")
        
    except ImportError:
        print("Performance benchmarks not available yet")
    
    # Summary
    print("\n" + "="*80)
    print("TEST EXECUTION COMPLETE")
    print("="*80)
    print(f"Completed at: {datetime.now().isoformat()}")
    print("="*80)
    
    return result.returncode == 0


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("Phase 6: Comprehensive Testing Suite")
    print("="*80)
    print("\nThis will:")
    print("1. Run unit tests for all phases (1-5)")
    print("2. Run integration tests (Phase 6)")
    print("3. Generate coverage reports")
    print("4. Run performance benchmarks")
    print("="*80)
    
    input("\nPress Enter to start testing...")
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("1. Review coverage report: htmlcov/index.html")
        print("2. Check benchmark results: tests/benchmark_results.json")
        print("3. Proceed to Phase 7 (CLI Interface)")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        print("Fix failing tests before proceeding to next phase.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
