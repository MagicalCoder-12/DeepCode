"""
MCP Tool Definitions Configuration Module

Separate tool definitions from main program logic, providing standardized tool definition format

Supported Tool Types:
- File Operations
- Code Execution
- Search Tools
- Project Structure Tools
"""

from typing import Dict, List, Any


class MCPToolDefinitions:
    """MCP Tool Definitions Manager"""

    @staticmethod
    def get_code_implementation_tools() -> List[Dict[str, Any]]:
        """
        Get tool definitions for code implementation
        """
        return [
            MCPToolDefinitions._get_read_file_tool(),
            MCPToolDefinitions._get_read_code_mem_tool(),
            MCPToolDefinitions._get_write_file_tool(),
            MCPToolDefinitions._get_execute_python_tool(),
            MCPToolDefinitions._get_execute_bash_tool(),
        ]

    @staticmethod
    def _get_read_file_tool() -> Dict[str, Any]:
        """Read file tool definition"""
        return {
            "name": "read_file",
            "description": "Read file content, supports specifying line number range",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path, relative to workspace",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Start line number (starting from 1, optional)",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "End line number (starting from 1, optional)",
                    },
                },
                "required": ["file_path"],
            },
        }

    @staticmethod
    def _get_read_code_mem_tool() -> Dict[str, Any]:
        """Read code memory tool definition - reads from implement_code_summary.md"""
        return {
            "name": "read_code_mem",
            "description": "Check if file summaries exist in implement_code_summary.md for multiple files in a single call. Returns summaries for all requested files if available.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to check for summary information in implement_code_summary.md",
                    }
                },
                "required": ["file_paths"],
            },
        }

    @staticmethod
    def _get_write_file_tool() -> Dict[str, Any]:
        """Write file tool definition"""
        return {
            "name": "write_file",
            "description": "Write content to file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path, relative to workspace",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to file",
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Whether to create directories if they don't exist",
                        "default": True,
                    },
                    "create_backup": {
                        "type": "boolean",
                        "description": "Whether to create backup file if file already exists",
                        "default": False,
                    },
                },
                "required": ["file_path", "content"],
            },
        }

    @staticmethod
    def _get_execute_python_tool() -> Dict[str, Any]:
        """Python execution tool definition"""
        return {
            "name": "execute_python",
            "description": "Execute Python code and return output",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 30,
                    },
                },
                "required": ["code"],
            },
        }

    @staticmethod
    def _get_execute_bash_tool() -> Dict[str, Any]:
        """Bash execution tool definition"""
        return {
            "name": "execute_bash",
            "description": "Execute bash command",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Bash command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        }

    @staticmethod
    def _get_file_structure_tool() -> Dict[str, Any]:
        """File structure retrieval tool definition"""
        return {
            "name": "get_file_structure",
            "description": "Get directory file structure",
            "input_schema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path, relative to workspace",
                        "default": ".",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum traversal depth",
                        "default": 5,
                    },
                },
            },
        }

    @staticmethod
    def _get_search_code_references_tool() -> Dict[str, Any]:
        """Unified code reference search tool definition - combines three steps into one tool"""
        return {
            "name": "search_code_references",
            "description": "UNIFIED TOOL: Search relevant reference code from index files. Combines directory setup, index loading, and searching in a single call.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "indexes_path": {
                        "type": "string",
                        "description": "Path to the indexes directory containing JSON index files",
                    },
                    "target_file": {
                        "type": "string",
                        "description": "Target file path to be implemented",
                    },
                    "keywords": {
                        "type": "string",
                        "description": "Search keywords, comma-separated",
                        "default": "",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10,
                    },
                },
                "required": ["indexes_path", "target_file"],
            },
        }

    @staticmethod
    def _get_get_indexes_overview_tool() -> Dict[str, Any]:
        """Get index overview tool definition"""
        return {
            "name": "get_indexes_overview",
            "description": "Get overview of all available reference code index information from specified directory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "indexes_path": {
                        "type": "string",
                        "description": "Path to the indexes directory containing JSON index files",
                    }
                },
                "required": ["indexes_path"],
            },
        }

    @staticmethod
    def _get_set_workspace_tool() -> Dict[str, Any]:
        """Set workspace directory tool definition"""
        return {
            "name": "set_workspace",
            "description": "Set the workspace directory for file operations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "workspace_path": {
                        "type": "string",
                        "description": "Directory path for the workspace",
                    }
                },
                "required": ["workspace_path"],
            },
        }

    # @staticmethod
    # def _get_set_indexes_directory_tool() -> Dict[str, Any]:
    #     """Set indexes directory tool definition - DEPRECATED: Use unified search_code_references instead"""
    #     return {
    #         "name": "set_indexes_directory",
    #         "description": "Set the directory path for code reference indexes",
    #         "input_schema": {
    #             "type": "object",
    #             "properties": {
    #                 "indexes_path": {
    #                     "type": "string",
    #                     "description": "Directory path containing index JSON files"
    #                 }
    #             },
    #             "required": ["indexes_path"]
    #         }
    #     }

    @staticmethod
    def get_available_tool_sets() -> Dict[str, str]:
        """
        Get available tool sets
        """
        return {
            "code_implementation": "Code implementation tool set",
            # More tool sets can be added here
            # "data_analysis": "Data analysis tool set",
            # "web_scraping": "Web scraping tool set",
        }

    @staticmethod
    def get_tool_set(tool_set_name: str) -> List[Dict[str, Any]]:
        """
        Get specific tool set by name
        """
        tool_sets = {
            "code_implementation": MCPToolDefinitions.get_code_implementation_tools(),
        }

        return tool_sets.get(tool_set_name, [])

    @staticmethod
    def get_all_tools() -> List[Dict[str, Any]]:
        """
        Get all available tools
        """
        all_tools = []
        for tool_set_name in MCPToolDefinitions.get_available_tool_sets().keys():
            all_tools.extend(MCPToolDefinitions.get_tool_set(tool_set_name))
        return all_tools


# Convenience access functions
def get_mcp_tools(tool_set: str = "code_implementation") -> List[Dict[str, Any]]:
    """
    Convenience function: Get MCP tool definitions

    Args:
        tool_set: Tool set name (default: "code_implementation")

    Returns:
        Tool definition list
    """
    return MCPToolDefinitions.get_tool_set(tool_set)
