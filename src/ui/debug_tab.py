#!/usr/bin/env python3
"""
Debug tab for D3-Mind-Flow-Editor
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QCheckBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor

import logging
from datetime import datetime
from typing import List, Dict

from ..utils.logger import logger


class DebugTab(QWidget):
    """Debug tab for displaying logs and error information"""
    
    def __init__(self):
        super().__init__()
        
        # Log storage
        self.log_entries: List[Dict] = []
        self.max_log_entries = 1000
        
        # Auto-scroll setting
        self.auto_scroll = True
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Setup log capture
        self._setup_log_capture()
        
        # Add initial message
        self.add_info("デバッグタブが初期化されました")
        
        logger.debug("Debug tab initialized")
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("デバッグ出力")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Log level filter
        level_label = QLabel("レベル:")
        header_layout.addWidget(level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.addItem("全て", "ALL")
        self.level_combo.addItem("デバッグ", "DEBUG")
        self.level_combo.addItem("情報", "INFO")
        self.level_combo.addItem("警告", "WARNING")
        self.level_combo.addItem("エラー", "ERROR")
        self.level_combo.addItem("重大", "CRITICAL")
        self.level_combo.setCurrentText("情報")
        header_layout.addWidget(self.level_combo)
        
        # Auto-scroll checkbox
        self.auto_scroll_check = QCheckBox("自動スクロール")
        self.auto_scroll_check.setChecked(True)
        header_layout.addWidget(self.auto_scroll_check)
        
        # Clear button
        self.clear_button = QPushButton("クリア")
        self.clear_button.setToolTip("ログをクリア")
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # Main splitter (log area | details area)
        splitter = QSplitter(Qt.Vertical)
        
        # Log display area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # Use monospace font for better formatting
        font = QFont("Consolas", 9)
        font.setFamily("Monaco")  # macOS
        font.setFamily("DejaVu Sans Mono")  # Linux
        self.log_text.setFont(font)
        
        # Enable rich text for color formatting
        self.log_text.setAcceptRichText(True)
        
        splitter.addWidget(self.log_text)
        
        # Details area (for error details, stack traces, etc.)
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(font)
        self.details_text.setMaximumHeight(200)
        self.details_text.setPlaceholderText("詳細情報がここに表示されます...")
        
        splitter.addWidget(self.details_text)
        
        # Set splitter sizes (log: 70%, details: 30%)
        splitter.setSizes([300, 100])
        
        layout.addWidget(splitter)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("準備完了")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.entry_count_label = QLabel("ログ件数: 0")
        self.entry_count_label.setStyleSheet("color: gray; font-size: 11px;")
        status_layout.addWidget(self.entry_count_label)
        
        layout.addLayout(status_layout)
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.level_combo.currentTextChanged.connect(self._refresh_display)
        self.auto_scroll_check.toggled.connect(self._set_auto_scroll)
        self.clear_button.clicked.connect(self.clear_logs)
        
        # Text selection in log area shows details
        self.log_text.selectionChanged.connect(self._show_selection_details)
    
    def _setup_log_capture(self):
        """Setup log capture from the application logger"""
        # Create a custom handler to capture logs
        class DebugTabHandler(logging.Handler):
            def __init__(self, debug_tab):
                super().__init__()
                self.debug_tab = debug_tab
            
            def emit(self, record):
                try:
                    # Format the log record
                    log_entry = {
                        'timestamp': datetime.fromtimestamp(record.created),
                        'level': record.levelname,
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno,
                        'message': record.getMessage(),
                        'exception': self.format(record) if record.exc_info else None
                    }
                    self.debug_tab._add_log_entry(log_entry)
                except Exception:
                    pass  # Avoid infinite recursion if logging fails
        
        # Add our handler to the application logger
        self.log_handler = DebugTabHandler(self)
        logger.get_logger().addHandler(self.log_handler)
    
    def _add_log_entry(self, entry: Dict):
        """Add a log entry to the display"""
        # Add to storage
        self.log_entries.append(entry)
        
        # Limit storage size
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]
        
        # Update display if entry matches current filter
        current_filter = self.level_combo.currentData()
        if self._should_show_entry(entry, current_filter):
            self._append_entry_to_display(entry)
        
        # Update status
        self._update_status()
    
    def _should_show_entry(self, entry: Dict, level_filter: str) -> bool:
        """Check if entry should be shown based on current filter"""
        if level_filter == "ALL":
            return True
        
        # Map log levels to numeric values for comparison
        level_values = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        
        entry_level = level_values.get(entry['level'], 0)
        filter_level = level_values.get(level_filter, 0)
        
        return entry_level >= filter_level
    
    def _append_entry_to_display(self, entry: Dict):
        """Append a single entry to the display"""
        # Format timestamp
        timestamp = entry['timestamp'].strftime('%H:%M:%S.%f')[:-3]
        
        # Create formatted line
        level = entry['level']
        module = entry['module']
        message = entry['message']
        
        # Color based on log level
        colors = {
            'DEBUG': '#808080',     # Gray
            'INFO': '#000000',      # Black
            'WARNING': '#ff8c00',   # Orange
            'ERROR': '#dc143c',     # Crimson
            'CRITICAL': '#8b0000'   # Dark red
        }
        
        color = colors.get(level, '#000000')
        
        # Format the line
        formatted_line = f"[{timestamp}] {level:<8} {module:<15} - {message}"
        
        # Append to text widget with color
        cursor = self.log_text.textCursor()
        # Use proper enum for QTextCursor move operation (compatible with newer PySide6)
        try:
            # Try new PySide6 style first
            cursor.movePosition(QTextCursor.MoveOperation.End)
        except AttributeError:
            # Fallback to older style
            cursor.movePosition(QTextCursor.End)
        
        # Set color format
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        
        # Insert text
        cursor.insertText(formatted_line + "\\n")
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _refresh_display(self):
        """Refresh the entire display based on current filter"""
        # Clear current display
        self.log_text.clear()
        
        # Get current filter
        current_filter = self.level_combo.currentData()
        
        # Add all entries that match the filter
        for entry in self.log_entries:
            if self._should_show_entry(entry, current_filter):
                self._append_entry_to_display(entry)
        
        self._update_status()
    
    def _set_auto_scroll(self, enabled: bool):
        """Set auto-scroll setting"""
        self.auto_scroll = enabled
    
    def _show_selection_details(self):
        """Show details for selected log entry"""
        cursor = self.log_text.textCursor()
        if not cursor.hasSelection():
            self.details_text.clear()
            return
        
        # Get selected line(s)
        selected_text = cursor.selectedText()
        
        # Try to find corresponding log entry
        # This is a simple implementation - could be improved
        for entry in reversed(self.log_entries):  # Check recent entries first
            if entry['message'] in selected_text:
                details = self._format_entry_details(entry)
                self.details_text.setPlainText(details)
                break
        else:
            self.details_text.setPlainText("選択されたログエントリの詳細が見つかりません")
    
    def _format_entry_details(self, entry: Dict) -> str:
        """Format detailed information for a log entry"""
        details = []
        details.append(f"タイムスタンプ: {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        details.append(f"レベル: {entry['level']}")
        details.append(f"モジュール: {entry['module']}")
        details.append(f"関数: {entry['function']}")
        details.append(f"行番号: {entry['line']}")
        details.append(f"メッセージ: {entry['message']}")
        
        if entry.get('exception'):
            details.append("\\n例外情報:")
            details.append(entry['exception'])
        
        return "\\n".join(details)
    
    def _update_status(self):
        """Update status information"""
        total_entries = len(self.log_entries)
        self.entry_count_label.setText(f"ログ件数: {total_entries}")
        
        # Update status message
        current_filter = self.level_combo.currentData()
        if current_filter == "ALL":
            self.status_label.setText("全てのログを表示中")
        else:
            self.status_label.setText(f"{current_filter}以上のログを表示中")
    
    # Public methods for adding different types of logs
    def add_debug(self, message: str):
        """Add debug message"""
        entry = {
            'timestamp': datetime.now(),
            'level': 'DEBUG',
            'module': 'debug_tab',
            'function': 'add_debug',
            'line': 0,
            'message': message,
            'exception': None
        }
        self._add_log_entry(entry)
    
    def add_info(self, message: str):
        """Add info message"""
        entry = {
            'timestamp': datetime.now(),
            'level': 'INFO',
            'module': 'debug_tab',
            'function': 'add_info',
            'line': 0,
            'message': message,
            'exception': None
        }
        self._add_log_entry(entry)
    
    def add_warning(self, message: str):
        """Add warning message"""
        entry = {
            'timestamp': datetime.now(),
            'level': 'WARNING',
            'module': 'debug_tab',
            'function': 'add_warning',
            'line': 0,
            'message': message,
            'exception': None
        }
        self._add_log_entry(entry)
    
    def add_error(self, message: str, exception_info: str = None):
        """Add error message"""
        entry = {
            'timestamp': datetime.now(),
            'level': 'ERROR',
            'module': 'debug_tab',
            'function': 'add_error',
            'line': 0,
            'message': message,
            'exception': exception_info
        }
        self._add_log_entry(entry)
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_entries.clear()
        self.log_text.clear()
        self.details_text.clear()
        self._update_status()
        self.add_info("ログがクリアされました")
    
    def export_logs(self, file_path: str):
        """Export logs to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"D3-Mind-Flow-Editor Debug Log\\n")
                f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
                f.write("=" * 50 + "\\n\\n")
                
                for entry in self.log_entries:
                    timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    f.write(f"[{timestamp}] {entry['level']:<8} {entry['module']:<15} - {entry['message']}\\n")
                    
                    if entry.get('exception'):
                        f.write(f"Exception: {entry['exception']}\\n")
                    f.write("\\n")
            
            self.add_info(f"ログを {file_path} にエクスポートしました")
            
        except Exception as e:
            self.add_error(f"ログのエクスポートに失敗しました: {e}")