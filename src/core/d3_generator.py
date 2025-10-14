#!/usr/bin/env python3
"""
D3.js HTML Generator for D3-Mind-Flow-Editor
Complete implementation with template system and export functionality
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import re
from datetime import datetime

from ..database.models import DiagramType
from ..utils.logger import logger


class D3Generator:
    """Generate D3.js HTML content for different diagram types"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "assets" / "d3_templates"
        self.cache = {}
        logger.debug("D3 generator initialized")
    
    def generate_html(self, 
                     content: str, 
                     diagram_type: str, 
                     data: Optional[Dict[str, Any]] = None,
                     standalone: bool = False,
                     title: str = None,
                     export_options: Optional[Dict[str, Any]] = None) -> str:
        """Generate complete HTML with D3.js visualization
        
        Args:
            content: Raw content (CSV/Mermaid)
            diagram_type: Type of diagram
            data: Processed data (optional)
            standalone: Whether to generate standalone HTML
            title: Custom title for the diagram
            export_options: Export-specific options
            
        Returns:
            Complete HTML string
        """
        try:
            export_options = export_options or {}
            
            if diagram_type == DiagramType.MINDMAP:
                return self._generate_mindmap_html(content, data, standalone, title, export_options)
            elif diagram_type == DiagramType.GANTT:
                return self._generate_gantt_html(content, data, standalone, title, export_options)
            elif diagram_type == DiagramType.FLOWCHART:
                return self._generate_flowchart_html(content, data, standalone, title, export_options)
            else:
                raise ValueError(f"Unsupported diagram type: {diagram_type}")
                
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            return self._generate_error_html(str(e))
    
    def _generate_mindmap_html(self, 
                              content: str, 
                              data: Optional[Dict[str, Any]], 
                              standalone: bool,
                              title: str,
                              export_options: Dict[str, Any]) -> str:
        """Generate mind map HTML using the existing template"""
        template_path = self.template_dir / "mindmap.html"
        
        if not template_path.exists():
            return self._generate_fallback_mindmap(content, standalone)
        
        # Load and cache template
        template_key = f"mindmap_{standalone}"
        if template_key not in self.cache:
            template = template_path.read_text(encoding='utf-8')
            
            if standalone:
                # Enhance template for standalone export
                template = self._enhance_template_for_export(template, "mindmap", export_options)
            
            self.cache[template_key] = template
        else:
            template = self.cache[template_key]
        
        # Process data if not provided
        if data is None:
            try:
                from .csv_parser import parse_mindmap_csv
                data = parse_mindmap_csv(content)
            except Exception as e:
                logger.warning(f"Failed to parse CSV: {e}")
                data = self._generate_sample_mindmap_data(content)
        
        # Replace template variables
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        html = template.replace("{{ JSON_DATA }}", json_data)
        html = html.replace("{{ TITLE }}", title or data.get("name", "Mind Map"))
        
        # Add metadata for exports
        if standalone:
            html = self._add_export_metadata(html, "mindmap", title, export_options)
        
        return html
    
    def _generate_gantt_html(self, 
                            content: str, 
                            data: Optional[Dict[str, Any]], 
                            standalone: bool,
                            title: str,
                            export_options: Dict[str, Any]) -> str:
        """Generate Gantt chart HTML using the existing template"""
        template_path = self.template_dir / "gantt.html"
        
        if not template_path.exists():
            return self._generate_fallback_gantt(content, standalone)
        
        # Load and cache template
        template_key = f"gantt_{standalone}"
        if template_key not in self.cache:
            template = template_path.read_text(encoding='utf-8')
            
            if standalone:
                # Enhance template for standalone export
                template = self._enhance_template_for_export(template, "gantt", export_options)
            
            self.cache[template_key] = template
        else:
            template = self.cache[template_key]
        
        # Process data if not provided
        if data is None:
            try:
                from .csv_parser import parse_gantt_csv
                data = parse_gantt_csv(content)
            except Exception as e:
                logger.warning(f"Failed to parse CSV: {e}")
                data = self._generate_sample_gantt_data(content)
        
        # Replace template variables
        json_data = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        html = template.replace("{{ JSON_DATA }}", json_data)
        html = html.replace("{{ TITLE }}", title or "Gantt Chart")
        
        # Add metadata for exports
        if standalone:
            html = self._add_export_metadata(html, "gantt", title, export_options)
        
        return html
    
    def _generate_flowchart_html(self, 
                                content: str, 
                                data: Optional[Dict[str, Any]], 
                                standalone: bool,
                                title: str,
                                export_options: Dict[str, Any]) -> str:
        """Generate flowchart HTML using the existing template"""
        template_path = self.template_dir / "flowchart.html"
        
        if not template_path.exists():
            return self._generate_fallback_flowchart(content, standalone)
        
        # Load and cache template
        template_key = f"flowchart_{standalone}"
        if template_key not in self.cache:
            template = template_path.read_text(encoding='utf-8')
            
            if standalone:
                # Enhance template for standalone export
                template = self._enhance_template_for_export(template, "flowchart", export_options)
            
            self.cache[template_key] = template
        else:
            template = self.cache[template_key]
        
        # Validate and process Mermaid content
        mermaid_content = content.strip() if content.strip() else self._get_sample_mermaid()
        
        if data is None:
            try:
                from .mermaid_parser import parse_mermaid
                data = parse_mermaid(mermaid_content)
            except Exception as e:
                logger.warning(f"Failed to parse Mermaid: {e}")
                mermaid_content = self._get_sample_mermaid()
        
        # Replace template variables
        html = template.replace("{{ MERMAID_CONTENT }}", mermaid_content)
        html = html.replace("{{ TITLE }}", title or "Flowchart")
        
        # Add metadata for exports
        if standalone:
            html = self._add_export_metadata(html, "flowchart", title, export_options)
        
        return html
    
    def _enhance_template_for_export(self, template: str, diagram_type: str, export_options: Dict[str, Any]) -> str:
        """Enhance template for standalone export"""
        enhancements = []
        
        # Add export-specific styles
        export_css = """
        <style id="export-enhancements">
        @media print {
            #controls { display: none !important; }
            .no-print { display: none !important; }
            body { margin: 0; padding: 0; }
        }
        
        .export-ready {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
        }
        
        .export-metadata {
            position: fixed;
            bottom: 10px;
            left: 10px;
            font-size: 10px;
            color: #666;
            background: rgba(255, 255, 255, 0.8);
            padding: 5px;
            border-radius: 3px;
            z-index: 2000;
        }
        </style>
        """
        
        # Insert before closing </head> tag
        template = template.replace("</head>", export_css + "\n</head>")
        
        # Add export-ready class to body
        template = re.sub(r'<body([^>]*)>', r'<body\1 class="export-ready">', template)
        
        # Add export optimization script
        export_script = """
        <script id="export-optimization">
        // Export optimization
        document.addEventListener('DOMContentLoaded', function() {
            // Wait for complete rendering
            setTimeout(function() {
                // Signal export readiness
                window.exportReady = true;
                
                // Dispatch custom event for export tools
                window.dispatchEvent(new Event('exportready'));
            }, 2000);
        });
        
        // Disable animations for exports if specified
        if (window.location.hash === '#export-static') {
            document.documentElement.style.setProperty('--animation-duration', '0s');
        }
        </script>
        """
        
        # Insert before closing </body> tag
        template = template.replace("</body>", export_script + "\n</body>")
        
        return template
    
    def _add_export_metadata(self, html: str, diagram_type: str, title: str, export_options: Dict[str, Any]) -> str:
        """Add metadata for exported files"""
        metadata = f"""
        <div class="export-metadata">
            Generated by D3-Mind-Flow-Editor | {diagram_type.title()} | {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
        """
        
        # Insert before closing </body> tag
        html = html.replace("</body>", metadata + "\n</body>")
        
        return html
    
    def _generate_sample_mindmap_data(self, content: str) -> Dict[str, Any]:
        """Generate sample mind map data when parsing fails"""
        return {
            "name": "Sample Mind Map",
            "children": [
                {
                    "name": "Branch 1",
                    "children": [
                        {"name": "Leaf 1.1"},
                        {"name": "Leaf 1.2"}
                    ]
                },
                {
                    "name": "Branch 2", 
                    "children": [
                        {"name": "Leaf 2.1"},
                        {"name": "Leaf 2.2"}
                    ]
                }
            ]
        }
    
    def _generate_sample_gantt_data(self, content: str) -> list:
        """Generate sample Gantt data when parsing fails"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        return [
            {
                "task": "Sample Task 1",
                "start": today.strftime("%Y-%m-%d"),
                "end": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
                "progress": 50,
                "resource": "Team Member"
            },
            {
                "task": "Sample Task 2",
                "start": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "end": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
                "progress": 25,
                "resource": "Team Lead"
            }
        ]
    
    def _get_sample_mermaid(self) -> str:
        """Get sample Mermaid flowchart"""
        return """flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E"""
    
    def _generate_fallback_mindmap(self, content: str, standalone: bool = False) -> str:
        """Generate fallback mind map HTML"""
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Mind Map - Fallback</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5;
        }}
        .fallback {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        pre {{ 
            background: #f9f9f9; 
            padding: 15px; 
            border-radius: 4px; 
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div class="fallback">
        <h2>🧠 Mind Map (Fallback Mode)</h2>
        <p>Template not found. Displaying raw content:</p>
        <pre>{content}</pre>
        <p><small>Generated by D3-Mind-Flow-Editor</small></p>
    </div>
</body>
</html>
        """
    
    def _generate_fallback_gantt(self, content: str, standalone: bool = False) -> str:
        """Generate fallback Gantt chart HTML"""
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Gantt Chart - Fallback</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5;
        }}
        .fallback {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        pre {{ 
            background: #f9f9f9; 
            padding: 15px; 
            border-radius: 4px; 
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div class="fallback">
        <h2>📅 Gantt Chart (Fallback Mode)</h2>
        <p>Template not found. Displaying raw content:</p>
        <pre>{content}</pre>
        <p><small>Generated by D3-Mind-Flow-Editor</small></p>
    </div>
</body>
</html>
        """
    
    def _generate_fallback_flowchart(self, content: str, standalone: bool = False) -> str:
        """Generate fallback flowchart HTML"""
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Flowchart - Fallback</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5;
        }}
        .fallback {{ 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .mermaid {{
            text-align: center;
            margin: 20px 0;
        }}
        pre {{ 
            background: #f9f9f9; 
            padding: 15px; 
            border-radius: 4px; 
            overflow: auto;
        }}
    </style>
</head>
<body>
    <div class="fallback">
        <h2>📈 Flowchart (Fallback Mode)</h2>
        <div class="mermaid">{content or self._get_sample_mermaid()}</div>
        <p>Raw Mermaid content:</p>
        <pre>{content}</pre>
        <p><small>Generated by D3-Mind-Flow-Editor</small></p>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose'
        }});
    </script>
</body>
</html>
        """
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generate error HTML"""
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>生成エラー - D3-Mind-Flow-Editor</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 50px; 
            background: #f8f9fa;
        }}
        .error {{ 
            color: #721c24;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 20px; 
            border-radius: 8px;
            margin: 20px 0;
        }}
        .error h2 {{
            color: #721c24;
            margin-top: 0;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 15px;
            padding: 8px 16px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .back-link:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="error">
        <h2>⚠️ 図表生成エラー</h2>
        <p><strong>エラー内容:</strong></p>
        <p>{error_message}</p>
        <p>以下をご確認ください：</p>
        <ul>
            <li>入力データの形式が正しいか</li>
            <li>必要なライブラリがインストールされているか</li>
            <li>ネットワーク接続に問題がないか</li>
        </ul>
        <a href="javascript:history.back()" class="back-link">← 戻る</a>
    </div>
    <footer style="margin-top: 40px; text-align: center; color: #666; font-size: 12px;">
        Generated by D3-Mind-Flow-Editor | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </footer>
</body>
</html>
        """
    
    def get_template_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available templates"""
        templates = {}
        
        for template_file in self.template_dir.glob("*.html"):
            name = template_file.stem
            templates[name] = {
                "path": str(template_file),
                "exists": template_file.exists(),
                "size": template_file.stat().st_size if template_file.exists() else 0,
                "modified": datetime.fromtimestamp(template_file.stat().st_mtime) if template_file.exists() else None
            }
        
        return templates
    
    def clear_cache(self):
        """Clear template cache"""
        self.cache.clear()
        logger.debug("Template cache cleared")
    
    def validate_template(self, diagram_type: str) -> Dict[str, Any]:
        """Validate template file for diagram type"""
        template_map = {
            DiagramType.MINDMAP: "mindmap.html",
            DiagramType.GANTT: "gantt.html", 
            DiagramType.FLOWCHART: "flowchart.html"
        }
        
        template_file = template_map.get(diagram_type)
        if not template_file:
            return {"valid": False, "error": f"Unknown diagram type: {diagram_type}"}
        
        template_path = self.template_dir / template_file
        
        if not template_path.exists():
            return {
                "valid": False, 
                "error": f"Template file not found: {template_path}",
                "fallback_available": True
            }
        
        try:
            content = template_path.read_text(encoding='utf-8')
            
            # Basic validation
            if "{{ JSON_DATA }}" not in content and "{{ MERMAID_CONTENT }}" not in content:
                return {
                    "valid": False,
                    "error": "Template missing required placeholder variables",
                    "fallback_available": True
                }
            
            return {
                "valid": True,
                "path": str(template_path),
                "size": len(content),
                "placeholders": re.findall(r'{{\\s*(\\w+)\\s*}}', content)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Template validation failed: {e}",
                "fallback_available": True
            }