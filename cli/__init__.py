"""
CLI Module for DeepCode Agent
DeepCode Agent CLI Module

Contains the following components:
- cli_app: CLI application main program
- cli_interface: CLI interface components  
- cli_launcher: CLI launcher
"""

__version__ = "1.0.0"
__author__ = "DeepCode Team - Data Intelligence Lab @ HKU"

from .cli_app import main as cli_main
from .cli_interface import CLIInterface
from .cli_launcher import main as launcher_main

__all__ = ["cli_main", "CLIInterface", "launcher_main"]