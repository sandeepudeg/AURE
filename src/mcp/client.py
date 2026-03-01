"""
MCP Client Implementation
Handles communication with MCP servers for external tool access
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for standardized external service access
    
    Features:
    - Tool registry management
    - Permission verification
    - Retry logic with exponential backoff
    - Fallback to cached data
    - Comprehensive logging
    """
    
    def __init__(
        self,
        tool_registry_path: str,
        servers: Dict[str, str],
        cache_ttl: int = 300,  # 5 minutes
        cache_maxsize: int = 100
    ):
        """
        Initialize MCP Client
        
        Args:
            tool_registry_path: Path to tool registry JSON file
            servers: Dictionary of server_name -> server_url
            cache_ttl: Cache time-to-live in seconds
            cache_maxsize: Maximum cache size
        """
        self.servers = servers
        self.tool_registry = self._load_tool_registry(tool_registry_path)
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)
        
        logger.info(f"MCP Client initialized with {len(self.tool_registry)} tools")
        logger.info(f"Connected servers: {list(servers.keys())}")
    
    def _load_tool_registry(self, registry_path: str) -> Dict[str, Dict[str, Any]]:
        """Load tool registry from JSON file"""
        try:
            path = Path(registry_path)
            if not path.exists():
                logger.error(f"Tool registry not found: {registry_path}")
                return {}
            
            with open(path, 'r') as f:
                registry = json.load(f)
            
            logger.info(f"Loaded {len(registry)} tools from registry")
            return registry
        
        except Exception as e:
            logger.error(f"Failed to load tool registry: {e}")
            return {}
    
    def _check_permission(self, tool_id: str, agent_role: str) -> bool:
        """
        Check if agent has permission to use tool
        
        Args:
            tool_id: Tool identifier
            agent_role: Agent role (e.g., 'Agri-Expert', 'Supervisor')
        
        Returns:
            True if permitted, False otherwise
        """
        if tool_id not in self.tool_registry:
            logger.warning(f"Tool not found in registry: {tool_id}")
            return False
        
        tool_config = self.tool_registry[tool_id]
        permissions = tool_config.get('permissions', [])
        
        # Check if agent role is in permissions list
        has_permission = agent_role in permissions
        
        if not has_permission:
            logger.warning(
                f"Permission denied: {agent_role} cannot use {tool_id}. "
                f"Allowed roles: {permissions}"
            )
        
        return has_permission
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def _call_mcp_server(
        self,
        server_url: str,
        tool_id: str,
        params: Dict[str, Any],
        timeout_ms: int
    ) -> Dict[str, Any]:
        """
        Call MCP server with retry logic
        
        Args:
            server_url: MCP server URL
            tool_id: Tool ID to call
            params: Tool parameters
            timeout_ms: Request timeout in milliseconds
        
        Returns:
            Tool response
        
        Raises:
            requests.RequestException: If all retries fail
        """
        timeout_sec = timeout_ms / 1000.0
        
        # Map tool_id to endpoint
        endpoint = f"{server_url}/{tool_id}"
        
        logger.debug(f"Calling MCP server: {endpoint}")
        
        response = requests.post(
            endpoint,
            json=params,
            timeout=timeout_sec
        )
        
        response.raise_for_status()
        return response.json()
    
    def call_tool(
        self,
        tool_id: str,
        agent_role: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call MCP tool with permission check, retry, and caching
        
        Args:
            tool_id: Tool identifier from registry
            agent_role: Agent role making the request
            params: Tool parameters
        
        Returns:
            Tool response or cached data
        
        Raises:
            PermissionError: If agent doesn't have permission
            ValueError: If tool not found in registry
            RuntimeError: If tool call fails after retries
        """
        # Validate tool exists
        if tool_id not in self.tool_registry:
            error_msg = f"Tool not found in registry: {tool_id}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check permissions
        if not self._check_permission(tool_id, agent_role):
            error_msg = f"Permission denied: {agent_role} cannot use {tool_id}"
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        # Get tool configuration
        tool_config = self.tool_registry[tool_id]
        server_name = tool_config['server_name']
        timeout_ms = tool_config.get('timeout_ms', 5000)
        
        # Check if server is configured
        if server_name not in self.servers:
            error_msg = f"Server not configured: {server_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        server_url = self.servers[server_name]
        
        # Create cache key
        cache_key = f"{tool_id}:{json.dumps(params, sort_keys=True)}"
        
        # Try to call MCP server
        try:
            start_time = time.time()
            
            result = self._call_mcp_server(
                server_url=server_url,
                tool_id=tool_id,
                params=params,
                timeout_ms=timeout_ms
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Cache successful result
            self.cache[cache_key] = result
            
            # Log successful call
            logger.info(
                f"MCP tool call successful: {tool_id} "
                f"(agent={agent_role}, elapsed={elapsed_ms:.0f}ms)"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"MCP tool call failed: {tool_id} - {str(e)}")
            
            # Try to return cached data as fallback
            if cache_key in self.cache:
                logger.warning(f"Returning cached data for {tool_id}")
                cached_result = self.cache[cache_key]
                cached_result['_cached'] = True
                return cached_result
            
            # No cache available, raise error
            error_msg = f"MCP tool call failed and no cache available: {tool_id}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def get_available_tools(self, agent_role: Optional[str] = None) -> List[str]:
        """
        Get list of available tools, optionally filtered by agent role
        
        Args:
            agent_role: Optional agent role to filter by permissions
        
        Returns:
            List of tool IDs
        """
        if agent_role is None:
            return list(self.tool_registry.keys())
        
        return [
            tool_id
            for tool_id, config in self.tool_registry.items()
            if agent_role in config.get('permissions', [])
        ]
    
    def get_tool_metadata(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific tool
        
        Args:
            tool_id: Tool identifier
        
        Returns:
            Tool metadata or None if not found
        """
        return self.tool_registry.get(tool_id)
