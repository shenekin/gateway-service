"""
External services verification script
This script checks if all required external services are available and configured
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.settings import get_settings


class ServiceVerifier:
    """Verify external services availability"""
    
    def __init__(self):
        """Initialize service verifier"""
        self.settings = get_settings()
        self.results: List[Tuple[str, bool, str]] = []
    
    async def check_redis(self) -> Tuple[str, bool, str]:
        """
        Check Redis connection
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 25-40: Redis connection check
        # Reason: Redis is required for rate limiting functionality
        try:
            import redis.asyncio as aioredis
            
            client = await aioredis.from_url(
                f"redis://{self.settings.redis_host}:{self.settings.redis_port}",
                password=self.settings.redis_password,
                db=self.settings.redis_db,
                socket_connect_timeout=2
            )
            await client.ping()
            await client.aclose()
            return ("Redis", True, f"Connected to {self.settings.redis_host}:{self.settings.redis_port}")
        except Exception as e:
            return ("Redis", False, f"Connection failed: {str(e)}")
    
    async def check_mysql(self) -> Tuple[str, bool, str]:
        """
        Check MySQL connection
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 42-60: MySQL connection check
        # Reason: MySQL is required for database operations and API key storage
        try:
            import asyncmy
            
            conn = await asyncmy.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                db=self.settings.mysql_database
            )
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1")
            await cursor.fetchone()
            await cursor.close()
            conn.close()
            return ("MySQL", True, f"Connected to {self.settings.mysql_host}:{self.settings.mysql_port}")
        except Exception as e:
            return ("MySQL", False, f"Connection failed: {str(e)}")
    
    async def check_database_initialized(self) -> Tuple[str, bool, str]:
        """
        Check if database is initialized with required tables
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 62-85: Database initialization check
        # Reason: Database must have required tables for API keys, routes, etc.
        try:
            import asyncmy
            
            conn = await asyncmy.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                db=self.settings.mysql_database
            )
            cursor = await conn.cursor()
            
            # Check if required tables exist
            await cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = %s AND table_name IN 
                ('api_keys', 'routes', 'service_instances', 'rate_limit_records', 'circuit_breaker_states', 'audit_logs')
            """, (self.settings.mysql_database,))
            
            result = await cursor.fetchone()
            table_count = result[0] if result else 0
            
            await cursor.close()
            conn.close()
            
            if table_count >= 6:
                return ("Database Schema", True, f"All {table_count} required tables exist")
            else:
                return ("Database Schema", False, f"Only {table_count}/6 tables found. Run init_database.py")
        except Exception as e:
            return ("Database Schema", False, f"Check failed: {str(e)}")
    
    async def check_service_discovery(self) -> Tuple[str, bool, str]:
        """
        Check service discovery availability
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 87-120: Service discovery check
        # Reason: Service discovery is needed to find backend service instances
        discovery_type = self.settings.service_discovery_type
        
        if discovery_type == "static":
            # Check if services.yaml exists
            services_file = Path(__file__).parent.parent / "config" / "services.yaml"
            if services_file.exists():
                return ("Service Discovery (Static)", True, "Using static configuration from services.yaml")
            else:
                return ("Service Discovery (Static)", False, "services.yaml file not found")
        
        elif discovery_type == "nacos":
            try:
                import httpx
                addresses = self.settings.nacos_server_addresses.split(",")
                for address in addresses:
                    host, port = address.strip().split(":")
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        response = await client.get(f"http://{host}:{port}/nacos/v1/console/health")
                        if response.status_code == 200:
                            return ("Nacos", True, f"Connected to {address}")
                return ("Nacos", False, f"Could not connect to any Nacos server: {addresses}")
            except Exception as e:
                return ("Nacos", False, f"Connection failed: {str(e)}")
        
        elif discovery_type == "consul":
            try:
                import httpx
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(
                        f"http://{self.settings.consul_host}:{self.settings.consul_port}/v1/status/leader"
                    )
                    if response.status_code == 200:
                        return ("Consul", True, f"Connected to {self.settings.consul_host}:{self.settings.consul_port}")
                    else:
                        return ("Consul", False, f"Health check failed: {response.status_code}")
            except Exception as e:
                return ("Consul", False, f"Connection failed: {str(e)}")
        
        elif discovery_type == "etcd":
            try:
                import etcd3
                client = etcd3.client(host=self.settings.etcd_host, port=self.settings.etcd_port)
                client.status()
                return ("etcd", True, f"Connected to {self.settings.etcd_host}:{self.settings.etcd_port}")
            except Exception as e:
                return ("etcd", False, f"Connection failed: {str(e)}")
        
        return ("Service Discovery", False, f"Unknown discovery type: {discovery_type}")
    
    async def check_jaeger(self) -> Tuple[str, bool, str]:
        """
        Check Jaeger availability (optional)
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 122-135: Jaeger availability check
        # Reason: Jaeger is optional but recommended for distributed tracing
        if not self.settings.tracing_enabled:
            return ("Jaeger", True, "Tracing disabled, not required")
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"http://{self.settings.jaeger_agent_host}:16686")
                if response.status_code == 200:
                    return ("Jaeger", True, f"Connected to {self.settings.jaeger_agent_host}:16686")
                else:
                    return ("Jaeger", False, f"Health check failed: {response.status_code}")
        except Exception as e:
            return ("Jaeger", False, f"Connection failed: {str(e)} (optional service)")
    
    def check_log_directory(self) -> Tuple[str, bool, str]:
        """
        Check if log directory is writable
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 137-150: Log directory check
        # Reason: Log directory must be writable for logging to work
        try:
            log_dir = Path(self.settings.log_directory)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write
            test_file = log_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
            
            return ("Log Directory", True, f"Directory writable: {log_dir}")
        except Exception as e:
            return ("Log Directory", False, f"Not writable: {str(e)}")
    
    async def check_backend_services(self) -> Tuple[str, bool, str]:
        """
        Check backend services availability
        
        Returns:
            Tuple of (service_name, is_available, message)
        """
        # Line 152-180: Backend services check
        # Reason: Backend services must be running for gateway to route requests
        try:
            from app.core.discovery import create_service_discovery
            
            service_discovery = create_service_discovery()
            
            # Check project-service
            instances = await service_discovery.get_instances("project-service")
            if instances:
                healthy_count = sum(1 for inst in instances if inst.healthy)
                return (
                    "Backend Services",
                    healthy_count > 0,
                    f"Found {len(instances)} instances, {healthy_count} healthy"
                )
            else:
                return ("Backend Services", False, "No backend service instances found")
        except Exception as e:
            return ("Backend Services", False, f"Check failed: {str(e)}")
    
    async def verify_all(self) -> Dict[str, any]:
        """
        Verify all external services
        
        Returns:
            Dictionary with verification results
        """
        # Line 182-205: Comprehensive service verification
        # Reason: Check all required and optional services before starting gateway
        print("=" * 60)
        print("External Services Verification")
        print("=" * 60)
        
        # Required services
        print("\n[REQUIRED SERVICES]")
        redis_result = await self.check_redis()
        self.results.append(redis_result)
        self._print_result(*redis_result)
        
        mysql_result = await self.check_mysql()
        self.results.append(mysql_result)
        self._print_result(*mysql_result)
        
        db_init_result = await self.check_database_initialized()
        self.results.append(db_init_result)
        self._print_result(*db_init_result)
        
        log_dir_result = self.check_log_directory()
        self.results.append(log_dir_result)
        self._print_result(*log_dir_result)
        
        # Optional services
        print("\n[OPTIONAL SERVICES]")
        discovery_result = await self.check_service_discovery()
        self.results.append(discovery_result)
        self._print_result(*discovery_result)
        
        jaeger_result = await self.check_jaeger()
        self.results.append(jaeger_result)
        self._print_result(*jaeger_result)
        
        backend_result = await self.check_backend_services()
        self.results.append(backend_result)
        self._print_result(*backend_result)
        
        # Summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        required_passed = all(
            result[1] for result in self.results[:4]  # First 4 are required
        )
        
        if required_passed:
            print("✅ All required services are available")
            print("✅ Gateway service can be started")
        else:
            print("❌ Some required services are not available")
            print("❌ Please fix the issues above before starting gateway")
        
        return {
            "required_passed": required_passed,
            "results": self.results,
            "can_start": required_passed
        }
    
    def _print_result(self, name: str, passed: bool, message: str) -> None:
        """
        Print verification result
        
        Args:
            name: Service name
            passed: Whether check passed
            message: Result message
        """
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")


async def main():
    """Main function"""
    verifier = ServiceVerifier()
    result = await verifier.verify_all()
    
    # Exit with error code if required services failed
    if not result["can_start"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

