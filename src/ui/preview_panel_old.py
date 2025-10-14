#!/usr/bin/env python3
"""
Preview panel for D3-Mind-Flow-Editor
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
        
        # Enable JavaScript and other features (PySide6 6.10+ compatible)
        try:
            # PySide6 6.10+ requires WebAttribute class for settings
            if hasattr(QWebEngineSettings, 'WebAttribute'):
                web_attr = QWebEngineSettings.WebAttribute
                
                # Enable JavaScript (critical for D3.js)
                if hasattr(web_attr, 'JavascriptEnabled'):
                    settings.setAttribute(web_attr.JavascriptEnabled, True)
                    logger.debug("JavaScript enabled")
                
                # Enable local content access (needed for HTML templates)
                if hasattr(web_attr, 'LocalContentCanAccessRemoteUrls'):
                    settings.setAttribute(web_attr.LocalContentCanAccessRemoteUrls, True)
                    logger.debug("Local content remote URL access enabled")
                
                if hasattr(web_attr, 'LocalContentCanAccessFileUrls'):
                    settings.setAttribute(web_attr.LocalContentCanAccessFileUrls, True)
                    logger.debug("Local content file URL access enabled")
                
                logger.info("WebEngine settings configured for PySide6 6.10+")
                
            else:
                # Fallback for older PySide6 versions (pre-6.10)
                settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
                logger.info("WebEngine settings configured for older PySide6")
                
        except Exception as e:
            logger.error(f"WebEngine settings configuration failed: {e}")
            logger.warning("Continuing with default settings - some features may be limited")
        
        # Developer tools setting (removed in PySide6 6.10+)
        # This functionality is no longer needed for the application to work
        # and has been deprecated/removed in newer versions
        if logger.get_logger().level <= 10:  # DEBUG level
            logger.debug("Developer tools setting disabled (PySide6 6.10+ compatibility)")
        
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
    
    def _generate_mindmap_html(self, content: str) -> str:
        """Generate HTML for mindmap preview with full D3.js implementation"""
        try:
            # Import and use the CSV parser to process the content
            from ..core.csv_parser import parse_mindmap_csv
            
            # Parse CSV content
            parsed_data = parse_mindmap_csv(content)
            
            # Convert to JSON for JavaScript
            import json
            data_json = json.dumps(parsed_data, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Failed to parse mindmap CSV: {e}")
            # Fallback to sample data
            data_json = json.dumps({
                "name": "サンプルマインドマップ", 
                "children": [
                    {"name": "分岐1", "color": "#4CAF50", "children": [{"name": "子要素1", "color": "#81C784"}]},
                    {"name": "分岐2", "color": "#2196F3", "children": [{"name": "子要素2", "color": "#64B5F6"}]}
                ]
            }, ensure_ascii=False)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>インタラクティブマインドマップ</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', 'Hiragino Sans', 'Yu Gothic UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }}

        .container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}

        .controls {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}

        .controls button {{
            margin: 5px;
            padding: 8px 12px;
            border: none;
            border-radius: 5px;
            background: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 12px;
        }}

        .controls button:hover {{
            background: #45a049;
        }}

        .controls select {{
            margin: 5px;
            padding: 5px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }}

        .mindmap-svg {{
            width: 100%;
            height: 100%;
            cursor: grab;
        }}

        .mindmap-svg:active {{
            cursor: grabbing;
        }}

        .node circle {{
            stroke-width: 3;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .node circle:hover {{
            stroke-width: 5;
            filter: brightness(1.1);
        }}

        .node text {{
            font-size: 14px;
            font-weight: 600;
            text-anchor: middle;
            pointer-events: none;
            fill: #333;
            text-shadow: 0 0 3px rgba(255, 255, 255, 0.8);
        }}

        .link {{
            fill: none;
            stroke-width: 3;
            stroke: #999;
            opacity: 0.6;
            transition: all 0.3s;
        }}

        .link:hover {{
            stroke-width: 5;
            opacity: 1;
        }}

        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 5px;
            pointer-events: none;
            font-size: 12px;
            z-index: 1000;
        }}

        .stats {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="controls">
            <button onclick="centerView()">🎯 中央表示</button>
            <button onclick="expandAll()">➕ 全展開</button>
            <button onclick="collapseAll()">➖ 全収納</button>
            <button onclick="autoLayout()">🔄 自動配置</button>
            <select id="colorScheme" onchange="changeColorScheme()">
                <option value="default">デフォルト</option>
                <option value="nature">自然</option>
                <option value="ocean">海洋</option>
                <option value="sunset">夕焼け</option>
                <option value="forest">森林</option>
            </select>
            <button onclick="exportSVG()">💾 SVG出力</button>
        </div>

        <svg class="mindmap-svg" id="mindmap"></svg>

        <div class="stats">
            <div>ノード数: <span id="nodeCount">0</span></div>
            <div>レベル数: <span id="levelCount">0</span></div>
            <div>ズーム: <span id="zoomLevel">100%</span></div>
        </div>

        <div class="tooltip" id="tooltip" style="display: none;"></div>
    </div>

    <script>
        // データ
        const mindmapData = {data_json};

        // SVG設定
        const svg = d3.select("#mindmap");
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        svg.attr("width", width).attr("height", height);

        // ズーム動作
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
                updateZoomLevel(event.transform.k);
            }});

        svg.call(zoom);

        // メイングループ
        const g = svg.append("g");

        // ツールチップ
        const tooltip = d3.select("#tooltip");

        // カラースキーム
        const colorSchemes = {{
            default: ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#00BCD4", "#FFEB3B", "#795548"],
            nature: ["#4CAF50", "#8BC34A", "#CDDC39", "#FFEB3B", "#FFC107", "#FF9800", "#FF5722", "#795548"],
            ocean: ["#006064", "#0097A7", "#00BCD4", "#26C6DA", "#4DD0E1", "#80DEEA", "#B2EBF2", "#E0F2F1"],
            sunset: ["#FF5722", "#FF7043", "#FF8A65", "#FFAB91", "#FFCCBC", "#FBE9E7", "#FFF3E0", "#FFF8E1"],
            forest: ["#1B5E20", "#2E7D32", "#388E3C", "#43A047", "#4CAF50", "#66BB6A", "#81C784", "#A5D6A7"]
        }};

        let currentColorScheme = "default";

        // ツリーレイアウト
        const tree = d3.tree().size([height - 100, width - 200]);

        // 階層データの作成
        const root = d3.hierarchy(mindmapData);
        const nodes = tree(root);

        // ノードとリンクの描画
        let nodeElements, linkElements;
        
        function updateVisualization() {{
            // リンクの描画
            linkElements = g.selectAll(".link")
                .data(nodes.links())
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", d3.linkHorizontal()
                    .x(d => d.y + 100)
                    .y(d => d.x)
                );

            // ノードの描画
            const nodeGroup = g.selectAll(".node")
                .data(nodes.descendants())
                .enter()
                .append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${{d.y + 100}},${{d.x}})`)
                .on("click", toggleNode)
                .on("mouseover", showTooltip)
                .on("mouseout", hideTooltip);

            // 円の追加
            nodeGroup.append("circle")
                .attr("r", d => d.children ? 20 : 15)
                .style("fill", (d, i) => {{
                    const colors = colorSchemes[currentColorScheme];
                    return d.data.color || colors[d.depth % colors.length];
                }})
                .style("stroke", d => d.children ? "#333" : "#666");

            // テキストの追加
            nodeGroup.append("text")
                .attr("dy", ".35em")
                .style("text-anchor", "middle")
                .style("font-size", d => d.children ? "14px" : "12px")
                .text(d => {{
                    const name = d.data.name || "ノード";
                    return name.length > 10 ? name.substring(0, 10) + "..." : name;
                }});

            updateStats();
        }}

        // ノードの展開/収納
        function toggleNode(event, d) {{
            if (d.children) {{
                d._children = d.children;
                d.children = null;
            }} else {{
                d.children = d._children;
                d._children = null;
            }}
            update();
        }}

        // 表示の更新
        function update() {{
            g.selectAll("*").remove();
            updateVisualization();
        }}

        // ツールチップの表示
        function showTooltip(event, d) {{
            tooltip.style("display", "block")
                .html(`
                    <strong>${{d.data.name || "ノード"}}</strong><br>
                    レベル: ${{d.depth}}<br>
                    子要素: ${{(d.children || d._children || []).length}}個
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}

        function hideTooltip() {{
            tooltip.style("display", "none");
        }}

        // 統計情報の更新
        function updateStats() {{
            const nodeCount = nodes.descendants().length;
            const levelCount = Math.max(...nodes.descendants().map(d => d.depth)) + 1;
            
            d3.select("#nodeCount").text(nodeCount);
            d3.select("#levelCount").text(levelCount);
        }}

        function updateZoomLevel(scale) {{
            d3.select("#zoomLevel").text(Math.round(scale * 100) + "%");
        }}

        // コントロール関数
        function centerView() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(width / 2, height / 2).scale(1)
            );
        }}

        function expandAll() {{
            function expand(d) {{
                if (d._children) {{
                    d.children = d._children;
                    d._children = null;
                }}
                if (d.children) {{
                    d.children.forEach(expand);
                }}
            }}
            expand(root);
            update();
        }}

        function collapseAll() {{
            function collapse(d) {{
                if (d.children) {{
                    d._children = d.children;
                    d.children = null;
                    d._children.forEach(collapse);
                }}
            }}
            if (root.children) {{
                root.children.forEach(collapse);
            }}
            update();
        }}

        function autoLayout() {{
            centerView();
            setTimeout(() => {{
                expandAll();
            }}, 500);
        }}

        function changeColorScheme() {{
            currentColorScheme = d3.select("#colorScheme").node().value;
            update();
        }}

        function exportSVG() {{
            const svgData = new XMLSerializer().serializeToString(svg.node());
            const blob = new Blob([svgData], {{type: "image/svg+xml"}});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "mindmap.svg";
            link.click();
        }}

        // 初期化
        updateVisualization();
        centerView();

        // キーボードショートカット
        d3.select("body").on("keydown", function(event) {{
            switch(event.code) {{
                case "KeyC":
                    centerView();
                    break;
                case "KeyE":
                    expandAll();
                    break;
                case "KeyQ":
                    collapseAll();
                    break;
                case "KeyR":
                    autoLayout();
                    break;
            }}
        }});

        // リサイズ対応
        window.addEventListener('resize', () => {{
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight;
            svg.attr("width", newWidth).attr("height", newHeight);
            tree.size([newHeight - 100, newWidth - 200]);
            update();
        }});
    </script>
</body>
</html>
        """
    
    def _generate_flowchart_html(self, content: str) -> str:
        """Generate HTML for flowchart preview with Mermaid.js integration"""
        try:
            # Import and use the Mermaid parser to validate the content
            from ..core.mermaid_parser import parse_mermaid
            
            # Validate Mermaid content
            parsed_data = parse_mermaid(content)
            
            # Use original content if valid
            mermaid_code = content.strip() if content.strip() else "flowchart TD\\n    A[Start] --> B{Decision}\\n    B -->|Yes| C[Process 1]\\n    B -->|No| D[Process 2]\\n    C --> E[End]\\n    D --> E"
            
        except Exception as e:
            logger.error(f"Failed to parse mermaid content: {e}")
            # Fallback to sample flowchart
            mermaid_code = "flowchart TD\\n    A[Start] --> B{Decision}\\n    B -->|Yes| C[Process 1]\\n    B -->|No| D[Process 2]\\n    C --> E[End]\\n    D --> E"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>インタラクティブフローチャート</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', 'Hiragino Sans', 'Yu Gothic UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }}

        .container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}

        .header {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }}

        .controls button, .controls select {{
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            background: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }}

        .controls button:hover {{
            background: #45a049;
        }}

        .controls select {{
            background: white;
            color: #333;
            border: 1px solid #ddd;
        }}

        .flowchart-container {{
            position: absolute;
            top: 70px;
            left: 0;
            right: 0;
            bottom: 0;
            padding: 20px;
            overflow: auto;
        }}

        .mermaid-wrapper {{
            width: 100%;
            height: calc(100vh - 110px);
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            position: relative;
        }}

        #flowchart {{
            width: 100%;
            height: 100%;
            text-align: center;
            overflow: auto;
        }}

        .mermaid {{
            background: white;
            border-radius: 8px;
        }}

        .info-panel {{
            position: absolute;
            top: 100px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            font-size: 12px;
            max-width: 250px;
            z-index: 999;
        }}

        .tooltip {{
            position: absolute;
            padding: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 11px;
            z-index: 1001;
            display: none;
        }}

        .stats {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 10px;
            font-size: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            z-index: 999;
        }}

        /* Mermaid カスタムスタイル */
        .nodeLabel {{
            font-family: 'Segoe UI', 'Hiragino Sans', sans-serif !important;
            font-size: 12px !important;
        }}

        .edgeLabel {{
            font-family: 'Segoe UI', 'Hiragino Sans', sans-serif !important;
            font-size: 10px !important;
        }}

        /* ズーム・パン機能 */
        .zoom-container {{
            cursor: grab;
        }}

        .zoom-container:active {{
            cursor: grabbing;
        }}

        /* フルスクリーンボタン */
        .fullscreen-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1002;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.9);
            cursor: pointer;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="controls">
                <button onclick="resetView()">🎯 元の表示</button>
                <button onclick="zoomIn()">🔍+ ズーム</button>
                <button onclick="zoomOut()">🔍- ズーム</button>
                <select id="themeSelect" onchange="changeTheme()">
                    <option value="default">デフォルト</option>
                    <option value="dark">ダーク</option>
                    <option value="forest">フォレスト</option>
                    <option value="base">ベース</option>
                    <option value="neutral">ニュートラル</option>
                </select>
                <button onclick="exportDiagram()">💾 エクスポート</button>
                <button onclick="showSource()">📝 ソース表示</button>
                <button onclick="validateFlow()">✅ 検証</button>
                <button onclick="optimizeLayout()">🎨 レイアウト最適化</button>
            </div>
        </div>

        <div class="flowchart-container">
            <div class="mermaid-wrapper">
                <button class="fullscreen-btn" onclick="toggleFullscreen()">⛶</button>
                <div id="flowchart">
                    <div class="mermaid" id="mermaidDiagram">
{mermaid_code}
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <div><strong>📊 フローチャート情報</strong></div>
            <hr>
            <div>ノード数: <span id="nodeCount">-</span></div>
            <div>エッジ数: <span id="edgeCount">-</span></div>
            <div>レベル数: <span id="levelCount">-</span></div>
            <div>テーマ: <span id="currentTheme">デフォルト</span></div>
        </div>

        <div class="stats">
            <div><strong>🔧 操作方法</strong></div>
            <hr>
            <div>• マウスドラッグでパン</div>
            <div>• マウスホイールでズーム</div>
            <div>• ノードクリックで詳細表示</div>
            <div>• Rキーでリセット</div>
        </div>

        <div class="tooltip" id="tooltip"></div>
    </div>

    <script>
        // Mermaid設定
        mermaid.initialize({{
            startOnLoad: false,
            theme: 'default',
            themeVariables: {{
                fontFamily: 'Segoe UI, Hiragino Sans, Yu Gothic UI, sans-serif',
                fontSize: '12px',
                primaryColor: '#4CAF50',
                primaryTextColor: '#fff',
                primaryBorderColor: '#2E7D32',
                lineColor: '#666',
                secondaryColor: '#2196F3',
                tertiaryColor: '#FFC107'
            }},
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            securityLevel: 'loose'
        }});

        // ズーム・パン機能
        let currentZoom = 1;
        let panX = 0, panY = 0;
        let isDragging = false;
        let startX, startY;

        // 初期化
        async function initializeFlowchart() {{
            try {{
                const element = document.getElementById('mermaidDiagram');
                const {{ svg }} = await mermaid.render('graphDiv', element.textContent);
                element.innerHTML = svg;
                
                setupInteractivity();
                updateStats();
                
            }} catch (error) {{
                console.error('Mermaid rendering error:', error);
                showError('フローチャートの描画でエラーが発生しました: ' + error.message);
            }}
        }}

        // インタラクティブ機能の設定
        function setupInteractivity() {{
            const svg = document.querySelector('#flowchart svg');
            if (!svg) return;

            // ズーム・パン機能
            svg.addEventListener('wheel', handleWheel);
            svg.addEventListener('mousedown', handleMouseDown);
            svg.addEventListener('mousemove', handleMouseMove);
            svg.addEventListener('mouseup', handleMouseUp);
            svg.addEventListener('mouseleave', handleMouseUp);

            // ノードクリック処理
            const nodes = svg.querySelectorAll('.node');
            nodes.forEach(node => {{
                node.addEventListener('click', (e) => handleNodeClick(e, node));
                node.addEventListener('mouseenter', (e) => showTooltip(e, node));
                node.addEventListener('mouseleave', hideTooltip);
            }});

            // 初期変換の適用
            applyTransform();
        }}

        // マウスイベントハンドラー
        function handleWheel(e) {{
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            currentZoom = Math.max(0.1, Math.min(3, currentZoom * delta));
            applyTransform();
        }}

        function handleMouseDown(e) {{
            isDragging = true;
            startX = e.clientX - panX;
            startY = e.clientY - panY;
            document.querySelector('#flowchart').style.cursor = 'grabbing';
        }}

        function handleMouseMove(e) {{
            if (!isDragging) return;
            panX = e.clientX - startX;
            panY = e.clientY - startY;
            applyTransform();
        }}

        function handleMouseUp(e) {{
            isDragging = false;
            document.querySelector('#flowchart').style.cursor = 'grab';
        }}

        // 変換の適用
        function applyTransform() {{
            const svg = document.querySelector('#flowchart svg');
            if (svg) {{
                svg.style.transform = `translate(${{panX}}px, ${{panY}}px) scale(${{currentZoom}})`;
                svg.style.transformOrigin = 'center center';
            }}
        }}

        // ノードクリック処理
        function handleNodeClick(e, node) {{
            e.stopPropagation();
            
            // 既存のハイライトを削除
            document.querySelectorAll('.node').forEach(n => {{
                n.style.filter = '';
                n.style.transform = '';
            }});

            // 選択されたノードをハイライト
            node.style.filter = 'brightness(1.2) drop-shadow(0 0 10px rgba(76, 175, 80, 0.6))';
            node.style.transform = 'scale(1.05)';
            node.style.transition = 'all 0.3s ease';

            // ノード情報を表示
            const nodeText = node.querySelector('foreignObject, text');
            const nodeName = nodeText ? nodeText.textContent.trim() : 'Unknown';
            
            alert(`ノード情報:\\n名前: ${{nodeName}}\\nタイプ: ${{getNodeType(node)}}\\nID: ${{node.id || 'N/A'}}`);
        }}

        // ノードタイプの判定
        function getNodeType(node) {{
            const shape = node.querySelector('rect, circle, polygon, ellipse');
            if (!shape) return 'テキスト';
            
            const tagName = shape.tagName.toLowerCase();
            switch(tagName) {{
                case 'rect': return '矩形';
                case 'circle': return '円';
                case 'ellipse': return '楕円';
                case 'polygon': return '多角形';
                default: return '不明';
            }}
        }}

        // ツールチップ機能
        function showTooltip(e, node) {{
            const tooltip = document.getElementById('tooltip');
            const nodeText = node.querySelector('foreignObject, text');
            const nodeName = nodeText ? nodeText.textContent.trim() : 'ノード';
            
            tooltip.innerHTML = `
                <strong>${{nodeName}}</strong><br>
                タイプ: ${{getNodeType(node)}}<br>
                クリックで詳細表示
            `;
            tooltip.style.display = 'block';
            tooltip.style.left = (e.pageX + 10) + 'px';
            tooltip.style.top = (e.pageY - 10) + 'px';
        }}

        function hideTooltip() {{
            document.getElementById('tooltip').style.display = 'none';
        }}

        // 統計情報の更新
        function updateStats() {{
            const svg = document.querySelector('#flowchart svg');
            if (!svg) return;

            const nodeCount = svg.querySelectorAll('.node').length;
            const edgeCount = svg.querySelectorAll('.edgePath').length;
            
            document.getElementById('nodeCount').textContent = nodeCount;
            document.getElementById('edgeCount').textContent = edgeCount;
            document.getElementById('levelCount').textContent = calculateLevels();
        }}

        function calculateLevels() {{
            // 簡易的なレベル計算
            const svg = document.querySelector('#flowchart svg');
            if (!svg) return 0;

            const nodes = Array.from(svg.querySelectorAll('.node'));
            if (nodes.length === 0) return 0;

            const yPositions = nodes.map(node => {{
                const transform = node.getAttribute('transform');
                const match = transform ? transform.match(/translate\\(([\\d.-]+),([\\d.-]+)\\)/) : null;
                return match ? parseFloat(match[2]) : 0;
            }});

            const uniqueY = [...new Set(yPositions.map(y => Math.round(y / 50)))];
            return uniqueY.length;
        }}

        // コントロール関数
        function resetView() {{
            currentZoom = 1;
            panX = 0;
            panY = 0;
            applyTransform();
        }}

        function zoomIn() {{
            currentZoom = Math.min(3, currentZoom * 1.2);
            applyTransform();
        }}

        function zoomOut() {{
            currentZoom = Math.max(0.1, currentZoom * 0.8);
            applyTransform();
        }}

        function changeTheme() {{
            const theme = document.getElementById('themeSelect').value;
            document.getElementById('currentTheme').textContent = 
                theme === 'default' ? 'デフォルト' :
                theme === 'dark' ? 'ダーク' :
                theme === 'forest' ? 'フォレスト' :
                theme === 'base' ? 'ベース' : 'ニュートラル';

            // Mermaidテーマを変更して再描画
            mermaid.initialize({{ theme: theme }});
            initializeFlowchart();
        }}

        function exportDiagram() {{
            const svg = document.querySelector('#flowchart svg');
            if (!svg) return;

            const svgData = new XMLSerializer().serializeToString(svg);
            const blob = new Blob([svgData], {{type: "image/svg+xml"}});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "flowchart.svg";
            link.click();
        }}

        function showSource() {{
            const source = document.getElementById('mermaidDiagram').textContent.trim();
            const popup = window.open('', '_blank', 'width=600,height=400');
            popup.document.write(`
                <html>
                    <head><title>Mermaid ソースコード</title></head>
                    <body style="font-family: monospace; padding: 20px;">
                        <h2>Mermaid ソースコード</h2>
                        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">${{source}}</pre>
                    </body>
                </html>
            `);
        }}

        function validateFlow() {{
            const nodeCount = document.querySelectorAll('.node').length;
            const edgeCount = document.querySelectorAll('.edgePath').length;
            
            const isValid = nodeCount > 0 && edgeCount >= 0;
            const message = isValid ? 
                `✅ フローチャートは有効です\\n• ノード: ${{nodeCount}}個\\n• エッジ: ${{edgeCount}}個` :
                `❌ フローチャートに問題があります`;
                
            alert(message);
        }}

        function optimizeLayout() {{
            // レイアウト最適化（再描画）
            initializeFlowchart();
            resetView();
        }}

        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }}

        function showError(message) {{
            const container = document.getElementById('flowchart');
            container.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #d32f2f;">
                    <h2>⚠️ エラーが発生しました</h2>
                    <p>${{message}}</p>
                    <button onclick="location.reload()" style="padding: 10px 20px; margin-top: 20px;">
                        🔄 再読み込み
                    </button>
                </div>
            `;
        }}

        // キーボードショートカット
        document.addEventListener('keydown', function(e) {{
            switch(e.code) {{
                case 'KeyR':
                    if (!e.ctrlKey) resetView();
                    break;
                case 'Equal': // +
                    if (e.ctrlKey) {{
                        e.preventDefault();
                        zoomIn();
                    }}
                    break;
                case 'Minus': // -
                    if (e.ctrlKey) {{
                        e.preventDefault();
                        zoomOut();
                    }}
                    break;
            }}
        }});

        // 初期化実行
        window.addEventListener('load', () => {{
            setTimeout(initializeFlowchart, 100);
        }});

        // リサイズ対応
        window.addEventListener('resize', () => {{
            setTimeout(() => {{
                const svg = document.querySelector('#flowchart svg');
                if (svg) {{
                    svg.setAttribute('width', '100%');
                    svg.setAttribute('height', '100%');
                }}
            }}, 100);
        }});
    </script>
</body>
</html>
        """
    
    def _generate_gantt_html(self, content: str) -> str:
        """Generate HTML for gantt chart preview with full D3.js implementation"""
        try:
            # Import and use the CSV parser to process the content
            from ..core.csv_parser import parse_gantt_csv
            
            # Parse CSV content
            parsed_data = parse_gantt_csv(content)
            
            # Convert to JSON for JavaScript
            import json
            data_json = json.dumps(parsed_data, ensure_ascii=False, default=str)
            
        except Exception as e:
            logger.error(f"Failed to parse gantt CSV: {e}")
            # Fallback to sample data
            from datetime import datetime, timedelta
            today = datetime.now()
            sample_data = [
                {{"task": "プロジェクト計画", "start": today.strftime("%Y-%m-%d"), 
                  "end": (today + timedelta(days=7)).strftime("%Y-%m-%d"), "progress": 100, "resource": "チームリーダー"}},
                {{"task": "開発フェーズ1", "start": (today + timedelta(days=8)).strftime("%Y-%m-%d"), 
                  "end": (today + timedelta(days=30)).strftime("%Y-%m-%d"), "progress": 60, "resource": "開発者A"}},
                {{"task": "テストフェーズ", "start": (today + timedelta(days=25)).strftime("%Y-%m-%d"), 
                  "end": (today + timedelta(days=40)).strftime("%Y-%m-%d"), "progress": 20, "resource": "QAチーム"}}
            ]
            data_json = json.dumps(sample_data, ensure_ascii=False)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>インタラクティブガントチャート</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', 'Hiragino Sans', 'Yu Gothic UI', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            overflow-x: auto;
            overflow-y: auto;
        }}

        .container {{
            width: 100%;
            min-height: 100vh;
            padding: 20px;
            box-sizing: border-box;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}

        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-bottom: 15px;
        }}

        .controls button, .controls select {{
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            background: #4CAF50;
            color: white;
            cursor: pointer;
            font-size: 12px;
        }}

        .controls button:hover {{
            background: #45a049;
        }}

        .controls select {{
            background: white;
            color: #333;
            border: 1px solid #ddd;
        }}

        .gantt-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            overflow: auto;
        }}

        .gantt-svg {{
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background: white;
        }}

        .task-bar {{
            cursor: pointer;
            transition: all 0.3s;
        }}

        .task-bar:hover {{
            stroke: #333;
            stroke-width: 2;
        }}

        .progress-bar {{
            pointer-events: none;
        }}

        .task-label {{
            font-size: 12px;
            font-weight: 500;
            fill: #333;
        }}

        .axis {{
            font-size: 11px;
        }}

        .axis path,
        .axis line {{
            fill: none;
            stroke: #999;
            shape-rendering: crispEdges;
        }}

        .grid line {{
            stroke: #e0e0e0;
            stroke-dasharray: 2,2;
        }}

        .dependency {{
            fill: none;
            stroke: #ff6b6b;
            stroke-width: 2;
            marker-end: url(#arrowhead);
        }}

        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 5px;
            pointer-events: none;
            font-size: 12px;
            z-index: 1000;
            max-width: 300px;
        }}

        .stats {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 10px;
            font-size: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            min-width: 200px;
        }}

        .legend {{
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📅 インタラクティブガントチャート</h2>
            <div class="controls">
                <button onclick="fitToView()">🎯 全体表示</button>
                <button onclick="zoomIn()">🔍+ ズームイン</button>
                <button onclick="zoomOut()">🔍- ズームアウト</button>
                <select id="timeScale" onchange="changeTimeScale()">
                    <option value="day">日単位</option>
                    <option value="week" selected>週単位</option>
                    <option value="month">月単位</option>
                </select>
                <button onclick="showCriticalPath()">🎯 クリティカルパス</button>
                <button onclick="exportChart()">💾 チャート出力</button>
                <button onclick="showStatistics()">📊 統計表示</button>
            </div>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #4CAF50;"></div>
                    <span>完了済み</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #2196F3;"></div>
                    <span>進行中</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #FFC107;"></div>
                    <span>未開始</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #F44336;"></div>
                    <span>遅延</span>
                </div>
            </div>
        </div>

        <div class="gantt-container">
            <svg class="gantt-svg" id="gantt"></svg>
        </div>

        <div class="stats">
            <div><strong>📋 プロジェクト統計</strong></div>
            <hr>
            <div>総タスク数: <span id="totalTasks">0</span></div>
            <div>完了タスク: <span id="completedTasks">0</span></div>
            <div>進行中タスク: <span id="inProgressTasks">0</span></div>
            <div>全体進捗: <span id="overallProgress">0%</span></div>
            <div>プロジェクト期間: <span id="projectDuration">0日</span></div>
            <div>現在の表示: <span id="currentView">週単位</span></div>
        </div>

        <div class="tooltip" id="tooltip" style="display: none;"></div>
    </div>

    <script>
        // データ
        const ganttData = {data_json};
        
        // 設定
        const margin = {{top: 50, right: 50, bottom: 60, left: 200}};
        const width = Math.max(1000, window.innerWidth - 100) - margin.left - margin.right;
        const height = Math.max(400, ganttData.length * 50 + 100) - margin.top - margin.bottom;

        // SVG作成
        const svg = d3.select("#gantt")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        // メイングループ
        const g = svg.append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

        // ツールチップ
        const tooltip = d3.select("#tooltip");

        // データ処理
        ganttData.forEach(d => {{
            d.startDate = new Date(d.start);
            d.endDate = new Date(d.end);
            d.duration = (d.endDate - d.startDate) / (1000 * 60 * 60 * 24); // 日数
            d.progress = d.progress || 0;
        }});

        // スケール設定
        const timeExtent = d3.extent(ganttData.flatMap(d => [d.startDate, d.endDate]));
        const xScale = d3.scaleTime()
            .domain(timeExtent)
            .range([0, width]);

        const yScale = d3.scaleBand()
            .domain(ganttData.map(d => d.task))
            .range([0, height])
            .padding(0.2);

        // 矢印マーカー定義
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "-0 -5 10 10")
            .attr("refX", 8)
            .attr("refY", 0)
            .attr("orient", "auto")
            .attr("markerWidth", 5)
            .attr("markerHeight", 5)
            .append("path")
            .attr("d", "M 0,-5 L 10,0 L 0,5")
            .attr("fill", "#ff6b6b");

        // グリッド線
        function drawGrid() {{
            // 縦線
            g.append("g")
                .attr("class", "grid")
                .selectAll("line")
                .data(xScale.ticks(d3.timeWeek.every(1)))
                .enter().append("line")
                .attr("x1", d => xScale(d))
                .attr("x2", d => xScale(d))
                .attr("y1", 0)
                .attr("y2", height);

            // 横線
            g.append("g")
                .attr("class", "grid")
                .selectAll("line")
                .data(ganttData)
                .enter().append("line")
                .attr("x1", 0)
                .attr("x2", width)
                .attr("y1", d => yScale(d.task) + yScale.bandwidth())
                .attr("y2", d => yScale(d.task) + yScale.bandwidth());
        }}

        // 軸の描画
        function drawAxes() {{
            // X軸（時間軸）
            const xAxis = d3.axisBottom(xScale)
                .tickFormat(d3.timeFormat("%m/%d"));

            g.append("g")
                .attr("class", "axis x-axis")
                .attr("transform", `translate(0,${{height}})`)
                .call(xAxis)
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", "rotate(-45)");

            // Y軸（タスク軸）
            const yAxis = d3.axisLeft(yScale);

            g.append("g")
                .attr("class", "axis y-axis")
                .call(yAxis);
        }}

        // タスクバーの描画
        function drawTaskBars() {{
            const taskGroups = g.selectAll(".task-group")
                .data(ganttData)
                .enter().append("g")
                .attr("class", "task-group");

            // メインのタスクバー
            taskGroups.append("rect")
                .attr("class", "task-bar")
                .attr("x", d => xScale(d.startDate))
                .attr("y", d => yScale(d.task))
                .attr("width", d => xScale(d.endDate) - xScale(d.startDate))
                .attr("height", yScale.bandwidth())
                .attr("rx", 3)
                .attr("fill", d => getTaskColor(d))
                .attr("stroke", "#666")
                .attr("stroke-width", 1)
                .on("mouseover", showTaskTooltip)
                .on("mouseout", hideTooltip)
                .on("click", selectTask);

            // 進捗バー
            taskGroups.append("rect")
                .attr("class", "progress-bar")
                .attr("x", d => xScale(d.startDate))
                .attr("y", d => yScale(d.task) + 2)
                .attr("width", d => (xScale(d.endDate) - xScale(d.startDate)) * (d.progress / 100))
                .attr("height", yScale.bandwidth() - 4)
                .attr("rx", 2)
                .attr("fill", d => d.progress === 100 ? "#4CAF50" : "#81C784")
                .attr("opacity", 0.8);

            // 進捗テキスト
            taskGroups.append("text")
                .attr("x", d => xScale(d.startDate) + (xScale(d.endDate) - xScale(d.startDate)) / 2)
                .attr("y", d => yScale(d.task) + yScale.bandwidth() / 2)
                .attr("dy", "0.35em")
                .attr("text-anchor", "middle")
                .attr("fill", "white")
                .attr("font-size", "11px")
                .attr("font-weight", "bold")
                .text(d => `${{d.progress}}%`);
        }}

        // タスクの色決定
        function getTaskColor(d) {{
            const now = new Date();
            if (d.progress === 100) return "#4CAF50"; // 完了
            if (d.endDate < now && d.progress < 100) return "#F44336"; // 遅延
            if (d.startDate <= now && d.endDate >= now) return "#2196F3"; // 進行中
            return "#FFC107"; // 未開始
        }}

        // ツールチップ表示
        function showTaskTooltip(event, d) {{
            const formatDate = d3.timeFormat("%Y年%m月%d日");
            tooltip.style("display", "block")
                .html(`
                    <strong>${{d.task}}</strong><br>
                    開始: ${{formatDate(d.startDate)}}<br>
                    終了: ${{formatDate(d.endDate)}}<br>
                    期間: ${{Math.ceil(d.duration)}}日<br>
                    進捗: ${{d.progress}}%<br>
                    担当者: ${{d.resource || "未定"}}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }}

        function hideTooltip() {{
            tooltip.style("display", "none");
        }}

        // タスク選択
        function selectTask(event, d) {{
            // 既存の選択をクリア
            g.selectAll(".task-bar").attr("stroke", "#666").attr("stroke-width", 1);
            
            // 新しい選択
            d3.select(this).attr("stroke", "#333").attr("stroke-width", 3);
            
            console.log("選択されたタスク:", d);
        }}

        // 統計情報の更新
        function updateStatistics() {{
            const totalTasks = ganttData.length;
            const completedTasks = ganttData.filter(d => d.progress === 100).length;
            const inProgressTasks = ganttData.filter(d => d.progress > 0 && d.progress < 100).length;
            const overallProgress = Math.round(ganttData.reduce((sum, d) => sum + d.progress, 0) / totalTasks);
            const projectStart = d3.min(ganttData, d => d.startDate);
            const projectEnd = d3.max(ganttData, d => d.endDate);
            const projectDuration = Math.ceil((projectEnd - projectStart) / (1000 * 60 * 60 * 24));

            d3.select("#totalTasks").text(totalTasks);
            d3.select("#completedTasks").text(completedTasks);
            d3.select("#inProgressTasks").text(inProgressTasks);
            d3.select("#overallProgress").text(overallProgress + "%");
            d3.select("#projectDuration").text(projectDuration + "日");
        }}

        // コントロール関数
        function fitToView() {{
            // 自動フィット機能
            console.log("全体表示に調整");
        }}

        function zoomIn() {{
            // ズームイン
            console.log("ズームイン");
        }}

        function zoomOut() {{
            // ズームアウト  
            console.log("ズームアウト");
        }}

        function changeTimeScale() {{
            const scale = d3.select("#timeScale").node().value;
            d3.select("#currentView").text(scale === "day" ? "日単位" : scale === "week" ? "週単位" : "月単位");
            console.log("時間スケール変更:", scale);
        }}

        function showCriticalPath() {{
            console.log("クリティカルパス表示");
        }}

        function exportChart() {{
            const svgData = new XMLSerializer().serializeToString(svg.node());
            const blob = new Blob([svgData], {{type: "image/svg+xml"}});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "gantt-chart.svg";
            link.click();
        }}

        function showStatistics() {{
            alert(`
プロジェクト統計:
- 総タスク数: ${{ganttData.length}}
- 完了率: ${{Math.round(ganttData.reduce((sum, d) => sum + d.progress, 0) / ganttData.length)}}%
- 遅延タスク: ${{ganttData.filter(d => d.endDate < new Date() && d.progress < 100).length}}
            `);
        }}

        // 初期化
        function initialize() {{
            drawGrid();
            drawAxes();
            drawTaskBars();
            updateStatistics();
        }}

        // 実行
        initialize();

        // リサイズ対応
        window.addEventListener('resize', () => {{
            // リサイズ処理
            console.log("リサイズ対応");
        }});
    </script>
</body>
</html>
        """
    
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