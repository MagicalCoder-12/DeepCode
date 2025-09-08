"""
Direct HTTP Serper Search Service

This module provides direct HTTP access to Serper API without MCP dependencies.
Replaces the MCP-based serper search server with a standalone service class.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


class SerperSearchService:
    """
    Direct HTTP service for Serper API web search functionality.
    
    This class provides the same interface as the previous MCP server
    but uses direct HTTP requests instead of Model Context Protocol.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Serper search service.
        
        Args:
            api_key: Serper API key. If not provided, will use SERPER_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("SERPER_API_KEY", "")
        self.endpoint = "https://google.serper.dev/search"
        
        if not self.api_key:
            raise ValueError(
                "Serper API key is required. Set SERPER_API_KEY environment variable or pass api_key parameter."
            )
    
    async def search(self, query: str, num: int = 10) -> str:
        """
        Search with Serper Web Search and get enhanced search details from billions of web documents.
        
        Args:
            query: Search query (required)
            num: Number of results (default 10)
            
        Returns:
            str: Formatted search results or error message
        """
        if not query or not query.strip():
            return "Error: Search query cannot be empty."
            
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "q": query.strip(),
            "num": num
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint, 
                    headers=headers, 
                    json=payload, 
                    timeout=10.0
                )
                response.raise_for_status()
                resp = response.json()
                
                results = []
                if "organic" in resp and resp["organic"]:
                    for result in resp["organic"]:
                        formatted_result = (
                            f"Title: {result.get('title', 'No title')}\n"
                            f"URL: {result.get('link', 'No URL')}\n"
                            f"Description: {result.get('snippet', 'No description')}\n"
                            f"Site name: {result.get('domain', 'Unknown domain')}"
                        )
                        results.append(formatted_result)
                
                if not results:
                    return "No results found for the given query."
                
                return "\n\n".join(results)
                
        except httpx.HTTPStatusError as e:
            error_msg = f"Serper API HTTP error: {e.response.status_code}"
            if e.response.text:
                error_msg += f" - {e.response.text}"
            return f"Error: {error_msg}"
            
        except httpx.RequestError as e:
            return f"Error: Network error communicating with Serper API - {str(e)}"
            
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON response from Serper API - {str(e)}"
            
        except Exception as e:
            return f"Error: Unexpected error during search - {str(e)}"
    
    def search_sync(self, query: str, num: int = 10) -> str:
        """
        Synchronous wrapper for the async search method.
        
        Args:
            query: Search query (required)
            num: Number of results (default 10)
            
        Returns:
            str: Formatted search results or error message
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.search(query, num))
    
    @classmethod
    def create_from_config(cls, config_path: str = "mcp_agent.config.yaml") -> 'SerperSearchService':
        """
        Create SerperSearchService instance from configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            SerperSearchService: Configured service instance
        """
        try:
            import yaml
            
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                
                # Try to get API key from MCP server config (for backward compatibility)
                mcp_config = config.get("mcp", {})
                servers = mcp_config.get("servers", {})
                serper_config = servers.get("serper", {})
                serper_env = serper_config.get("env", {})
                api_key = serper_env.get("SERPER_API_KEY")
                
                if api_key:
                    return cls(api_key=api_key)
        
        except Exception as e:
            print(f"Warning: Could not read config file {config_path}: {e}")
        
        # Fall back to environment variable
        return cls()


# Global service instance for backward compatibility
_default_service: Optional[SerperSearchService] = None


def get_default_search_service() -> SerperSearchService:
    """
    Get or create the default Serper search service instance.
    
    Returns:
        SerperSearchService: The default service instance
    """
    global _default_service
    
    if _default_service is None:
        _default_service = SerperSearchService.create_from_config()
    
    return _default_service


async def serper_web_search(query: str, num: int = 10) -> str:
    """
    Backward compatibility function that mimics the original MCP server interface.
    
    Args:
        query: Search query (required)
        num: Number of results (default 10)
        
    Returns:
        str: Formatted search results or error message
    """
    service = get_default_search_service()
    return await service.search(query, num)


# Convenience functions for common use cases
async def search_papers(topic: str, num: int = 5) -> str:
    """
    Search for research papers on a specific topic.
    
    Args:
        topic: Research topic
        num: Number of results
        
    Returns:
        str: Search results
    """
    query = f"{topic} research paper filetype:pdf site:arxiv.org OR site:scholar.google.com"
    return await serper_web_search(query, num)


async def search_code_repositories(technology: str, num: int = 5) -> str:
    """
    Search for code repositories related to a specific technology.
    
    Args:
        technology: Technology or framework name
        num: Number of results
        
    Returns:
        str: Search results
    """
    query = f"{technology} implementation site:github.com"
    return await serper_web_search(query, num)


if __name__ == "__main__":
    # Test the service
    async def test_service():
        try:
            service = SerperSearchService()
            result = await service.search("machine learning papers", 3)
            print("Search Result:")
            print(result)
        except Exception as e:
            print(f"Test failed: {e}")
    
    asyncio.run(test_service())