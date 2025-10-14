#!/usr/bin/env python3
"""
Preview panel for D3-Mind-Flow-Editor
Streamlined version using D3Generator templates
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

import json
from ..database.models import DiagramType
from ..utils.config import Config
from ..utils.logger import logger
from ..utils.resolution_manager import ResolutionManager


class PreviewPanel(QWidget):
    """Preview panel for diagram visualization"""
    
    # Signals
    error_occurred = Signal(str)
    
    def __init__(self, config: Config, resolution_manager: ResolutionManager):
        super().__init__()
        
        self.config = config
        self.resolution_manager = resolution_manager
        
        # Current content
        self.current_content = ""
        self.current_type = DiagramType.MINDMAP
        
        # Loading timer
        self.loading_timer = QTimer()
        self.loading_timer.setSingleShot(True)
        self.loading_timer.timeout.connect(self._loading_timeout)
        
        self._setup_ui()
        self._setup_web_view()
        
        logger.debug("Preview panel initialized")
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        self.title_label = QLabel("プレビュー")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Control buttons
        self.refresh_button = QPushButton("🔄 更新")
        self.refresh_button.setToolTip("プレビューを更新")
        header_layout.addWidget(self.refresh_button)
        
        self.zoom_in_button = QPushButton("🔍+")
        self.zoom_in_button.setToolTip("ズームイン")
        header_layout.addWidget(self.zoom_in_button)
        
        self.zoom_out_button = QPushButton("🔍-")
        self.zoom_out_button.setToolTip("ズームアウト")
        header_layout.addWidget(self.zoom_out_button)
        
        self.zoom_reset_button = QPushButton("⟲")
        self.zoom_reset_button.setToolTip("ズームリセット")
        header_layout.addWidget(self.zoom_reset_button)
        
        layout.addLayout(header_layout)
        
        # Progress bar for loading indication
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Web view for D3.js rendering
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(300)
        layout.addWidget(self.web_view)
        
        # Status label
        self.status_label = QLabel("プレビュー準備完了")
        self.status_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Button connections
        self.refresh_button.clicked.connect(self._refresh_preview)
        self.zoom_in_button.clicked.connect(lambda: self._zoom(1.2))
        self.zoom_out_button.clicked.connect(lambda: self._zoom(0.8))
        self.zoom_reset_button.clicked.connect(self._reset_zoom)
        
        # Web view connections
        self.web_view.loadStarted.connect(self._on_load_started)
        self.web_view.loadFinished.connect(self._on_load_finished)
    
    def _setup_web_view(self):
        """Setup web view settings"""
        settings = self.web_view.settings()
        
        # Enable JavaScript and other features
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        
        # Enable developer tools in debug mode (check if attribute exists for compatibility)
        if logger.get_logger().level <= 10:  # DEBUG level
            try:
                # Try different possible attribute names for developer tools
                if hasattr(QWebEngineSettings, 'DeveloperExtrasEnabled'):
                    settings.setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
                elif hasattr(QWebEngineSettings, 'WebAttribute') and hasattr(QWebEngineSettings.WebAttribute, 'DeveloperExtrasEnabled'):
                    settings.setAttribute(QWebEngineSettings.WebAttribute.DeveloperExtrasEnabled, True)
                else:
                    logger.debug("Developer tools setting not available in this PySide6 version")
            except AttributeError as e:
                logger.debug(f"Developer tools setting failed: {e}")
        
        # Set zoom factor based on display settings
        zoom_factor = self.resolution_manager.get_scaling_factor()
        self.web_view.setZoomFactor(zoom_factor)
        
        logger.debug(f"Web view configured with zoom factor: {zoom_factor}")
    
    def update_content(self, content: str, diagram_type: str):
        """Update preview with new content
        
        Args:
            content: Diagram content (Mermaid/CSV)
            diagram_type: Type of diagram
        """
        self.current_content = content
        self.current_type = diagram_type
        
        if not content.strip():
            self.clear()
            return
        
        self._show_loading()
        
        try:
            # Generate HTML for preview
            html_content = self._generate_preview_html(content, diagram_type)
            
            # Load HTML in web view
            self.web_view.setHtml(html_content, QUrl("file://"))
            
            # Update status
            diagram_name = DiagramType.display_names().get(diagram_type, diagram_type)
            self.status_label.setText(f"プレビュー更新中: {diagram_name}")
            
            # Start loading timeout
            self.loading_timer.start(10000)  # 10 second timeout
            
        except Exception as e:
            error_msg = f"プレビュー生成エラー: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self._hide_loading()
    
    def _generate_preview_html(self, content: str, diagram_type: str) -> str:
        """Generate HTML content for preview using D3Generator
        
        Args:
            content: Diagram data
            diagram_type: Type of diagram
            
        Returns:
            HTML content string
        """
        try:
            # Import D3Generator
            from ..core.d3_generator import D3Generator
            
            # Create generator instance
            generator = D3Generator()
            
            # Generate HTML using the complete D3 templates
            html_content = generator.generate_html(
                content=content,
                diagram_type=diagram_type,
                standalone=False,  # For preview, not standalone
                title=f"{DiagramType.display_names().get(diagram_type, diagram_type)} Preview"
            )
            
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to generate preview HTML: {e}")
            return self._generate_error_html(f"プレビュー生成エラー: {e}")
    
    # Note: Old HTML generation methods (_generate_mindmap_html, _generate_flowchart_html, 
    # _generate_gantt_html) have been removed and replaced with D3Generator templates
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generate HTML for error display"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>エラー</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .error {{
            color: #d32f2f;
            text-align: center;
            margin: 50px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error">
            <h2>⚠️ プレビューエラー</h2>
            <p>{error_message}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _show_loading(self):
        """Show loading indicator"""
        self.progress_bar.setVisible(True)
        self.refresh_button.setEnabled(False)
    
    def _hide_loading(self):
        """Hide loading indicator"""
        self.progress_bar.setVisible(False)
        self.refresh_button.setEnabled(True)
        self.loading_timer.stop()
    
    def _on_load_started(self):
        """Handle web view load start"""
        logger.debug("Preview load started")
    
    def _on_load_finished(self, success: bool):
        """Handle web view load completion"""
        self._hide_loading()
        
        if success:
            self.status_label.setText("プレビュー更新完了")
            logger.debug("Preview loaded successfully")
        else:
            error_msg = "プレビューの読み込みに失敗しました"
            self.status_label.setText(error_msg)
            self.error_occurred.emit(error_msg)
            logger.error("Preview load failed")
    
    def _loading_timeout(self):
        """Handle loading timeout"""
        error_msg = "プレビューの読み込みがタイムアウトしました"
        self.status_label.setText(error_msg)
        self.error_occurred.emit(error_msg)
        self._hide_loading()
        logger.warning("Preview loading timeout")
    
    def _refresh_preview(self):
        """Refresh current preview"""
        if self.current_content:
            self.update_content(self.current_content, self.current_type)
        else:
            self.status_label.setText("更新する内容がありません")
    
    def _zoom(self, factor: float):
        """Apply zoom to web view"""
        current_zoom = self.web_view.zoomFactor()
        new_zoom = current_zoom * factor
        
        # Limit zoom range
        new_zoom = max(0.1, min(5.0, new_zoom))
        
        self.web_view.setZoomFactor(new_zoom)
        self.status_label.setText(f"ズーム: {int(new_zoom * 100)}%")
        
        logger.debug(f"Zoom changed to: {new_zoom}")
    
    def _reset_zoom(self):
        """Reset zoom to default"""
        default_zoom = self.resolution_manager.get_scaling_factor()
        self.web_view.setZoomFactor(default_zoom)
        self.status_label.setText(f"ズーム: {int(default_zoom * 100)}% (デフォルト)")
        
        logger.debug(f"Zoom reset to: {default_zoom}")
    
    def clear(self):
        """Clear preview content"""
        self.web_view.setHtml("<html><body><h2>プレビューエリア</h2><p>図を作成するには左側のパネルでデータを入力してください。</p></body></html>")
        self.current_content = ""
        self.status_label.setText("プレビュークリア完了")
        logger.debug("Preview cleared")
    
    def get_current_zoom(self) -> float:
        """Get current zoom factor"""
        return self.web_view.zoomFactor()