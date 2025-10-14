#!/usr/bin/env python3
"""
Settings tab for D3-Mind-Flow-Editor
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QComboBox, QSpinBox, QCheckBox, QRadioButton,
    QPushButton, QButtonGroup, QGroupBox, QLineEdit,
    QFileDialog, QMessageBox, QSlider
)
from PySide6.QtCore import Qt, Signal

from ..utils.config import Config
from ..utils.logger import logger
from ..utils.resolution_manager import ResolutionManager


class SettingsTab(QWidget):
    """Settings tab for application configuration"""
    
    # Signal emitted when settings change
    settings_changed = Signal()
    
    def __init__(self, config: Config, resolution_manager: ResolutionManager):
        super().__init__()
        
        self.config = config
        self.resolution_manager = resolution_manager
        
        # Track if settings have been modified
        self.settings_modified = False
        
        self._setup_ui()
        self._setup_connections()
        self._load_current_settings()
        
        logger.debug("Settings tab initialized")
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("設定")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Reset and apply buttons
        self.reset_button = QPushButton("デフォルトに戻す")
        self.reset_button.setToolTip("全ての設定をデフォルト値に戻す")
        header_layout.addWidget(self.reset_button)
        
        self.apply_button = QPushButton("適用")
        self.apply_button.setToolTip("設定を適用")
        self.apply_button.setEnabled(False)
        header_layout.addWidget(self.apply_button)
        
        layout.addLayout(header_layout)
        
        # Display settings group
        display_group = self._create_display_settings_group()
        layout.addWidget(display_group)
        
        # Export settings group
        export_group = self._create_export_settings_group()
        layout.addWidget(export_group)
        
        # Preview settings group
        preview_group = self._create_preview_settings_group()
        layout.addWidget(preview_group)
        
        # Editor settings group
        editor_group = self._create_editor_settings_group()
        layout.addWidget(editor_group)
        
        # Paths settings group
        paths_group = self._create_paths_settings_group()
        layout.addWidget(paths_group)
        
        layout.addStretch()
        
        # Status display
        self.status_label = QLabel("設定準備完了")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.status_label)
    
    def _create_display_settings_group(self) -> QGroupBox:
        """Create display settings group"""
        group = QGroupBox("表示設定")
        layout = QGridLayout(group)
        
        # DPI Scaling
        layout.addWidget(QLabel("DPI スケーリング:"), 0, 0)
        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(["自動検出", "100%", "150%", "200%", "300%"])
        layout.addWidget(self.dpi_combo, 0, 1)
        
        # Current display info
        display_info = self.resolution_manager.get_display_info()
        dpi_info_text = f"現在の DPR: {display_info['device_pixel_ratio']:.1f}, DPI: {display_info['logical_dpi']:.0f}"
        dpi_info_label = QLabel(dpi_info_text)
        dpi_info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(dpi_info_label, 0, 2)
        
        return group
    
    def _create_export_settings_group(self) -> QGroupBox:
        """Create export settings group"""
        group = QGroupBox("エクスポート設定")
        layout = QGridLayout(group)
        
        # PNG DPI settings
        layout.addWidget(QLabel("PNG解像度:"), 0, 0)
        
        # PNG DPI radio buttons
        self.png_dpi_group = QButtonGroup()
        
        self.png_72_radio = QRadioButton("標準 (72 dpi)")
        self.png_150_radio = QRadioButton("高画質 (150 dpi)")
        self.png_300_radio = QRadioButton("印刷品質 (300 dpi) [推奨]")
        self.png_custom_radio = QRadioButton("カスタム")
        
        self.png_dpi_group.addButton(self.png_72_radio, 72)
        self.png_dpi_group.addButton(self.png_150_radio, 150)
        self.png_dpi_group.addButton(self.png_300_radio, 300)
        self.png_dpi_group.addButton(self.png_custom_radio, 0)
        
        dpi_layout = QVBoxLayout()
        dpi_layout.addWidget(self.png_72_radio)
        dpi_layout.addWidget(self.png_150_radio)
        dpi_layout.addWidget(self.png_300_radio)
        
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.png_custom_radio)
        self.png_custom_spin = QSpinBox()
        self.png_custom_spin.setRange(50, 600)
        self.png_custom_spin.setSuffix(" dpi")
        custom_layout.addWidget(self.png_custom_spin)
        custom_layout.addStretch()
        dpi_layout.addLayout(custom_layout)
        
        layout.addLayout(dpi_layout, 0, 1, 1, 2)
        
        # PNG Size settings
        layout.addWidget(QLabel("PNG サイズ:"), 1, 0)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("幅:"))
        self.png_width_spin = QSpinBox()
        self.png_width_spin.setRange(100, 7680)
        self.png_width_spin.setSuffix(" px")
        size_layout.addWidget(self.png_width_spin)
        
        size_layout.addWidget(QLabel("高さ:"))
        self.png_height_spin = QSpinBox()
        self.png_height_spin.setRange(100, 4320)
        self.png_height_spin.setSuffix(" px")
        size_layout.addWidget(self.png_height_spin)
        
        self.aspect_ratio_check = QCheckBox("アスペクト比を固定")
        size_layout.addWidget(self.aspect_ratio_check)
        
        size_layout.addStretch()
        layout.addLayout(size_layout, 1, 1, 1, 2)
        
        # PDF settings
        layout.addWidget(QLabel("PDF設定:"), 2, 0)
        
        pdf_layout = QVBoxLayout()
        self.pdf_vector_check = QCheckBox("ベクター形式で出力（推奨）")
        pdf_layout.addWidget(self.pdf_vector_check)
        
        paper_layout = QHBoxLayout()
        paper_layout.addWidget(QLabel("用紙サイズ:"))
        self.pdf_paper_combo = QComboBox()
        self.pdf_paper_combo.addItems(["A4", "A3", "Letter", "Legal", "Custom"])
        paper_layout.addWidget(self.pdf_paper_combo)
        paper_layout.addStretch()
        pdf_layout.addLayout(paper_layout)
        
        layout.addLayout(pdf_layout, 2, 1, 1, 2)
        
        return group
    
    def _create_preview_settings_group(self) -> QGroupBox:
        """Create preview settings group"""
        group = QGroupBox("プレビュー設定")
        layout = QGridLayout(group)
        
        # Rendering quality
        layout.addWidget(QLabel("レンダリング品質:"), 0, 0)
        
        quality_layout = QVBoxLayout()
        self.quality_group = QButtonGroup()
        
        self.quality_low_radio = QRadioButton("低（動作優先）")
        self.quality_standard_radio = QRadioButton("標準")
        self.quality_high_radio = QRadioButton("高（表示優先）")
        
        self.quality_group.addButton(self.quality_low_radio, 0)
        self.quality_group.addButton(self.quality_standard_radio, 1)
        self.quality_group.addButton(self.quality_high_radio, 2)
        
        quality_layout.addWidget(self.quality_low_radio)
        quality_layout.addWidget(self.quality_standard_radio)
        quality_layout.addWidget(self.quality_high_radio)
        
        layout.addLayout(quality_layout, 0, 1)
        
        # Anti-aliasing
        layout.addWidget(QLabel("アンチエイリアス:"), 1, 0)
        self.antialiasing_check = QCheckBox("有効にする")
        layout.addWidget(self.antialiasing_check, 1, 1)
        
        return group
    
    def _create_editor_settings_group(self) -> QGroupBox:
        """Create editor settings group"""
        group = QGroupBox("エディタ設定")
        layout = QGridLayout(group)
        
        # Auto-save
        layout.addWidget(QLabel("自動保存:"), 0, 0)
        self.auto_save_check = QCheckBox("有効にする")
        layout.addWidget(self.auto_save_check, 0, 1)
        
        # Auto-save interval
        layout.addWidget(QLabel("自動保存間隔:"), 1, 0)
        interval_layout = QHBoxLayout()
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(10, 300)
        self.auto_save_interval_spin.setSuffix(" 秒")
        interval_layout.addWidget(self.auto_save_interval_spin)
        interval_layout.addStretch()
        layout.addLayout(interval_layout, 1, 1)
        
        # Line numbers
        layout.addWidget(QLabel("行番号表示:"), 2, 0)
        self.line_numbers_check = QCheckBox("有効にする")
        layout.addWidget(self.line_numbers_check, 2, 1)
        
        # Word wrap
        layout.addWidget(QLabel("ワードラップ:"), 3, 0)
        self.word_wrap_check = QCheckBox("有効にする")
        layout.addWidget(self.word_wrap_check, 3, 1)
        
        return group
    
    def _create_paths_settings_group(self) -> QGroupBox:
        """Create paths settings group"""
        group = QGroupBox("パス設定")
        layout = QGridLayout(group)
        
        # Export directory
        layout.addWidget(QLabel("エクスポート先:"), 0, 0)
        
        export_layout = QHBoxLayout()
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setPlaceholderText("デフォルトディレクトリを使用")
        export_layout.addWidget(self.export_path_edit)
        
        self.export_browse_button = QPushButton("参照...")
        export_layout.addWidget(self.export_browse_button)
        
        layout.addLayout(export_layout, 0, 1)
        
        # Template directory
        layout.addWidget(QLabel("テンプレート:"), 1, 0)
        
        template_layout = QHBoxLayout()
        self.template_path_edit = QLineEdit()
        self.template_path_edit.setPlaceholderText("デフォルトテンプレートを使用")
        template_layout.addWidget(self.template_path_edit)
        
        self.template_browse_button = QPushButton("参照...")
        template_layout.addWidget(self.template_browse_button)
        
        layout.addLayout(template_layout, 1, 1)
        
        return group
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Buttons
        self.reset_button.clicked.connect(self._reset_to_defaults)
        self.apply_button.clicked.connect(self._apply_settings)
        
        # Settings change tracking
        self.dpi_combo.currentTextChanged.connect(self._on_setting_changed)
        
        # PNG DPI settings
        self.png_dpi_group.buttonClicked.connect(self._on_setting_changed)
        self.png_custom_spin.valueChanged.connect(self._on_setting_changed)
        
        # PNG size settings
        self.png_width_spin.valueChanged.connect(self._on_png_width_changed)
        self.png_height_spin.valueChanged.connect(self._on_png_height_changed)
        self.aspect_ratio_check.toggled.connect(self._on_setting_changed)
        
        # PDF settings
        self.pdf_vector_check.toggled.connect(self._on_setting_changed)
        self.pdf_paper_combo.currentTextChanged.connect(self._on_setting_changed)
        
        # Preview settings
        self.quality_group.buttonClicked.connect(self._on_setting_changed)
        self.antialiasing_check.toggled.connect(self._on_setting_changed)
        
        # Editor settings
        self.auto_save_check.toggled.connect(self._on_auto_save_toggled)
        self.auto_save_interval_spin.valueChanged.connect(self._on_setting_changed)
        self.line_numbers_check.toggled.connect(self._on_setting_changed)
        self.word_wrap_check.toggled.connect(self._on_setting_changed)
        
        # Path settings
        self.export_path_edit.textChanged.connect(self._on_setting_changed)
        self.template_path_edit.textChanged.connect(self._on_setting_changed)
        self.export_browse_button.clicked.connect(self._browse_export_directory)
        self.template_browse_button.clicked.connect(self._browse_template_directory)
        
        # Enable/disable custom PNG DPI spinbox
        self.png_custom_radio.toggled.connect(self._on_png_custom_toggled)
    
    def _on_setting_changed(self):
        """Handle setting change"""
        self.settings_modified = True
        self.apply_button.setEnabled(True)
        self.status_label.setText("設定が変更されました（適用ボタンを押してください）")
    
    def _on_auto_save_toggled(self, enabled: bool):
        """Handle auto-save toggle"""
        self.auto_save_interval_spin.setEnabled(enabled)
        self._on_setting_changed()
    
    def _on_png_custom_toggled(self, enabled: bool):
        """Handle custom PNG DPI toggle"""
        self.png_custom_spin.setEnabled(enabled)
        self._on_setting_changed()
    
    def _on_png_width_changed(self, width: int):
        """Handle PNG width change (maintain aspect ratio if enabled)"""
        if self.aspect_ratio_check.isChecked():
            # Calculate height maintaining 16:9 ratio
            height = int(width * 9 / 16)
            self.png_height_spin.blockSignals(True)
            self.png_height_spin.setValue(height)
            self.png_height_spin.blockSignals(False)
        self._on_setting_changed()
    
    def _on_png_height_changed(self, height: int):
        """Handle PNG height change (maintain aspect ratio if enabled)"""
        if self.aspect_ratio_check.isChecked():
            # Calculate width maintaining 16:9 ratio
            width = int(height * 16 / 9)
            self.png_width_spin.blockSignals(True)
            self.png_width_spin.setValue(width)
            self.png_width_spin.blockSignals(False)
        self._on_setting_changed()
    
    def _browse_export_directory(self):
        """Browse for export directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "エクスポート先ディレクトリを選択",
            self.export_path_edit.text()
        )
        if directory:
            self.export_path_edit.setText(directory)
    
    def _browse_template_directory(self):
        """Browse for template directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "テンプレートディレクトリを選択",
            self.template_path_edit.text()
        )
        if directory:
            self.template_path_edit.setText(directory)
    
    def _load_current_settings(self):
        """Load current settings from config"""
        # Display settings
        dpi_setting = self.config.dpi_scaling
        dpi_mapping = {
            "auto": "自動検出",
            "100%": "100%",
            "150%": "150%",
            "200%": "200%",
            "300%": "300%"
        }
        self.dpi_combo.setCurrentText(dpi_mapping.get(dpi_setting, "自動検出"))
        
        # Export settings
        png_dpi = self.config.png_dpi
        if png_dpi == 72:
            self.png_72_radio.setChecked(True)
        elif png_dpi == 150:
            self.png_150_radio.setChecked(True)
        elif png_dpi == 300:
            self.png_300_radio.setChecked(True)
        else:
            self.png_custom_radio.setChecked(True)
            self.png_custom_spin.setValue(png_dpi)
        
        self.png_width_spin.setValue(self.config.get('export.png_width', 1920))
        self.png_height_spin.setValue(self.config.get('export.png_height', 1080))
        self.aspect_ratio_check.setChecked(self.config.get('export.png_keep_aspect', True))
        
        self.pdf_vector_check.setChecked(self.config.get('export.pdf_vector', True))
        self.pdf_paper_combo.setCurrentText(self.config.get('export.pdf_paper_size', 'A4'))
        
        # Preview settings
        quality = self.config.get('display.rendering_quality', 'standard')
        quality_mapping = {"low": 0, "standard": 1, "high": 2}
        quality_button = self.quality_group.button(quality_mapping.get(quality, 1))
        if quality_button:
            quality_button.setChecked(True)
        
        self.antialiasing_check.setChecked(self.config.get('display.anti_aliasing', True))
        
        # Editor settings
        self.auto_save_check.setChecked(self.config.get('editor.auto_save', True))
        self.auto_save_interval_spin.setValue(self.config.get('editor.auto_save_interval', 30))
        self.auto_save_interval_spin.setEnabled(self.auto_save_check.isChecked())
        
        self.line_numbers_check.setChecked(self.config.get('editor.show_line_numbers', True))
        self.word_wrap_check.setChecked(self.config.get('editor.word_wrap', True))
        
        # Path settings
        self.export_path_edit.setText(self.config.export_directory)
        self.template_path_edit.setText(self.config.get('paths.template_directory', ''))
        
        # Enable custom PNG DPI spinbox if custom is selected
        self.png_custom_spin.setEnabled(self.png_custom_radio.isChecked())
        
        self.settings_modified = False
        self.apply_button.setEnabled(False)
        self.status_label.setText("設定が読み込まれました")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "設定リセット",
            "全ての設定をデフォルト値に戻しますか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_to_defaults()
            self._load_current_settings()
            self.settings_changed.emit()
            self.status_label.setText("設定がデフォルト値に戻されました")
            logger.info("Settings reset to defaults")
    
    def _apply_settings(self):
        """Apply current settings"""
        try:
            # Display settings
            dpi_mapping = {
                "自動検出": "auto",
                "100%": "100%",
                "150%": "150%",
                "200%": "200%",
                "300%": "300%"
            }
            self.config.dpi_scaling = dpi_mapping.get(self.dpi_combo.currentText(), "auto")
            
            # Export settings
            if self.png_custom_radio.isChecked():
                self.config.png_dpi = self.png_custom_spin.value()
            else:
                checked_button = self.png_dpi_group.checkedButton()
                if checked_button:
                    self.config.png_dpi = self.png_dpi_group.id(checked_button)
            
            self.config.set('export.png_width', self.png_width_spin.value())
            self.config.set('export.png_height', self.png_height_spin.value())
            self.config.set('export.png_keep_aspect', self.aspect_ratio_check.isChecked())
            
            self.config.set('export.pdf_vector', self.pdf_vector_check.isChecked())
            self.config.set('export.pdf_paper_size', self.pdf_paper_combo.currentText())
            
            # Preview settings
            quality_mapping = {0: "low", 1: "standard", 2: "high"}
            checked_quality = self.quality_group.checkedButton()
            if checked_quality:
                quality = quality_mapping.get(self.quality_group.id(checked_quality), "standard")
                self.config.set('display.rendering_quality', quality)
            
            self.config.set('display.anti_aliasing', self.antialiasing_check.isChecked())
            
            # Editor settings
            self.config.set('editor.auto_save', self.auto_save_check.isChecked())
            self.config.set('editor.auto_save_interval', self.auto_save_interval_spin.value())
            self.config.set('editor.show_line_numbers', self.line_numbers_check.isChecked())
            self.config.set('editor.word_wrap', self.word_wrap_check.isChecked())
            
            # Path settings
            self.config.export_directory = self.export_path_edit.text()
            self.config.set('paths.template_directory', self.template_path_edit.text())
            
            # Save configuration
            self.config.save()
            
            # Emit settings changed signal
            self.settings_changed.emit()
            
            # Update UI state
            self.settings_modified = False
            self.apply_button.setEnabled(False)
            self.status_label.setText("設定が適用されました")
            
            logger.info("Settings applied successfully")
            
        except Exception as e:
            error_msg = f"設定の適用に失敗しました: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self, "エラー", error_msg)
            self.status_label.setText("設定の適用に失敗しました")