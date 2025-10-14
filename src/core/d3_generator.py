#!/usr/bin/env python3
"""
D3.js HTML generation engine for D3-Mind-Flow-Editor
Generates complete HTML files with embedded D3.js visualizations
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

from ..database.models import DiagramType
from ..utils.logger import logger
from .csv_parser import CSVParser
from .mermaid_parser import MermaidParser


class D3GenerationError(Exception):
    """D3.js generation error"""
    pass


class D3Generator:
    """D3.js HTML generator for different diagram types"""
    
    def __init__(self, assets_path: Optional[Path] = None):
        """Initialize D3 generator
        
        Args:
            assets_path: Path to assets directory
        """
        if assets_path is None:
            # Default to src/assets relative to this file
            self.assets_path = Path(__file__).parent.parent / "assets"
        else:
            self.assets_path = Path(assets_path)
        
        self.templates_path = self.assets_path / "d3_templates"
        
        logger.debug(f"D3Generator initialized with assets path: {self.assets_path}")
    
    def generate_html(
        self,
        content: str,
        diagram_type: str,
        title: str = "D3 Diagram",
        **kwargs
    ) -> str:
        """Generate complete HTML with D3.js visualization
        
        Args:
            content: Input data (CSV or Mermaid)
            diagram_type: Type of diagram (mindmap, gantt, flowchart)
            title: Title for the diagram
            **kwargs: Additional options
            
        Returns:
            Complete HTML string
            
        Raises:
            D3GenerationError: If generation fails
        """
        try:
            if diagram_type == DiagramType.MINDMAP:
                return self._generate_mindmap_html(content, title, **kwargs)
            elif diagram_type == DiagramType.GANTT:
                return self._generate_gantt_html(content, title, **kwargs)
            elif diagram_type == DiagramType.FLOWCHART:
                return self._generate_flowchart_html(content, title, **kwargs)
            else:
                raise D3GenerationError(f"Unsupported diagram type: {diagram_type}")
                
        except Exception as e:
            logger.error(f"Failed to generate D3 HTML: {e}")
            raise D3GenerationError(f"D3 generation failed: {e}")
    
    def _generate_mindmap_html(self, csv_content: str, title: str, **kwargs) -> str:
        """Generate mindmap HTML
        
        Args:
            csv_content: CSV formatted mindmap data
            title: Diagram title
            **kwargs: Additional options
            
        Returns:
            HTML string for mindmap
        """
        # Parse CSV data
        try:
            mindmap_data = CSVParser.parse_mindmap_csv(csv_content)
        except Exception as e:
            raise D3GenerationError(f"Failed to parse mindmap CSV: {e}")
        
        # Load HTML template
        template_path = self.templates_path / "mindmap.html"
        if not template_path.exists():
            raise D3GenerationError(f"Mindmap template not found: {template_path}")
        
        template_html = template_path.read_text(encoding='utf-8')
        
        # Replace template variables
        html = template_html.replace("{{ TITLE }}", self._escape_html(title))
        html = html.replace("{{ JSON_DATA }}", json.dumps(mindmap_data, ensure_ascii=False, indent=2))
        
        logger.debug(f"Generated mindmap HTML for: {title}")
        return html
    
    def _generate_gantt_html(self, csv_content: str, title: str, **kwargs) -> str:
        """Generate Gantt chart HTML
        
        Args:
            csv_content: CSV formatted Gantt data
            title: Diagram title
            **kwargs: Additional options
            
        Returns:
            HTML string for Gantt chart
        """
        # Parse CSV data
        try:
            gantt_data = CSVParser.parse_gantt_csv(csv_content)
        except Exception as e:
            raise D3GenerationError(f"Failed to parse Gantt CSV: {e}")
        
        # Load HTML template
        template_path = self.templates_path / "gantt.html"
        if not template_path.exists():
            raise D3GenerationError(f"Gantt template not found: {template_path}")
        
        template_html = template_path.read_text(encoding='utf-8')
        
        # Replace template variables
        html = template_html.replace("{{ TITLE }}", self._escape_html(title))
        html = html.replace("{{ JSON_DATA }}", json.dumps(gantt_data, ensure_ascii=False, indent=2))
        
        logger.debug(f"Generated Gantt HTML for: {title}")
        return html
    
    def _generate_flowchart_html(self, mermaid_content: str, title: str, **kwargs) -> str:
        """Generate flowchart HTML
        
        Args:
            mermaid_content: Mermaid formatted flowchart data
            title: Diagram title
            **kwargs: Additional options
            
        Returns:
            HTML string for flowchart
        """
        # Validate Mermaid data
        try:
            is_valid, error_msg = MermaidParser.validate_mermaid(mermaid_content)
            if not is_valid:
                logger.warning(f"Mermaid validation warning: {error_msg}")
        except Exception as e:
            logger.warning(f"Mermaid validation failed: {e}")
        
        # Load HTML template
        template_path = self.templates_path / "flowchart.html"
        if not template_path.exists():
            raise D3GenerationError(f"Flowchart template not found: {template_path}")
        
        template_html = template_path.read_text(encoding='utf-8')
        
        # Replace template variables
        html = template_html.replace("{{ TITLE }}", self._escape_html(title))
        html = html.replace("{{ MERMAID_DATA }}", self._escape_mermaid(mermaid_content))
        
        logger.debug(f"Generated flowchart HTML for: {title}")
        return html
    
    def generate_standalone_html(
        self,
        content: str,
        diagram_type: str,
        title: str = "D3 Diagram",
        include_controls: bool = True,
        **kwargs
    ) -> str:
        """Generate standalone HTML file for export
        
        Args:
            content: Input data
            diagram_type: Type of diagram
            title: Diagram title
            include_controls: Whether to include interactive controls
            **kwargs: Additional options
            
        Returns:
            Complete standalone HTML string
        """
        # Generate base HTML
        html = self.generate_html(content, diagram_type, title, **kwargs)
        
        if not include_controls:
            # Remove controls section for static export
            html = self._remove_controls_from_html(html)
        
        # Add metadata for standalone version
        html = self._add_standalone_metadata(html, title, diagram_type)
        
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters
        
        Args:
            text: Text to escape
            
        Returns:
            HTML-escaped text
        """
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    def _escape_mermaid(self, mermaid_text: str) -> str:
        """Escape Mermaid text for JavaScript
        
        Args:
            mermaid_text: Mermaid text to escape
            
        Returns:
            JavaScript-safe string
        """
        # Escape backslashes and quotes for JavaScript
        escaped = (mermaid_text
                   .replace('\\', '\\\\')
                   .replace('`', '\\`')
                   .replace('${', '\\${'))
        
        return escaped
    
    def _remove_controls_from_html(self, html: str) -> str:
        """Remove interactive controls from HTML
        
        Args:
            html: HTML string
            
        Returns:
            HTML without controls
        """
        # Remove controls div
        html = re.sub(r'<div id="controls".*?</div>', '', html, flags=re.DOTALL)
        
        # Remove control-related styles
        html = re.sub(r'#controls\s*\{[^}]*\}', '', html, flags=re.DOTALL)
        html = re.sub(r'#controls[^{]*\{[^}]*\}', '', html, flags=re.DOTALL)
        
        return html
    
    def _add_standalone_metadata(self, html: str, title: str, diagram_type: str) -> str:
        """Add metadata to standalone HTML
        
        Args:
            html: HTML string
            title: Diagram title
            diagram_type: Type of diagram
            
        Returns:
            HTML with added metadata
        """
        # Add meta tags in head section
        metadata = f'''
    <meta name="generator" content="D3-Mind-Flow-Editor">
    <meta name="diagram-type" content="{diagram_type}">
    <meta name="diagram-title" content="{self._escape_html(title)}">
    <meta name="created-date" content="{self._get_current_datetime()}">
'''
        
        # Insert metadata after <head>
        html = html.replace('<head>', f'<head>{metadata}')
        
        return html
    
    def _get_current_datetime(self) -> str:
        """Get current datetime as ISO string
        
        Returns:
            Current datetime in ISO format
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def preview_html(
        self,
        content: str,
        diagram_type: str,
        title: str = "Preview"
    ) -> str:
        """Generate HTML for preview (simplified version)
        
        Args:
            content: Input data
            diagram_type: Type of diagram
            title: Preview title
            
        Returns:
            HTML string optimized for preview
        """
        try:
            return self.generate_html(content, diagram_type, title)
        except Exception as e:
            # Return error HTML for preview
            return self._generate_error_html(str(e), diagram_type)
    
    def _generate_error_html(self, error_message: str, diagram_type: str) -> str:
        """Generate error HTML for display
        
        Args:
            error_message: Error message to display
            diagram_type: Type of diagram (for styling)
            
        Returns:
            Error HTML string
        """
        return f'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>エラー - {diagram_type}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }}
        .error-container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 50px auto;
        }}
        .error-icon {{
            font-size: 48px;
            color: #dc3545;
            margin-bottom: 20px;
        }}
        .error-title {{
            font-size: 24px;
            color: #dc3545;
            margin-bottom: 15px;
        }}
        .error-message {{
            font-size: 16px;
            color: #6c757d;
            line-height: 1.5;
            margin-bottom: 20px;
        }}
        .error-details {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            text-align: left;
            color: #495057;
            white-space: pre-wrap;
            word-break: break-word;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <div class="error-title">図表生成エラー</div>
        <div class="error-message">
            図表の生成中にエラーが発生しました。<br>
            入力データの形式をご確認ください。
        </div>
        <div class="error-details">{self._escape_html(error_message)}</div>
    </div>
</body>
</html>'''
    
    def validate_template_files(self) -> Dict[str, bool]:
        """Validate that all template files exist
        
        Returns:
            Dictionary mapping template names to existence status
        """
        templates = {
            'mindmap': self.templates_path / "mindmap.html",
            'gantt': self.templates_path / "gantt.html",
            'flowchart': self.templates_path / "flowchart.html"
        }
        
        status = {}
        for name, path in templates.items():
            status[name] = path.exists()
            if not path.exists():
                logger.warning(f"Template file missing: {path}")
        
        return status
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get information about available templates
        
        Returns:
            Dictionary with template information
        """
        templates = self.validate_template_files()
        
        info = {
            'templates_path': str(self.templates_path),
            'available_templates': templates,
            'all_templates_available': all(templates.values()),
            'missing_templates': [name for name, exists in templates.items() if not exists]
        }
        
        return info


class D3StyleManager:
    """Manages D3.js styling and themes"""
    
    DEFAULT_COLORS = {
        'mindmap': {
            'primary': '#4CAF50',
            'secondary': '#8BC34A',
            'background': '#f8f9fa'
        },
        'gantt': {
            'completed': '#8BC34A',
            'in_progress': '#FFC107',
            'not_started': '#E0E0E0',
            'background': '#f8f9fa'
        },
        'flowchart': {
            'primary': '#FF9800',
            'secondary': '#FFC107',
            'background': '#f8f9fa'
        }
    }
    
    @classmethod
    def get_color_scheme(cls, diagram_type: str, theme: str = 'default') -> Dict[str, str]:
        """Get color scheme for diagram type
        
        Args:
            diagram_type: Type of diagram
            theme: Theme name
            
        Returns:
            Dictionary of color values
        """
        base_colors = cls.DEFAULT_COLORS.get(diagram_type, cls.DEFAULT_COLORS['mindmap'])
        
        if theme == 'dark':
            return cls._apply_dark_theme(base_colors)
        elif theme == 'blue':
            return cls._apply_blue_theme(base_colors)
        
        return base_colors
    
    @classmethod
    def _apply_dark_theme(cls, colors: Dict[str, str]) -> Dict[str, str]:
        """Apply dark theme to colors
        
        Args:
            colors: Base color scheme
            
        Returns:
            Dark theme colors
        """
        dark_colors = colors.copy()
        dark_colors['background'] = '#2d3748'
        dark_colors['text'] = '#ffffff'
        return dark_colors
    
    @classmethod
    def _apply_blue_theme(cls, colors: Dict[str, str]) -> Dict[str, str]:
        """Apply blue theme to colors
        
        Args:
            colors: Base color scheme
            
        Returns:
            Blue theme colors
        """
        blue_colors = colors.copy()
        blue_colors['primary'] = '#2196F3'
        blue_colors['secondary'] = '#64B5F6'
        return blue_colors