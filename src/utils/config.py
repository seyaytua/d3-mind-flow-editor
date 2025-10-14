#!/usr/bin/env python3
"""
Configuration management for D3-Mind-Flow-Editor
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        "display": {
            "dpi_scaling": "auto",
            "anti_aliasing": True,
            "rendering_quality": "standard"
        },
        "export": {
            "png_dpi": 300,
            "png_width": 1920,
            "png_height": 1080,
            "png_keep_aspect": True,
            "pdf_vector": True,
            "pdf_paper_size": "A4"
        },
        "ui": {
            "window_width": 1200,
            "window_height": 800,
            "splitter_sizes": [400, 800],
            "theme": "default"
        },
        "editor": {
            "auto_save": True,
            "auto_save_interval": 30,
            "show_line_numbers": True,
            "word_wrap": True
        },
        "paths": {
            "export_directory": "",
            "template_directory": ""
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            home_dir = Path.home()
            config_dir = home_dir / ".d3_mind_flow_editor"
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
        
        self._config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(self._config, user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            print("Using default configuration")
    
    def save(self):
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path (e.g., 'display.dpi_scaling')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation
        
        Args:
            key_path: Dot-separated path (e.g., 'display.dpi_scaling')
            value: Value to set
        """
        keys = key_path.split('.')
        target = self._config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Set the final value
        target[keys[-1]] = value
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self.DEFAULT_CONFIG.copy()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return self._config.copy()
    
    @staticmethod
    def _merge_config(base: Dict[str, Any], user: Dict[str, Any]):
        """Recursively merge user config into base config"""
        for key, value in user.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._merge_config(base[key], value)
            else:
                base[key] = value
    
    # Convenience properties for common settings
    @property
    def dpi_scaling(self) -> str:
        return self.get('display.dpi_scaling', 'auto')
    
    @dpi_scaling.setter
    def dpi_scaling(self, value: str):
        self.set('display.dpi_scaling', value)
    
    @property
    def png_dpi(self) -> int:
        return self.get('export.png_dpi', 300)
    
    @png_dpi.setter
    def png_dpi(self, value: int):
        self.set('export.png_dpi', value)
    
    @property
    def window_size(self) -> tuple[int, int]:
        width = self.get('ui.window_width', 1200)
        height = self.get('ui.window_height', 800)
        return (width, height)
    
    @window_size.setter
    def window_size(self, size: tuple[int, int]):
        self.set('ui.window_width', size[0])
        self.set('ui.window_height', size[1])
    
    @property
    def export_directory(self) -> str:
        return self.get('paths.export_directory', '')
    
    @export_directory.setter
    def export_directory(self, path: str):
        self.set('paths.export_directory', path)