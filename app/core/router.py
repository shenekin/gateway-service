"""
Route matching and configuration management
"""

import yaml
from typing import List, Optional, Dict
from pathlib import Path
from app.models.route import Route, RouteConfig
from app.settings import get_settings


class Router:
    """Route matching and management service"""
    
    def __init__(self, routes_file: Optional[str] = None):
        """
        Initialize router with route configuration
        
        Args:
            routes_file: Path to routes configuration file
        """
        self.settings = get_settings()
        self.routes: List[Route] = []
        self.routes_file = routes_file or "config/routes.yaml"
        self._load_routes()
    
    def _load_routes(self) -> None:
        """Load routes from configuration file"""
        try:
            routes_path = Path(self.routes_file)
            if not routes_path.exists():
                routes_path = Path(__file__).parent.parent.parent / self.routes_file
            
            with open(routes_path, "r") as f:
                config = yaml.safe_load(f)
            
            routes_data = config.get("routes", [])
            for route_data in routes_data:
                route_config = RouteConfig(**route_data)
                route = Route(
                    config=route_config,
                    pattern=route_config.path,
                    priority=self._calculate_priority(route_config.path)
                )
                self.routes.append(route)
            
            # Sort by priority (higher priority first)
            self.routes.sort(key=lambda r: r.priority, reverse=True)
        except Exception as e:
            raise RuntimeError(f"Failed to load routes: {e}")
    
    def _calculate_priority(self, path: str) -> int:
        """
        Calculate route priority based on path specificity
        
        Args:
            path: Route path pattern
            
        Returns:
            Priority value (higher = more specific)
        """
        priority = 0
        
        # Exact matches have highest priority
        if not path.endswith(("/*", "/**")):
            priority += 1000
        
        # Count path segments
        segments = path.split("/")
        priority += len(segments) * 10
        
        # Paths with parameters have lower priority
        if "{" in path:
            priority -= 50
        
        return priority
    
    def find_route(self, path: str, method: str) -> Optional[Route]:
        """
        Find matching route for given path and method
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Matching route or None
        """
        for route in self.routes:
            if route.matches(path, method):
                return route
        return None
    
    def get_all_routes(self) -> List[Route]:
        """
        Get all configured routes
        
        Returns:
            List of all routes
        """
        return self.routes
    
    def reload_routes(self) -> None:
        """Reload routes from configuration file"""
        self.routes.clear()
        self._load_routes()

