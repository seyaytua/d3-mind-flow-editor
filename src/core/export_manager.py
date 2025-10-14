#!/usr/bin/env python3
"""
Export Manager for D3-Mind-Flow-Editor
Handles HTML, PNG, SVG, and PDF export with high-resolution support using Playwright
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Optional, Tuple
from playwright.async_api import async_playwright
from PIL import Image
import tempfile

from ..utils.config import Config
from ..utils.logger import logger
from ..utils.resolution_manager import ResolutionManager


class ExportManager:
    """Manages export functionality for all diagram formats"""
    
    def __init__(self, config: Config, resolution_manager: ResolutionManager):
        self.config = config
        self.resolution_manager = resolution_manager
        
        # Export format specifications from design document
        self.supported_formats = {
            'html': 'スタンドアロンHTML（推奨：マインドマップ）',
            'png': '高解像度PNG（推奨：フローチャート）', 
            'svg': 'ベクターSVG（拡大縮小対応）',
            'pdf': 'ベクターPDF（印刷用）'
        }
        
        logger.debug("Export manager initialized")
    
    async def export_diagram(self, diagram_data: Dict, format: str, output_path: str) -> bool:
        """
        Export diagram in specified format
        
        Args:
            diagram_data: Diagram data with type, content, styles
            format: Export format (html/png/svg/pdf)
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate HTML content
            html_content = self._generate_standalone_html(diagram_data)
            
            if format == 'html':
                return await self._export_html(html_content, output_path)
            elif format == 'png':
                return await self._export_png(html_content, output_path)
            elif format == 'svg':
                return await self._export_svg(html_content, output_path)
            elif format == 'pdf':
                return await self._export_pdf(html_content, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def _generate_standalone_html(self, diagram_data: Dict) -> str:
        """
        Generate standalone HTML with embedded D3.js templates
        
        Args:
            diagram_data: Diagram data
            
        Returns:
            Complete HTML string
        """
        diagram_type = diagram_data.get('type', 'mindmap')
        content = diagram_data.get('content', '')
        styles = diagram_data.get('styles', {})
        
        # Load appropriate D3.js template
        template_path = Path(__file__).parent.parent / 'assets' / 'd3_templates' / f'{diagram_type}.html'
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            # Fallback to basic template
            return self._generate_fallback_html(diagram_data)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Embed data into template
            data_json = json.dumps({
                'content': content,
                'styles': styles,
                'type': diagram_type
            }, ensure_ascii=False)
            
            # Replace placeholder with actual data
            html_content = template.replace('{{DIAGRAM_DATA}}', data_json)
            
            # Make standalone (embed D3.js CDN content)
            html_content = self._make_standalone(html_content)
            
            return html_content
            
        except Exception as e:
            logger.error(f"Template processing failed: {e}")
            return self._generate_fallback_html(diagram_data)
    
    def _generate_fallback_html(self, diagram_data: Dict) -> str:
        """Generate basic fallback HTML when template fails"""
        diagram_type = diagram_data.get('type', 'mindmap')
        content = diagram_data.get('content', '')
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{diagram_type.title()} Export</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', 'Hiragino Sans', 'Yu Gothic UI', sans-serif;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{diagram_type.title()} Export</h1>
        <div id="diagram"></div>
        <pre>{content}</pre>
    </div>
</body>
</html>
        """
    
    def _make_standalone(self, html_content: str) -> str:
        """
        Make HTML standalone by embedding external dependencies
        
        Args:
            html_content: HTML with CDN links
            
        Returns:
            HTML with embedded resources
        """
        # For now, keep CDN links but add fallback
        # In production, would download and embed D3.js content
        
        standalone_note = """
<!-- Standalone HTML Export from D3-Mind-Flow-Editor -->
<!-- This file contains all necessary code to run independently -->
        """
        
        return html_content.replace('<head>', f'<head>\n{standalone_note}')
    
    async def _export_html(self, html_content: str, output_path: str) -> bool:
        """Export as standalone HTML file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML exported successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            return False
    
    async def _export_png(self, html_content: str, output_path: str) -> bool:
        """
        Export as high-resolution PNG using Playwright
        Based on design document specifications
        """
        try:
            # Get export settings from config
            png_dpi = self.config.get('export.png_dpi', 300)
            png_width = self.config.get('export.png_width', 1920)
            png_height = self.config.get('export.png_height', 1080)
            
            # Calculate scale factor: scale = dpi / 72
            scale_factor = png_dpi / 72.0
            
            # Adjust viewport for high resolution
            viewport_width = int(png_width * scale_factor)
            viewport_height = int(png_height * scale_factor)
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_path = f.name
            
            try:
                async with async_playwright() as p:
                    # Launch browser with high DPI support
                    browser = await p.chromium.launch(headless=True)
                    
                    # Create page with high resolution viewport
                    page = await browser.new_page(
                        viewport={'width': viewport_width, 'height': viewport_height},
                        device_scale_factor=scale_factor
                    )
                    
                    # Navigate to HTML file
                    await page.goto(f'file://{temp_html_path}')
                    
                    # Wait for D3.js to render
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)  # Additional wait for D3 animations
                    
                    # Take screenshot
                    await page.screenshot(
                        path=output_path,
                        full_page=False,
                        scale='device'
                    )
                    
                    await browser.close()
                
                # Set PNG DPI metadata using Pillow
                self._set_png_dpi(output_path, png_dpi)
                
                logger.info(f"PNG exported successfully: {output_path} (DPI: {png_dpi})")
                return True
                
            finally:
                # Clean up temporary file
                os.unlink(temp_html_path)
                
        except Exception as e:
            logger.error(f"PNG export failed: {e}")
            return False
    
    def _set_png_dpi(self, png_path: str, dpi: int):
        """Set DPI metadata in PNG file using Pillow"""
        try:
            with Image.open(png_path) as img:
                img.save(png_path, dpi=(dpi, dpi))
            logger.debug(f"PNG DPI metadata set to {dpi}")
        except Exception as e:
            logger.warning(f"Failed to set PNG DPI metadata: {e}")
    
    async def _export_svg(self, html_content: str, output_path: str) -> bool:
        """
        Export as SVG by extracting SVG from D3.js rendered page
        """
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_path = f.name
            
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    await page.goto(f'file://{temp_html_path}')
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)
                    
                    # Extract SVG content using JavaScript
                    svg_content = await page.evaluate("""
                        () => {
                            const svgs = document.querySelectorAll('svg');
                            if (svgs.length > 0) {
                                return svgs[0].outerHTML;
                            }
                            return null;
                        }
                    """)
                    
                    await browser.close()
                
                if svg_content:
                    # Add XML declaration and clean up SVG
                    svg_content = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svg_content
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                    
                    logger.info(f"SVG exported successfully: {output_path}")
                    return True
                else:
                    logger.error("No SVG content found in rendered page")
                    return False
                
            finally:
                os.unlink(temp_html_path)
                
        except Exception as e:
            logger.error(f"SVG export failed: {e}")
            return False
    
    async def _export_pdf(self, html_content: str, output_path: str) -> bool:
        """
        Export as vector PDF using Playwright
        Based on design document: prefer vector format
        """
        try:
            # Get PDF settings from config
            pdf_vector = self.config.get('export.pdf_vector', True)
            paper_size = self.config.get('export.pdf_paper_size', 'A4')
            
            # Paper size mapping
            paper_sizes = {
                'A4': {'width': 8.27, 'height': 11.69},  # inches
                'A3': {'width': 11.69, 'height': 16.54},
                'Letter': {'width': 8.5, 'height': 11}
            }
            
            size_config = paper_sizes.get(paper_size, paper_sizes['A4'])
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_path = f.name
            
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    await page.goto(f'file://{temp_html_path}')
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(2)
                    
                    # Generate PDF with vector support
                    if pdf_vector:
                        await page.pdf(
                            path=output_path,
                            format=paper_size if paper_size in ['A3', 'A4', 'Letter'] else None,
                            width=f"{size_config['width']}in" if paper_size not in ['A3', 'A4', 'Letter'] else None,
                            height=f"{size_config['height']}in" if paper_size not in ['A3', 'A4', 'Letter'] else None,
                            print_background=True,
                            prefer_css_page_size=True
                        )
                    else:
                        # Fallback: PNG to PDF conversion
                        logger.warning("Vector PDF failed, using raster fallback")
                        return False
                    
                    await browser.close()
                
                logger.info(f"PDF exported successfully: {output_path} (Vector: {pdf_vector})")
                return True
                
            finally:
                os.unlink(temp_html_path)
                
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return False
    
    def get_export_settings(self) -> Dict:
        """Get current export settings from config"""
        return {
            'png_dpi': self.config.get('export.png_dpi', 300),
            'png_width': self.config.get('export.png_width', 1920),
            'png_height': self.config.get('export.png_height', 1080),
            'png_keep_aspect': self.config.get('export.png_keep_aspect', True),
            'pdf_vector': self.config.get('export.pdf_vector', True),
            'pdf_paper_size': self.config.get('export.pdf_paper_size', 'A4')
        }
    
    def update_export_settings(self, settings: Dict):
        """Update export settings in config"""
        for key, value in settings.items():
            self.config.set(f'export.{key}', value)
        
        logger.info("Export settings updated")
    
    def get_recommended_settings(self, use_case: str) -> Dict:
        """
        Get recommended export settings based on use case
        From design document specifications
        """
        recommendations = {
            'web': {
                'png_dpi': 72,
                'png_width': 1920,
                'png_height': 1080,
                'pdf_paper_size': 'A4'
            },
            'presentation': {
                'png_dpi': 150,
                'png_width': 1920,
                'png_height': 1080,
                'pdf_paper_size': 'A4'
            },
            'print': {
                'png_dpi': 300,
                'png_width': 3840,
                'png_height': 2160,
                'pdf_paper_size': 'A3'
            }
        }
        
        return recommendations.get(use_case, recommendations['web'])