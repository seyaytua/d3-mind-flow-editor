#!/usr/bin/env python3
"""
Clipboard operations for D3-Mind-Flow-Editor
"""

import pyperclip
from typing import Optional

from .logger import logger


class ClipboardManager:
    """Manages clipboard operations"""
    
    @staticmethod
    def copy_text(text: str) -> bool:
        """Copy text to clipboard
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy(text)
            logger.debug(f"Copied {len(text)} characters to clipboard")
            return True
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False
    
    @staticmethod
    def paste_text() -> Optional[str]:
        """Get text from clipboard
        
        Returns:
            Clipboard text or None if failed
        """
        try:
            text = pyperclip.paste()
            logger.debug(f"Pasted {len(text)} characters from clipboard")
            return text
        except Exception as e:
            logger.error(f"Failed to paste from clipboard: {e}")
            return None
    
    @staticmethod
    def has_text() -> bool:
        """Check if clipboard has text content
        
        Returns:
            True if clipboard contains text, False otherwise
        """
        try:
            text = pyperclip.paste()
            return isinstance(text, str) and len(text) > 0
        except Exception:
            return False