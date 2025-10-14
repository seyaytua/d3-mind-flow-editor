#!/usr/bin/env python3
"""
Export Manager for D3-Mind-Flow-Editor
Handles all export functionality for different diagram types and formats
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..utils.logger import logger
from ..database.models import DiagramType
from .d3_generator import D3Generator


class ExportManager:
    """Export manager for different diagram formats"""
    
    def __init__(self):
        self.d3_generator = D3Generator()
        self.temp_dir = tempfile.mkdtemp(prefix="d3_mindflow_")
        
        logger.debug("Export manager initialized")
    
    def export_diagram(self, 
                      content: str, 
                      diagram_type: str, 
                      output_path: str, 
                      format: str = "html",
                      options: Optional[Dict[str, Any]] = None) -> bool:
        """Export diagram to specified format
        
        Args:
            content: Diagram content (CSV/Mermaid)
            diagram_type: Type of diagram (mindmap, gantt, flowchart)
            output_path: Output file path
            format: Export format (html, png, svg, pdf)
            options: Export options (quality, size, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            options = options or {}
            
            logger.info(f"Exporting {diagram_type} as {format} to {output_path}")
            
            if format.lower() == "html":
                return self._export_html(content, diagram_type, output_path, options)
            elif format.lower() == "png":
                return self._export_png(content, diagram_type, output_path, options)
            elif format.lower() == "svg":
                return self._export_svg(content, diagram_type, output_path, options)
            elif format.lower() == "pdf":
                return self._export_pdf(content, diagram_type, output_path, options)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def _export_html(self, content: str, diagram_type: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Export as standalone HTML file"""
        try:
            # Generate complete HTML with embedded data
            html_content = self.d3_generator.generate_html(content, diagram_type, standalone=True)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML exported successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            return False
    
    def _export_png(self, content: str, diagram_type: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Export as PNG image using Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available for PNG export")
            return False
        
        try:
            # Generate HTML content
            html_content = self.d3_generator.generate_html(content, diagram_type, standalone=True)
            
            # Create temporary HTML file
            temp_html = os.path.join(self.temp_dir, f"export_{datetime.now().timestamp()}.html")
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Screenshot with Playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Set viewport size
                width = options.get('width', 1200)
                height = options.get('height', 800)
                page.set_viewport_size({"width": width, "height": height})
                
                # Load page and wait for content
                page.goto(f"file://{temp_html}")
                page.wait_for_timeout(3000)  # Wait for D3.js rendering
                
                # Take screenshot
                page.screenshot(path=output_path, full_page=options.get('full_page', True))
                
                browser.close()
            
            # Cleanup
            os.remove(temp_html)
            
            logger.info(f"PNG exported successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PNG export failed: {e}")
            return False
    
    def _export_svg(self, content: str, diagram_type: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Export as SVG using Playwright to extract SVG content"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available for SVG export")
            return False
        
        try:
            # Generate HTML content
            html_content = self.d3_generator.generate_html(content, diagram_type, standalone=True)
            
            # Create temporary HTML file
            temp_html = os.path.join(self.temp_dir, f"export_{datetime.now().timestamp()}.html")
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Extract SVG with Playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Load page and wait for content
                page.goto(f"file://{temp_html}")
                page.wait_for_timeout(3000)  # Wait for D3.js rendering
                
                # Extract SVG content
                svg_content = page.evaluate("""
                    () => {
                        const svg = document.querySelector('svg');
                        return svg ? svg.outerHTML : null;
                    }
                """)
                
                browser.close()
            
            if svg_content:
                # Add XML declaration and styling
                full_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
{svg_content}'''
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_svg)
                
                logger.info(f"SVG exported successfully to {output_path}")
                return True
            else:
                logger.error("No SVG content found in generated HTML")
                return False
            
            # Cleanup
            os.remove(temp_html)
            
        except Exception as e:
            logger.error(f"SVG export failed: {e}")
            return False
    
    def _export_pdf(self, content: str, diagram_type: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Export as PDF using PNG conversion or direct PDF generation"""
        try:
            # Method 1: PNG to PDF conversion
            if PLAYWRIGHT_AVAILABLE and PIL_AVAILABLE and REPORTLAB_AVAILABLE:
                return self._export_pdf_via_png(content, diagram_type, output_path, options)
            
            # Method 2: Direct PDF generation (limited functionality)
            elif REPORTLAB_AVAILABLE:
                return self._export_pdf_direct(content, diagram_type, output_path, options)
            
            else:
                logger.error("Required libraries for PDF export not available")
                return False
                
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return False
    
    def _export_pdf_via_png(self, content: str, diagram_type: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Export PDF via PNG conversion"""
        try:
            # Create temporary PNG
            temp_png = os.path.join(self.temp_dir, f"temp_{datetime.now().timestamp()}.png")
            
            # Export as PNG first
            png_options = {
                'width': options.get('width', 1200),
                'height': options.get('height', 800),
                'full_page': options.get('full_page', True)
            }
            
            if not self._export_png(content, diagram_type, temp_png, png_options):
                return False
            
            # Convert PNG to PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            # Open PNG image
            img = Image.open(temp_png)
            img_width, img_height = img.size
            
            # Create PDF
            page_size = options.get('page_size', A4)
            pdf_canvas = canvas.Canvas(output_path, pagesize=page_size)
            
            # Calculate scaling to fit page
            page_width, page_height = page_size
            scale_x = (page_width - 40) / img_width  # 20px margin on each side
            scale_y = (page_height - 40) / img_height
            scale = min(scale_x, scale_y)
            
            # Calculate centered position
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            # Draw image
            pdf_canvas.drawImage(ImageReader(img), x, y, scaled_width, scaled_height)
            
            # Add metadata
            pdf_canvas.setTitle(f"{diagram_type.title()} Chart")
            pdf_canvas.setAuthor("D3-Mind-Flow-Editor")
            pdf_canvas.setSubject(f"Exported {diagram_type} diagram")
            pdf_canvas.setCreator("D3-Mind-Flow-Editor")
            
            pdf_canvas.save()
            
            # Cleanup
            os.remove(temp_png)
            
            logger.info(f"PDF exported successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF via PNG export failed: {e}")
            return False
    
    def _export_pdf_direct(self, content: str, diagram_type: str, output_path: str, options: Dict[str, Any]) -> bool:
        """Direct PDF generation (text-based, limited functionality)"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            story.append(Paragraph(f"{diagram_type.title()} Chart", title_style))
            story.append(Spacer(1, 20))
            
            # Content (simplified text representation)
            content_style = styles['Normal']
            story.append(Paragraph("Diagram Content:", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Process content based on type
            if diagram_type == DiagramType.MINDMAP:
                lines = content.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        story.append(Paragraph(f"• {line.strip()}", content_style))
            
            elif diagram_type == DiagramType.GANTT:
                lines = content.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        story.append(Paragraph(f"Task: {line.strip()}", content_style))
            
            elif diagram_type == DiagramType.FLOWCHART:
                story.append(Paragraph("Flowchart Mermaid Code:", content_style))
                story.append(Spacer(1, 12))
                code_style = ParagraphStyle(
                    'Code',
                    parent=styles['Code'],
                    fontSize=10,
                    fontName='Courier'
                )
                story.append(Paragraph(content.replace('\n', '<br/>'), code_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1
            )
            story.append(Paragraph(f"Generated by D3-Mind-Flow-Editor on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF exported successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Direct PDF export failed: {e}")
            return False
    
    def get_export_formats(self) -> Dict[str, Dict[str, Any]]:
        """Get available export formats and their capabilities"""
        formats = {
            "html": {
                "name": "HTML",
                "extension": ".html",
                "description": "Interactive HTML file with embedded D3.js",
                "available": True,
                "primary_for": [DiagramType.MINDMAP]
            },
            "png": {
                "name": "PNG Image",
                "extension": ".png",
                "description": "High-quality raster image",
                "available": PLAYWRIGHT_AVAILABLE,
                "primary_for": [DiagramType.FLOWCHART]
            },
            "svg": {
                "name": "SVG Vector",
                "extension": ".svg",
                "description": "Scalable vector graphics",
                "available": PLAYWRIGHT_AVAILABLE,
                "primary_for": [DiagramType.GANTT]
            },
            "pdf": {
                "name": "PDF Document",
                "extension": ".pdf",
                "description": "Portable document format",
                "available": REPORTLAB_AVAILABLE,
                "primary_for": []
            }
        }
        
        return formats
    
    def get_export_options(self, format: str) -> Dict[str, Any]:
        """Get available export options for a format"""
        base_options = {
            "quality": {"type": "int", "default": 100, "min": 10, "max": 100},
            "title": {"type": "str", "default": "Diagram"},
        }
        
        if format in ["png", "svg"]:
            base_options.update({
                "width": {"type": "int", "default": 1200, "min": 400, "max": 4000},
                "height": {"type": "int", "default": 800, "min": 300, "max": 3000},
                "full_page": {"type": "bool", "default": True}
            })
        
        if format == "pdf":
            base_options.update({
                "page_size": {"type": "choice", "default": "A4", "choices": ["A4", "Letter", "Legal"]},
                "orientation": {"type": "choice", "default": "portrait", "choices": ["portrait", "landscape"]}
            })
        
        return base_options
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.debug("Export manager cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


# Export format utilities
class ExportFormatUtils:
    """Utilities for export format handling"""
    
    @staticmethod
    def get_default_format(diagram_type: str) -> str:
        """Get the default export format for a diagram type"""
        defaults = {
            DiagramType.MINDMAP: "html",
            DiagramType.FLOWCHART: "png", 
            DiagramType.GANTT: "svg"
        }
        return defaults.get(diagram_type, "html")
    
    @staticmethod
    def get_format_description(format: str) -> str:
        """Get description of export format"""
        descriptions = {
            "html": "Interactive web page with full functionality",
            "png": "High-quality static image for presentations",
            "svg": "Vector graphics for scalable printing",
            "pdf": "Document format for reports and sharing"
        }
        return descriptions.get(format, "Unknown format")
    
    @staticmethod
    def validate_export_options(format: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean export options"""
        manager = ExportManager()
        valid_options = manager.get_export_options(format)
        
        cleaned_options = {}
        for key, value in options.items():
            if key in valid_options:
                option_def = valid_options[key]
                try:
                    if option_def["type"] == "int":
                        cleaned_value = int(value)
                        if "min" in option_def:
                            cleaned_value = max(cleaned_value, option_def["min"])
                        if "max" in option_def:
                            cleaned_value = min(cleaned_value, option_def["max"])
                        cleaned_options[key] = cleaned_value
                    elif option_def["type"] == "bool":
                        cleaned_options[key] = bool(value)
                    elif option_def["type"] == "choice":
                        if value in option_def["choices"]:
                            cleaned_options[key] = value
                        else:
                            cleaned_options[key] = option_def["default"]
                    else:
                        cleaned_options[key] = str(value)
                except (ValueError, TypeError):
                    cleaned_options[key] = option_def["default"]
        
        return cleaned_options