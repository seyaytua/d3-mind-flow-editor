#!/usr/bin/env python3
"""
Dialog windows for D3-Mind-Flow-Editor
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QFileDialog, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QSpinBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..utils.logger import logger


class SaveDialog(QDialog):
    """Dialog for saving diagram with title and description"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("図を保存")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Title input
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("図のタイトルを入力してください")
        form_layout.addRow("タイトル *:", self.title_edit)
        
        # Description input
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("図の説明を入力してください（任意）")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("説明:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Customize button text
        save_button = button_box.button(QDialogButtonBox.Save)
        save_button.setText("保存")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("キャンセル")
        
        layout.addWidget(button_box)
        
        # Set focus to title
        self.title_edit.setFocus()
    
    def _validate_and_accept(self):
        """Validate input and accept dialog"""
        title = self.title_edit.text().strip()
        
        if not title:
            QMessageBox.warning(self, "入力エラー", "タイトルを入力してください。")
            self.title_edit.setFocus()
            return
        
        self.accept()
    
    def get_data(self) -> tuple[str, str]:
        """Get entered data"""
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        return title, description
    
    def set_title(self, title: str):
        """Set title text"""
        self.title_edit.setText(title)
    
    def set_description(self, description: str):
        """Set description text"""
        self.description_edit.setPlainText(description)


class ExportDialog(QDialog):
    """Dialog for export settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("エクスポート設定")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.selected_format = "html"
        self.output_path = ""
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        
        # Format selection group
        format_group = QGroupBox("エクスポート形式")
        format_layout = QVBoxLayout(format_group)
        
        self.format_group = QButtonGroup()
        
        # HTML format
        self.html_radio = QRadioButton("HTML (スタンドアロン)")
        self.html_radio.setToolTip("インタラクティブなHTMLファイルとして出力")
        self.html_radio.setChecked(True)
        self.format_group.addButton(self.html_radio, 0)
        format_layout.addWidget(self.html_radio)
        
        # PNG format
        self.png_radio = QRadioButton("PNG (画像)")
        self.png_radio.setToolTip("静的な画像ファイルとして出力")
        self.format_group.addButton(self.png_radio, 1)
        format_layout.addWidget(self.png_radio)
        
        # SVG format
        self.svg_radio = QRadioButton("SVG (ベクター画像)")
        self.svg_radio.setToolTip("ベクター形式の画像ファイルとして出力")
        self.format_group.addButton(self.svg_radio, 2)
        format_layout.addWidget(self.svg_radio)
        
        # PDF format
        self.pdf_radio = QRadioButton("PDF (ドキュメント)")
        self.pdf_radio.setToolTip("PDFドキュメントとして出力")
        self.format_group.addButton(self.pdf_radio, 3)
        format_layout.addWidget(self.pdf_radio)
        
        layout.addWidget(format_group)
        
        # Quality settings group
        self.quality_group = QGroupBox("品質設定")
        quality_layout = QFormLayout(self.quality_group)
        
        # DPI setting for raster formats
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(["72 DPI (Web)", "150 DPI (高品質)", "300 DPI (印刷品質)"])
        self.dpi_combo.setCurrentIndex(2)  # Default to 300 DPI
        quality_layout.addRow("解像度 (PNG):", self.dpi_combo)
        
        # Size setting
        size_layout = QHBoxLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 7680)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix(" px")
        size_layout.addWidget(QLabel("幅:"))
        size_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 4320)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix(" px")
        size_layout.addWidget(QLabel("高さ:"))
        size_layout.addWidget(self.height_spin)
        
        size_layout.addStretch()
        quality_layout.addRow("サイズ:", size_layout)
        
        # Transparent background
        self.transparent_check = QCheckBox("透明な背景")
        self.transparent_check.setToolTip("背景を透明にする（PNG/SVG）")
        quality_layout.addRow("オプション:", self.transparent_check)
        
        layout.addWidget(self.quality_group)
        
        # Output path group
        path_group = QGroupBox("出力先")
        path_layout = QVBoxLayout(path_group)
        
        path_input_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("ファイルパスを選択してください")
        path_input_layout.addWidget(self.path_edit)
        
        self.browse_button = QPushButton("参照...")
        self.browse_button.clicked.connect(self._browse_output_path)
        path_input_layout.addWidget(self.browse_button)
        
        path_layout.addLayout(path_input_layout)
        
        layout.addWidget(path_group)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Customize button text
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("エクスポート")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setText("キャンセル")
        
        layout.addWidget(button_box)
        
        # Connect format change to update quality settings
        self.format_group.buttonClicked.connect(self._on_format_changed)
        
        # Initialize quality settings visibility
        self._on_format_changed()
    
    def _on_format_changed(self):
        """Handle format selection change"""
        checked_button = self.format_group.checkedButton()
        if not checked_button:
            return
        
        format_id = self.format_group.id(checked_button)
        
        # Update format mapping
        format_map = {0: "html", 1: "png", 2: "svg", 3: "pdf"}
        self.selected_format = format_map.get(format_id, "html")
        
        # Enable/disable quality settings based on format
        is_raster = format_id == 1  # PNG
        self.dpi_combo.setEnabled(is_raster)
        self.width_spin.setEnabled(format_id in [1, 2])  # PNG, SVG
        self.height_spin.setEnabled(format_id in [1, 2])  # PNG, SVG
        self.transparent_check.setEnabled(format_id in [1, 2])  # PNG, SVG
        
        # Update file extension in path
        self._update_file_extension()
    
    def _update_file_extension(self):
        """Update file extension based on selected format"""
        current_path = self.path_edit.text()
        
        extensions = {
            "html": ".html",
            "png": ".png",
            "svg": ".svg",
            "pdf": ".pdf"
        }
        
        new_extension = extensions.get(self.selected_format, ".html")
        
        if current_path:
            # Remove old extension and add new one
            base_path = current_path
            for ext in extensions.values():
                if base_path.endswith(ext):
                    base_path = base_path[:-len(ext)]
                    break
            
            new_path = base_path + new_extension
            self.path_edit.setText(new_path)
    
    def _browse_output_path(self):
        """Browse for output file path"""
        format_filters = {
            "html": "HTML Files (*.html)",
            "png": "PNG Images (*.png)",
            "svg": "SVG Images (*.svg)",
            "pdf": "PDF Documents (*.pdf)"
        }
        
        filter_str = format_filters.get(self.selected_format, "All Files (*)")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"{self.selected_format.upper()}ファイルを保存",
            self.path_edit.text(),
            filter_str
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def _validate_and_accept(self):
        """Validate settings and accept dialog"""
        if not self.path_edit.text().strip():
            QMessageBox.warning(self, "入力エラー", "出力先ファイルを選択してください。")
            return
        
        self.output_path = self.path_edit.text().strip()
        self.accept()
    
    def get_export_settings(self) -> tuple[str, str]:
        """Get export settings"""
        return self.selected_format, self.output_path
    
    def get_quality_settings(self) -> dict:
        """Get quality settings"""
        dpi_map = {"72 DPI (Web)": 72, "150 DPI (高品質)": 150, "300 DPI (印刷品質)": 300}
        
        return {
            "dpi": dpi_map.get(self.dpi_combo.currentText(), 300),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "transparent": self.transparent_check.isChecked()
        }


class AboutDialog(QDialog):
    """About dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("D3-Mind-Flow-Editorについて")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        
        # Application info
        app_info = QLabel("""
        <h2>D3-Mind-Flow-Editor</h2>
        <p><b>バージョン:</b> 1.0.0</p>
        <p><b>作者:</b> seyaytua</p>
        <p><b>ライセンス:</b> MIT License</p>
        """)
        app_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_info)
        
        # Description
        description = QLabel("""
        <h3>概要</h3>
        <p>D3.jsを使用したマインドマップ・フローチャート・ガントチャート作成デスクトップアプリケーション</p>
        
        <h3>主な機能</h3>
        <ul>
        <li>インタラクティブなマインドマップ作成</li>
        <li>Mermaid記法対応のフローチャート</li>
        <li>プロジェクト管理用ガントチャート</li>
        <li>多様なエクスポート形式（HTML/PNG/SVG/PDF）</li>
        <li>AIプロンプト支援機能</li>
        <li>高DPI/Retinaディスプレイ対応</li>
        </ul>
        
        <h3>技術仕様</h3>
        <ul>
        <li>Python 3.10+ / PySide6</li>
        <li>D3.js v7 / SQLite3</li>
        <li>Playwright / Pillow</li>
        </ul>
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Close button
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class PreferencesDialog(QDialog):
    """Advanced preferences dialog"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("環境設定")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        
        # Tab widget for different categories
        from PySide6.QtWidgets import QTabWidget
        
        self.tab_widget = QTabWidget()
        
        # General tab
        self._create_general_tab()
        
        # Advanced tab
        self._create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self._apply_and_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self._apply_settings)
        
        # Customize button text
        button_box.button(QDialogButtonBox.Ok).setText("OK")
        button_box.button(QDialogButtonBox.Cancel).setText("キャンセル")
        button_box.button(QDialogButtonBox.Apply).setText("適用")
        
        layout.addWidget(button_box)
    
    def _create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark", "Light"])
        layout.addRow("テーマ:", self.theme_combo)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["日本語", "English"])
        layout.addRow("言語:", self.language_combo)
        
        # Startup behavior
        self.startup_check = QCheckBox("起動時に前回のファイルを開く")
        layout.addRow("起動設定:", self.startup_check)
        
        self.tab_widget.addTab(widget, "一般")
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Debug settings
        self.debug_check = QCheckBox("デバッグモードを有効にする")
        layout.addRow("デバッグ:", self.debug_check)
        
        # Performance settings
        self.performance_combo = QComboBox()
        self.performance_combo.addItems(["高品質", "バランス", "高速"])
        layout.addRow("パフォーマンス:", self.performance_combo)
        
        # Memory settings
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(256, 4096)
        self.memory_spin.setSuffix(" MB")
        layout.addRow("メモリ制限:", self.memory_spin)
        
        self.tab_widget.addTab(widget, "詳細")
    
    def _load_settings(self):
        """Load current settings"""
        # Load settings from config
        pass
    
    def _apply_settings(self):
        """Apply settings"""
        try:
            # Apply settings to config
            logger.info("Preferences applied")
        except Exception as e:
            logger.error(f"Failed to apply preferences: {e}")
            QMessageBox.critical(self, "エラー", f"設定の適用に失敗しました: {e}")
    
    def _apply_and_accept(self):
        """Apply settings and close dialog"""
        self._apply_settings()
        self.accept()