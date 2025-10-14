#!/usr/bin/env python3
"""
Resolution and DPI management for D3-Mind-Flow-Editor
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize
from PySide6.QtGui import QScreen
from typing import Tuple, Optional

from .logger import logger
from .config import Config


class ResolutionManager:
    """Manages display resolution and DPI scaling"""
    
    def __init__(self, config: Config):
        """Initialize resolution manager
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self._device_pixel_ratio = 1.0
        self._logical_dpi = 96
        self._physical_dpi = 96
        
        self._detect_display_properties()
    
    def _detect_display_properties(self):
        """Detect display properties"""
        app = QApplication.instance()
        if app is None:
            logger.warning("No QApplication instance found, using default DPI values")
            return
        
        try:
            screen = app.primaryScreen()
            if screen is None:
                logger.warning("No primary screen found")
                return
            
            self._device_pixel_ratio = screen.devicePixelRatio()
            self._logical_dpi = screen.logicalDotsPerInch()
            self._physical_dpi = screen.physicalDotsPerInch()
            
            logger.info(f"Display detected - DPR: {self._device_pixel_ratio}, "
                       f"Logical DPI: {self._logical_dpi}, Physical DPI: {self._physical_dpi}")
            
        except Exception as e:
            logger.error(f"Failed to detect display properties: {e}")
    
    def get_device_pixel_ratio(self) -> float:
        """Get device pixel ratio"""
        return self._device_pixel_ratio
    
    def get_logical_dpi(self) -> float:
        """Get logical DPI"""
        return self._logical_dpi
    
    def get_physical_dpi(self) -> float:
        """Get physical DPI"""
        return self._physical_dpi
    
    def is_high_dpi(self) -> bool:
        """Check if display is high DPI (Retina/4K)"""
        return self._device_pixel_ratio > 1.0
    
    def get_scaling_factor(self) -> float:
        """Get DPI scaling factor based on configuration
        
        Returns:
            Scaling factor to apply
        """
        dpi_setting = self.config.dpi_scaling
        
        if dpi_setting == "auto":
            return self._device_pixel_ratio
        elif dpi_setting == "100%":
            return 1.0
        elif dpi_setting == "150%":
            return 1.5
        elif dpi_setting == "200%":
            return 2.0
        elif dpi_setting == "300%":
            return 3.0
        else:
            logger.warning(f"Unknown DPI setting: {dpi_setting}, using auto")
            return self._device_pixel_ratio
    
    def get_export_dpi(self) -> int:
        """Get DPI for export operations
        
        Returns:
            DPI value for exports
        """
        base_dpi = self.config.png_dpi
        scaling = self.get_scaling_factor()
        
        # Apply scaling to export DPI for high-DPI displays
        if self.is_high_dpi():
            return int(base_dpi * scaling)
        else:
            return base_dpi
    
    def scale_size(self, size: QSize) -> QSize:
        """Scale size for high DPI displays
        
        Args:
            size: Original size
            
        Returns:
            Scaled size
        """
        scaling = self.get_scaling_factor()
        return QSize(
            int(size.width() * scaling),
            int(size.height() * scaling)
        )
    
    def scale_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        """Scale dimensions for high DPI displays
        
        Args:
            width: Original width
            height: Original height
            
        Returns:
            Scaled (width, height) tuple
        """
        scaling = self.get_scaling_factor()
        return (
            int(width * scaling),
            int(height * scaling)
        )
    
    def get_optimal_size(self, base_width: int, base_height: int) -> Tuple[int, int]:
        """Get optimal size for current display
        
        Args:
            base_width: Base width in pixels
            base_height: Base height in pixels
            
        Returns:
            Optimal (width, height) for current display
        """
        if self.is_high_dpi():
            return self.scale_dimensions(base_width, base_height)
        else:
            return (base_width, base_height)
    
    def get_display_info(self) -> dict:
        """Get comprehensive display information
        
        Returns:
            Dictionary with display properties
        """
        app = QApplication.instance()
        screen_info = {}
        
        if app and app.primaryScreen():
            screen = app.primaryScreen()
            geometry = screen.geometry()
            screen_info = {
                'geometry': {
                    'width': geometry.width(),
                    'height': geometry.height()
                },
                'available_geometry': {
                    'width': screen.availableGeometry().width(),
                    'height': screen.availableGeometry().height()
                },
                'name': screen.name()
            }
        
        return {
            'device_pixel_ratio': self._device_pixel_ratio,
            'logical_dpi': self._logical_dpi,
            'physical_dpi': self._physical_dpi,
            'is_high_dpi': self.is_high_dpi(),
            'scaling_factor': self.get_scaling_factor(),
            'export_dpi': self.get_export_dpi(),
            'screen': screen_info
        }