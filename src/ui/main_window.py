#!/usr/bin/env python3
"""
Main window for D3-Mind-Flow-Editor
"""

# Import PySide6 components with comprehensive error handling
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QSplitter, QTabWidget, QToolBar, QMenuBar, QMenu,
        QStatusBar, QMessageBox, QApplication, QFileDialog
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QAction, QIcon, QKeySequence
except ImportError as e:
    print(f"Critical Error: PySide6 UI components import failed: {e}")
    import sys
    sys.exit(1)

# Import application modules with error handling
try:
    from ..database.db_manager import DatabaseManager
    from ..database.models import Diagram, DiagramType
    from ..utils.config import Config
    from ..utils.logger import logger
    from ..utils.resolution_manager import ResolutionManager
    from ..core.export_manager import ExportManager
    
    from .input_panel import InputPanel
    from .preview_panel import PreviewPanel
    from .list_panel import ListPanel
    from .debug_tab import DebugTab
    from .help_tab import HelpTab
    from .settings_tab import SettingsTab
    from .dialogs import SaveDialog, ExportDialog
except ImportError as e:
    print(f"Warning: Some application modules could not be imported: {e}")
    # Continue with available modules
    try:
        from ..utils.logger import logger
        logger.warning(f"Module import warning: {e}")
    except:
        print(f"Logger unavailable, import error: {e}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    diagram_saved = Signal(Diagram)
    diagram_loaded = Signal(Diagram)
    
    def __init__(self):
        super().__init__()
        
        # Initialize components with error handling
        try:
            self.config = Config()
            logger.info("Configuration initialized")
        except Exception as e:
            logger.error(f"Config initialization failed: {e}")
            self.config = None
        
        try:
            self.db_manager = DatabaseManager()
            logger.info("Database manager initialized")
        except Exception as e:
            logger.error(f"Database manager initialization failed: {e}")
            self.db_manager = None
        
        try:
            self.resolution_manager = ResolutionManager(self.config) if self.config else None
            logger.info("Resolution manager initialized")
        except Exception as e:
            logger.warning(f"Resolution manager initialization failed: {e}")
            self.resolution_manager = None
        
        # Initialize export manager
        try:
            self.export_manager = ExportManager()
            logger.info("Export manager initialized")
        except Exception as e:
            logger.warning(f"Export manager initialization failed: {e}")
            self.export_manager = None
        
        # Current diagram
        self.current_diagram = None
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        
        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_tool_bar()
        self._setup_status_bar()
        self._setup_shortcuts()
        self._setup_connections()
        
        # Apply configuration
        self._apply_config()
        
        # Initial preview update (delayed to ensure UI is ready)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._initial_preview_update)
        
        logger.info("Main window initialized")
    
    def _initial_preview_update(self):
        """Perform initial preview update"""
        try:
            # Update preview with initial content
            self._refresh_preview()
            logger.debug("Initial preview updated")
        except Exception as e:
            logger.warning(f"Initial preview update failed: {e}")
    
    def _setup_ui(self):
        """Setup main UI layout"""
        self.setWindowTitle("D3-Mind-Flow-Editor")
        self.setMinimumSize(800, 600)
        
        # Central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main splitter (horizontal: left panel | right area)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel (input and list)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Input panel with error handling
        try:
            self.input_panel = InputPanel(self.config, self.db_manager)
            left_layout.addWidget(self.input_panel, 2)  # 2/3 of left panel
            logger.debug("Input panel created")
        except Exception as e:
            logger.error(f"Input panel initialization failed: {e}")
            # Create fallback simple text widget
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("入力パネルの初期化に失敗しました")
            left_layout.addWidget(fallback_label, 2)
            self.input_panel = None
        
        # Saved diagrams list with error handling
        try:
            self.list_panel = ListPanel(self.db_manager)
            left_layout.addWidget(self.list_panel, 1)  # 1/3 of left panel
            logger.debug("List panel created")
        except Exception as e:
            logger.warning(f"List panel initialization failed: {e}")
            # Create fallback simple widget
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("リストパネルの初期化に失敗しました")
            left_layout.addWidget(fallback_label, 1)
            self.list_panel = None
        
        main_splitter.addWidget(left_widget)
        
        # Right area with tabs
        self.right_tabs = QTabWidget()
        self.right_tabs.setTabPosition(QTabWidget.South)
        
        # Preview tab with error handling
        try:
            self.preview_panel = PreviewPanel(self.config, self.resolution_manager)
            self.right_tabs.addTab(self.preview_panel, "プレビュー")
            logger.debug("Preview panel created")
        except Exception as e:
            logger.error(f"Preview panel initialization failed: {e}")
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("プレビューパネルの初期化に失敗しました")
            self.right_tabs.addTab(fallback_label, "プレビュー")
            self.preview_panel = None
        
        # Debug tab with error handling
        try:
            self.debug_tab = DebugTab()
            self.right_tabs.addTab(self.debug_tab, "デバッグ")
            logger.debug("Debug tab created")
        except Exception as e:
            logger.warning(f"Debug tab initialization failed: {e}")
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("デバッグタブの初期化に失敗しました")
            self.right_tabs.addTab(fallback_label, "デバッグ")
            self.debug_tab = None
        
        # Help tab with error handling
        try:
            self.help_tab = HelpTab()
            self.right_tabs.addTab(self.help_tab, "ヘルプ")
            logger.debug("Help tab created")
        except Exception as e:
            logger.warning(f"Help tab initialization failed: {e}")
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("ヘルプタブの初期化に失敗しました")
            self.right_tabs.addTab(fallback_label, "ヘルプ")
            self.help_tab = None
        
        # Settings tab with error handling
        try:
            self.settings_tab = SettingsTab(self.config, self.resolution_manager)
            self.right_tabs.addTab(self.settings_tab, "設定")
            logger.debug("Settings tab created")
        except Exception as e:
            logger.warning(f"Settings tab initialization failed: {e}")
            from PySide6.QtWidgets import QLabel
            fallback_label = QLabel("設定タブの初期化に失敗しました")
            self.right_tabs.addTab(fallback_label, "設定")
            self.settings_tab = None
        
        main_splitter.addWidget(self.right_tabs)
        
        # Set splitter sizes (left: 400px, right: remaining)
        main_splitter.setSizes([400, 800])
        
        # Store splitter reference
        self.main_splitter = main_splitter
    
    def _setup_menu_bar(self):
        """Setup menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("ファイル(&F)")
        
        # New action
        new_action = QAction("新規作成(&N)", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_diagram)
        file_menu.addAction(new_action)
        
        # Open action
        open_action = QAction("開く(&O)", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_diagram)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save action
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_diagram)
        file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction("名前を付けて保存(&A)", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self._save_diagram_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = file_menu.addMenu("エクスポート(&E)")
        
        export_html_action = QAction("HTML", self)
        export_html_action.triggered.connect(lambda: self._export_diagram("html"))
        export_menu.addAction(export_html_action)
        
        export_png_action = QAction("PNG", self)
        export_png_action.triggered.connect(lambda: self._export_diagram("png"))
        export_menu.addAction(export_png_action)
        
        export_svg_action = QAction("SVG", self)
        export_svg_action.triggered.connect(lambda: self._export_diagram("svg"))
        export_menu.addAction(export_svg_action)
        
        export_pdf_action = QAction("PDF", self)
        export_pdf_action.triggered.connect(lambda: self._export_diagram("pdf"))
        export_menu.addAction(export_pdf_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("編集(&E)")
        
        # Copy action
        copy_action = QAction("コピー(&C)", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._copy_content)
        edit_menu.addAction(copy_action)
        
        # Paste action
        paste_action = QAction("貼り付け(&V)", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self._paste_content)
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menu_bar.addMenu("表示(&V)")
        
        # Refresh action
        refresh_action = QAction("更新(&R)", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self._refresh_preview)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("ヘルプ(&H)")
        
        # About action
        about_action = QAction("D3-Mind-Flow-Editorについて(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_tool_bar(self):
        """Setup tool bar"""
        toolbar = QToolBar("メインツールバー")
        self.addToolBar(toolbar)
        
        # New button
        new_action = QAction("新規", self)
        new_action.setToolTip("新しい図を作成")
        new_action.triggered.connect(self._new_diagram)
        toolbar.addAction(new_action)
        
        # Save button
        save_action = QAction("保存", self)
        save_action.setToolTip("現在の図を保存")
        save_action.triggered.connect(self._save_diagram)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Export button
        export_action = QAction("エクスポート", self)
        export_action.setToolTip("図をファイルにエクスポート")
        export_action.triggered.connect(self._show_export_dialog)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Refresh button
        refresh_action = QAction("更新", self)
        refresh_action.setToolTip("プレビューを更新")
        refresh_action.triggered.connect(self._refresh_preview)
        toolbar.addAction(refresh_action)
    
    def _setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Display initial message
        self.status_bar.showMessage("準備完了", 2000)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Additional shortcuts not covered by menu actions
        pass
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Input panel connections
        self.input_panel.content_changed.connect(self._on_content_changed)
        self.input_panel.diagram_type_changed.connect(self._on_diagram_type_changed)
        
        # List panel connections
        self.list_panel.diagram_selected.connect(self._load_diagram)
        self.list_panel.diagram_deleted.connect(self._on_diagram_deleted)
        
        # Settings tab connections
        self.settings_tab.settings_changed.connect(self._apply_config)
        
        # Preview panel connections
        self.preview_panel.error_occurred.connect(self._on_preview_error)
    
    def _apply_config(self):
        """Apply configuration settings"""
        # Window size
        width, height = self.config.window_size
        self.resize(width, height)
        
        # Splitter sizes
        splitter_sizes = self.config.get('ui.splitter_sizes', [400, 800])
        self.main_splitter.setSizes(splitter_sizes)
        
        # Auto-save timer
        if self.config.get('editor.auto_save', True):
            interval = self.config.get('editor.auto_save_interval', 30) * 1000
            self.auto_save_timer.start(interval)
        else:
            self.auto_save_timer.stop()
    
    def _new_diagram(self):
        """Create new diagram"""
        self.current_diagram = None
        self.input_panel.clear()
        self.preview_panel.clear()
        self.status_bar.showMessage("新しい図を作成しました", 2000)
        logger.info("New diagram created")
    
    def _save_diagram(self):
        """Save current diagram"""
        if self.current_diagram is None:
            self._save_diagram_as()
        else:
            self._do_save()
    
    def _save_diagram_as(self):
        """Save diagram with new name"""
        dialog = SaveDialog(self)
        
        if self.current_diagram:
            dialog.set_title(self.current_diagram.title)
            dialog.set_description(self.current_diagram.description)
        
        if dialog.exec():
            title, description = dialog.get_data()
            
            # Create or update diagram
            if self.current_diagram is None:
                self.current_diagram = Diagram()
            
            self.current_diagram.title = title
            self.current_diagram.description = description
            self.current_diagram.diagram_type = self.input_panel.get_diagram_type()
            self.current_diagram.mermaid_data = self.input_panel.get_content()
            
            self._do_save()
    
    def _do_save(self):
        """Perform actual save operation"""
        try:
            diagram_id = self.db_manager.save_diagram(self.current_diagram)
            self.current_diagram.id = diagram_id
            
            self.status_bar.showMessage(f"保存しました: {self.current_diagram.title}", 2000)
            self.diagram_saved.emit(self.current_diagram)
            self.list_panel.refresh()
            
            logger.info(f"Diagram saved: {self.current_diagram.title} (ID: {diagram_id})")
            
        except Exception as e:
            logger.error(f"Failed to save diagram: {e}")
            QMessageBox.critical(self, "エラー", f"保存に失敗しました: {e}")
    
    def _load_diagram(self, diagram: Diagram):
        """Load diagram from database"""
        self.current_diagram = diagram
        self.input_panel.load_diagram(diagram)
        self.preview_panel.update_content(diagram.mermaid_data, diagram.diagram_type)
        
        self.status_bar.showMessage(f"読み込みました: {diagram.title}", 2000)
        self.diagram_loaded.emit(diagram)
        
        logger.info(f"Diagram loaded: {diagram.title} (ID: {diagram.id})")
    
    def _open_diagram(self):
        """Show open diagram dialog"""
        # Switch to list panel tab for diagram selection
        self.right_tabs.setCurrentWidget(self.list_panel)
        self.status_bar.showMessage("リストから図を選択してください", 3000)
    
    def _export_diagram(self, format_type: str):
        """Export current diagram"""
        content = self.input_panel.get_content().strip()
        if not content:
            QMessageBox.warning(self, "警告", "エクスポートする内容がありません。")
            return
        
        # Get diagram type
        diagram_type = self.input_panel.get_diagram_type()
        
        try:
            # Import export manager
            from ..core.export_manager import ExportManager
            
            # Create export manager
            export_manager = ExportManager(self.config, self.resolution_manager)
            
            # Show file dialog
            from PySide6.QtWidgets import QFileDialog
            
            # Set file extension based on format
            extensions = {
                'html': 'HTML Files (*.html)',
                'png': 'PNG Images (*.png)', 
                'svg': 'SVG Files (*.svg)',
                'pdf': 'PDF Files (*.pdf)'
            }
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"{format_type.upper()}としてエクスポート",
                f"diagram.{format_type}",
                extensions.get(format_type, "All Files (*)")
            )
            
            if not file_path:
                return
            
            # Prepare diagram data
            diagram_data = {
                'type': diagram_type,
                'content': content,
                'styles': {}
            }
            
            # Show progress message
            self.status_bar.showMessage(f"{format_type.upper()}エクスポート中...", 0)
            QApplication.processEvents()
            
            # Export using async function (we'll make it sync for now)
            import asyncio
            
            # Create new event loop if one doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Export diagram
            success = loop.run_until_complete(
                export_manager.export_diagram(diagram_data, format_type, file_path)
            )
            
            if success:
                self.status_bar.showMessage(f"{format_type.upper()}エクスポート完了: {file_path}", 5000)
                QMessageBox.information(self, "成功", f"エクスポートが完了しました:\n{file_path}")
                logger.info(f"Export successful: {file_path}")
            else:
                self.status_bar.showMessage("エクスポートに失敗しました", 3000)
                QMessageBox.warning(self, "エラー", "エクスポートに失敗しました。\nデバッグタブでエラー詳細を確認してください。")
                logger.error(f"Export failed: {format_type}")
                
        except Exception as e:
            self.status_bar.showMessage("エクスポートエラーが発生しました", 3000)
            QMessageBox.critical(self, "エラー", f"エクスポート中にエラーが発生しました:\n{str(e)}")
            logger.error(f"Export error: {e}", exc_info=True)
    
    def _show_export_dialog(self):
        """Show export dialog"""
        dialog = ExportDialog(self)
        if dialog.exec():
            format_type, file_path = dialog.get_export_settings()
            self._export_diagram(format_type)
    
    def _copy_content(self):
        """Copy current content to clipboard"""
        self.input_panel.copy_content()
    
    def _paste_content(self):
        """Paste content from clipboard"""
        self.input_panel.paste_content()
    
    def _refresh_preview(self):
        """Refresh preview panel"""
        content = self.input_panel.get_content()
        diagram_type = self.input_panel.get_diagram_type()
        self.preview_panel.update_content(content, diagram_type)
        self.status_bar.showMessage("プレビューを更新しました", 2000)
    
    def _on_content_changed(self):
        """Handle input content change"""
        # Update preview automatically
        self._refresh_preview()
        
        # Update current diagram if exists
        if self.current_diagram:
            self.current_diagram.mermaid_data = self.input_panel.get_content()
        
        logger.debug("Content changed - preview updated")
    
    def _on_diagram_type_changed(self, diagram_type: str):
        """Handle diagram type change"""
        # Update preview with new type
        self._refresh_preview()
        
        # Update current diagram type
        if self.current_diagram:
            self.current_diagram.diagram_type = diagram_type
            
        # Update status
        from ..database.models import DiagramType
        type_name = DiagramType.display_names().get(diagram_type, diagram_type)
        self.status_bar.showMessage(f"図の種類を{type_name}に変更しました", 2000)
        
        logger.debug(f"Diagram type changed to: {diagram_type}")
    
    def _on_preview_error(self, error_message: str):
        """Handle preview error"""
        self.status_bar.showMessage(f"プレビューエラー: {error_message}", 5000)
        logger.error(f"Preview error: {error_message}")
        
        # Add error to debug tab
        if hasattr(self, 'debug_tab'):
            self.debug_tab.add_log(f"PREVIEW ERROR: {error_message}", "error")
    
    def _load_diagram(self, diagram: 'Diagram'):
        """Load selected diagram from list"""
        try:
            self.current_diagram = diagram
            
            # Set content and type in input panel
            self.input_panel.set_content(diagram.mermaid_data or "")
            self.input_panel.set_diagram_type(diagram.diagram_type)
            
            # Update preview
            self._refresh_preview()
            
            # Update status
            self.status_bar.showMessage(f"図を読み込みました: {diagram.title}", 3000)
            logger.info(f"Diagram loaded: {diagram.title}")
            
            # Emit signal
            self.diagram_loaded.emit(diagram)
            
        except Exception as e:
            error_msg = f"図の読み込みに失敗しました: {e}"
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "エラー", error_msg)
            logger.error(f"Failed to load diagram: {e}")
    
    def _on_diagram_deleted(self, diagram_id: int):
        """Handle diagram deletion"""
        if self.current_diagram and self.current_diagram.id == diagram_id:
            self.current_diagram = None
            self.input_panel.clear()
            self.preview_panel.clear()
            
        self.status_bar.showMessage("図が削除されました", 2000)
        logger.info(f"Diagram deleted: {diagram_id}")
    
    def _auto_save(self):
        """Auto-save current diagram"""
        if self.current_diagram and self.input_panel.get_content().strip():
            self.current_diagram.mermaid_data = self.input_panel.get_content()
            self.current_diagram.diagram_type = self.input_panel.get_diagram_type()
            
            try:
                self.db_manager.save_diagram(self.current_diagram)
                logger.debug("Auto-save completed")
            except Exception as e:
                logger.warning(f"Auto-save failed: {e}")
    
    def _on_content_changed(self):
        """Handle content change in input panel"""
        # Update preview if enabled
        if self.config.get('editor.live_preview', True):
            self._refresh_preview()
    
    def _on_diagram_type_changed(self, diagram_type: str):
        """Handle diagram type change"""
        self._refresh_preview()
        self.status_bar.showMessage(f"図の種類を{DiagramType.display_names().get(diagram_type, diagram_type)}に変更しました", 2000)
    
    def _on_diagram_deleted(self, diagram_id: int):
        """Handle diagram deletion"""
        if self.current_diagram and self.current_diagram.id == diagram_id:
            self._new_diagram()
        self.status_bar.showMessage("図を削除しました", 2000)
    
    def _on_preview_error(self, error_message: str):
        """Handle preview error"""
        self.debug_tab.add_error(error_message)
        self.right_tabs.setCurrentWidget(self.debug_tab)
        self.status_bar.showMessage("プレビューエラーが発生しました", 3000)
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "D3-Mind-Flow-Editorについて", 
                         "D3-Mind-Flow-Editor v1.0.0\\n\\n"
                         "D3.jsを使用したマインドマップ・フローチャート・ガントチャート作成ツール\\n\\n"
                         "© 2024 seyaytua")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save current window state
        size = self.size()
        self.config.window_size = (size.width(), size.height())
        
        splitter_sizes = self.main_splitter.sizes()
        self.config.set('ui.splitter_sizes', splitter_sizes)
        
        self.config.save()
        
        logger.info("Application closing")
        event.accept()