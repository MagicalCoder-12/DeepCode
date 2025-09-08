"""
CLI-specific Workflow Adapters
CLI-specific workflow adapter

This module provides CLI-optimized versions of workflow components that are
specifically adapted for command-line interface usage patterns.
"""

from .cli_workflow_adapter import CLIWorkflowAdapter

__all__ = ["CLIWorkflowAdapter"]
