"""
smolagents - A lightweight agent framework for working with various language models.
"""

from .base_client import test_client
from .web_agent import WebAgent
__version__ = "0.1.0"
__author__ = "Mhdaw"
__all__ = ["test_client", "WebAgent"]