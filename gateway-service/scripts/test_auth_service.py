#!/usr/bin/env python3
"""
Test script for Auth Service
Tests health check and all auth routes
"""
import sys
import asyncio
import httpx
from typing import Dict, Tuple, List
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Auth Service Configuration
AUTH_SERVICE_BASE_URL = "http://127.0.0.1:8000"
HEALTH_CHECK_PATH = "/health"
AUTH_ROUTES = [
    "/auth/login",
    "/auth/logout",
    "/auth/register",
    "/auth/refresh",
]


class AuthServiceTester:
    """Test Auth Service endpoints"""
    
    def __init__(self, base_url: str = AUTH_SERVICE_BASE_URL):
        """
        Initialize tester
        
        Args:
            base_url: Base URL of auth service
        """
        self.base_url = base_url.rstrip("/")
        self.results: List[Tuple[str, bool, str]] = []
    
    async def test_health_check(self) -> Tuple[str, bool, str]:
        """
        Test health check endpoint
        
        Returns:
            Tuple of (endpoint, success, message)
        """
        endpoint = f"{self.base_url}{HEALTH_CHECK_PATH}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    service = data.get("service", "unknown")
                    version = data.get("version", "unknown")
                    
                    return (
                        HEALTH_CHECK_PATH,
                        True,
                        f"Status: {status}, Service: {service}, Version: {version}"
                    )
                else:
                    return (
                        HEALTH_CHECK_PATH,
                        False,
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
        except httpx.ConnectError:
            return (
                HEALTH_CHECK_PATH,
                False,
                f"Connection failed: Service not running at {self.base_url}"
            )
        except httpx.TimeoutException:
            return (
                HEALTH_CHECK_PATH,
                False,
                "Request timeout: Service not responding"
            )
        except Exception as e:
            return (
                HEALTH_CHECK_PATH,
                False,
                f"Error: {str(e)}"
            )
    
    async def test_auth_route(self, route: str) -> Tuple[str, bool, str]:
        """
        Test an auth route endpoint
        
        Args:
            route: Route path to test
            
        Returns:
            Tuple of (endpoint, success, message)
        """
        endpoint = f"{self.base_url}{route}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try GET first (some endpoints might support it)
                response = await client.get(endpoint)
                
                # If GET returns 405, try POST (most auth endpoints use POST)
                if response.status_code == 405:
                    # Try POST with empty body
                    response = await client.post(endpoint, json={})
                
                # Check if endpoint exists (not 404)
                if response.status_code == 404:
                    return (
                        route,
                        False,
                        f"Endpoint not found (404)"
                    )
                elif response.status_code in [200, 201, 400, 401, 422]:
                    # 200/201 = success, 400/401/422 = endpoint exists but validation failed (expected)
                    status_text = "exists"
                    if response.status_code == 200 or response.status_code == 201:
                        status_text = "working"
                    elif response.status_code == 401:
                        status_text = "requires authentication"
                    elif response.status_code == 422:
                        status_text = "validation error (expected)"
                    
                    return (
                        route,
                        True,
                        f"HTTP {response.status_code} - {status_text}"
                    )
                else:
                    return (
                        route,
                        False,
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
        except httpx.ConnectError:
            return (
                route,
                False,
                f"Connection failed: Service not running at {self.base_url}"
            )
        except httpx.TimeoutException:
            return (
                route,
                False,
                "Request timeout: Service not responding"
            )
        except Exception as e:
            return (
                route,
                False,
                f"Error: {str(e)}"
            )
    
    async def test_all(self) -> Dict[str, any]:
        """
        Test all endpoints
        
        Returns:
            Dictionary with test results
        """
        print("=" * 70)
        print("Auth Service Test")
        print("=" * 70)
        print()
        print(f"Service URL: {self.base_url}")
        print(f"Health Check: {HEALTH_CHECK_PATH}")
        print(f"Auth Routes: {len(AUTH_ROUTES)} routes")
        print()
        
        # Test health check
        print("🔍 Testing Health Check...")
        print("-" * 70)
        health_result = await self.test_health_check()
        self.results.append(health_result)
        self._print_result(*health_result)
        print()
        
        # Test auth routes
        print("🔍 Testing Auth Routes...")
        print("-" * 70)
        for route in AUTH_ROUTES:
            route_result = await self.test_auth_route(route)
            self.results.append(route_result)
            self._print_result(*route_result)
        print()
        
        # Summary
        print("=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print()
        
        if failed > 0:
            print("Failed Tests:")
            for endpoint, success, message in self.results:
                if not success:
                    print(f"  - {endpoint}: {message}")
            print()
        
        # Overall status
        all_passed = failed == 0
        if all_passed:
            print("✅ All tests passed! Auth Service is ready.")
        else:
            print("❌ Some tests failed. Please check the issues above.")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "all_passed": all_passed,
            "results": self.results
        }
    
    def _print_result(self, endpoint: str, success: bool, message: str) -> None:
        """
        Print test result
        
        Args:
            endpoint: Endpoint path
            success: Whether test passed
            message: Result message
        """
        status = "✅" if success else "❌"
        print(f"{status} {endpoint}: {message}")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Auth Service endpoints")
    parser.add_argument(
        "--url",
        type=str,
        default=AUTH_SERVICE_BASE_URL,
        help=f"Auth service base URL (default: {AUTH_SERVICE_BASE_URL})"
    )
    
    args = parser.parse_args()
    
    tester = AuthServiceTester(base_url=args.url)
    result = await tester.test_all()
    
    # Exit with error code if tests failed
    sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
