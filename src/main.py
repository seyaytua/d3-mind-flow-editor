#!/usr/bin/env python3
"""
D3-Mind-Flow-Editor - Main Application Entry Point

A desktop application for creating mind maps, flowcharts, and Gantt charts
using D3.js visualization library with PySide6 interface.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))
sys.path.insert(0, str(src_dir))

# Import PySide6 components with comprehensive compatibility checks
try:
    from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
    from PySide6.QtCore import Qt, QTimer, QTranslator, QLocale
    from PySide6.QtGui import QPixmap, QPainter, QFont, QIcon, QLinearGradient
    
    # Check for PySide6 version compatibility
    import PySide6
    PYSIDE6_VERSION = PySide6.__version__
except ImportError as e:
    print(f"Critical Error: PySide6 import failed: {e}")
    print("Please install PySide6: pip install PySide6>=6.6.0")
    sys.exit(1)

# Application imports with error handling
try:
    import src.ui.main_window as main_window_module
    import src.utils.config as config_module
    import src.utils.logger as logger_module
    import src.utils.resolution_manager as resolution_manager_module
except ImportError as e:
    print(f"Critical Error: Application module import failed: {e}")
    print("Please ensure all src modules are properly installed.")
    sys.exit(1)

# Application metadata
APP_NAME = "D3-Mind-Flow-Editor"
APP_VERSION = "1.0.0"
APP_AUTHOR = "seyaytua"
APP_DESCRIPTION = "D3.js powered Mind Map, Flow Chart, and Gantt Chart Desktop Editor"


class Application(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        # Check if QApplication instance already exists
        existing_app = QApplication.instance()
        if existing_app is not None:
            # Use existing instance
            self.__dict__ = existing_app.__dict__
            return
            
        super().__init__(argv)
        
        # Set application metadata
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        self.setOrganizationName(APP_AUTHOR)
        self.setApplicationDisplayName(APP_NAME)
        
        # Initialize components
        self.config = None
        self.main_window = None
        self.resolution_manager = None
        
        # Setup application
        self._setup_application()
        
    def _setup_application(self):
        """Setup application-wide settings"""
        # Set up high DPI support (PySide6 6.6+ handles this automatically)
        try:
            # Only set these attributes for older PySide6 versions
            # Newer versions (6.6+) handle high DPI automatically
            import PySide6
            version_info = PySide6.__version__.split('.')
            major, minor = int(version_info[0]), int(version_info[1])
            
            if major < 6 or (major == 6 and minor < 6):
                # Only for older versions
                if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                    self.setAttribute(Qt.AA_EnableHighDpiScaling)
                if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                    self.setAttribute(Qt.AA_UseHighDpiPixmaps)
                logger_module.logger.debug(f"Applied HiDPI attributes for PySide6 {PySide6.__version__}")
            else:
                logger_module.logger.debug(f"PySide6 {PySide6.__version__} handles HiDPI automatically")
        except (AttributeError, ImportError, ValueError) as e:
            # Fallback: newer versions handle HiDPI automatically
            logger_module.logger.debug(f"HiDPI setup skipped: {e}")
        
        # Set application style
        self.setStyle('Fusion')  # Modern cross-platform style
        
        # Load configuration
        try:
            self.config = config_module.Config()
            logger_module.logger.info(f"Configuration loaded from: {self.config.config_path}")
        except Exception as e:
            logger_module.logger.error(f"Failed to load configuration: {e}")
            QMessageBox.critical(None, "設定エラー", f"設定の読み込みに失敗しました: {e}")
            sys.exit(1)
        
        # Setup resolution management
        try:
            self.resolution_manager = resolution_manager_module.ResolutionManager(self.config)
            logger_module.logger.info(f"Resolution manager initialized: {self.resolution_manager.get_display_info()}")
        except Exception as e:
            logger_module.logger.warning(f"Resolution manager initialization failed: {e}")
        
        # Setup application icon
        self._setup_app_icon()
        
        # Setup application style sheet
        self._setup_stylesheet()
        
    def _setup_app_icon(self):
        """Setup application icon"""
        # Create a simple icon for now
        # TODO: Replace with actual icon file
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a simple chart icon
        painter.setBrush(Qt.blue)
        painter.setPen(Qt.darkBlue)
        painter.drawEllipse(10, 10, 20, 20)
        painter.drawEllipse(30, 20, 20, 20)
        painter.drawEllipse(20, 35, 20, 20)
        
        # Draw connections
        painter.setPen(Qt.black)
        painter.drawLine(25, 20, 35, 25)
        painter.drawLine(30, 35, 35, 30)
        
        painter.end()
        
        self.setWindowIcon(QIcon(pixmap))
    
    def _setup_stylesheet(self):
        """Setup application stylesheet"""
        # Basic stylesheet for consistent appearance
        stylesheet = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QToolBar {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            spacing: 3px;
            padding: 2px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            padding: 4px;
            margin: 1px;
            border-radius: 3px;
        }
        
        QToolBar QToolButton:hover {
            background-color: #e0e0e0;
            border: 1px solid #c0c0c0;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #d0d0d0;
        }
        
        QTabWidget::pane {
            border: 1px solid #d0d0d0;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #f0f0f0;
            border: 1px solid #d0d0d0;
            padding: 6px 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
        }
        
        QTabBar::tab:hover {
            background-color: #e0e0e0;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #d0d0d0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 5px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            padding: 6px 12px;
            border-radius: 3px;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QPushButton:disabled {
            background-color: #f5f5f5;
            color: #a0a0a0;
        }
        
        QTextEdit, QLineEdit {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
            padding: 4px;
        }
        
        QTextEdit:focus, QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
        
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
        }
        
        QListWidget::item {
            padding: 4px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        QListWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        
        QListWidget::item:hover {
            background-color: #e8f5e8;
        }
        
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            padding: 4px 8px;
            border-radius: 3px;
        }
        
        QComboBox:hover {
            border: 1px solid #4CAF50;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNUw2IDhMOSA1IiBzdHJva2U9IiM2NjY2NjYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
        }
        """
        
        self.setStyleSheet(stylesheet)
    
    def create_splash_screen(self) -> QSplashScreen:
        """Create and show splash screen"""
        # Create splash screen pixmap
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background gradient
        gradient = QLinearGradient(0, 0, 400, 300)
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, Qt.lightGray)
        painter.fillRect(pixmap.rect(), gradient)
        
        # Draw title
        painter.setPen(Qt.black)
        title_font = QFont("Arial", 18, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, APP_NAME)
        
        # Draw version
        version_font = QFont("Arial", 10)
        painter.setFont(version_font)
        painter.drawText(50, 250, f"Version {APP_VERSION}")
        
        # Draw description
        desc_font = QFont("Arial", 9)
        painter.setFont(desc_font)
        painter.setPen(Qt.gray)
        painter.drawText(50, 270, "D3.js powered diagram editor")
        
        painter.end()
        
        # Create splash screen
        splash = QSplashScreen(pixmap)
        splash.setMask(pixmap.mask())
        
        return splash
    
    def run(self):
        """Run the application"""
        try:
            # Show splash screen
            splash = self.create_splash_screen()
            splash.show()
            self.processEvents()
            
            # Initialize main window
            splash.showMessage("メインウィンドウを初期化中...", Qt.AlignBottom | Qt.AlignCenter)
            self.processEvents()
            
            self.main_window = main_window_module.MainWindow()
            
            # Setup main window
            splash.showMessage("UIコンポーネントを設定中...", Qt.AlignBottom | Qt.AlignCenter)
            self.processEvents()
            
            # Show main window
            splash.showMessage("アプリケーションを開始中...", Qt.AlignBottom | Qt.AlignCenter)
            self.processEvents()
            
            # Close splash screen and show main window with proper timer handling
            close_timer = QTimer()
            close_timer.setSingleShot(True)
            close_timer.timeout.connect(splash.close)
            close_timer.start(1000)
            
            show_timer = QTimer()
            show_timer.setSingleShot(True)
            show_timer.timeout.connect(self.main_window.show)
            show_timer.start(1000)
            
            logger_module.logger.info(f"{APP_NAME} v{APP_VERSION} started successfully")
            
            # Start event loop
            return self.exec()
            
        except Exception as e:
            logger_module.logger.critical(f"Fatal error during application startup: {e}")
            
            # Show error dialog
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("致命的エラー")
            error_dialog.setText("アプリケーションの起動に失敗しました。")
            error_dialog.setDetailedText(str(e))
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec()
            
            return 1
    
    def closeEvent(self, event):
        """Handle application close"""
        logger_module.logger.info("Application closing")
        
        # Save configuration
        if self.config:
            try:
                self.config.save()
                logger_module.logger.debug("Configuration saved")
            except Exception as e:
                logger_module.logger.warning(f"Failed to save configuration: {e}")
        
        event.accept()


def setup_exception_handling():
    """Setup global exception handling"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger_module.logger.critical(
            f"Uncaught exception: {exc_type.__name__}: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PySide6
    except ImportError:
        missing_deps.append("PySide6")
    
    try:
        import playwright
    except ImportError:
        missing_deps.append("playwright")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import pypdf
    except ImportError:
        missing_deps.append("pypdf")
    
    if missing_deps:
        print(f"Error: Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point"""
    # Setup platform for headless environment
    import os
    if 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        print("Set Qt platform to offscreen for headless environment")
    
    # Setup exception handling
    setup_exception_handling()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Initialize logging
    logger_module.logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger_module.logger.info(f"Python version: {sys.version}")
    logger_module.logger.info(f"Platform: {sys.platform}")
    
    # Create and run application (handle existing instance)
    existing_app = QApplication.instance()
    if existing_app is not None:
        app = existing_app
        # Re-initialize if needed
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName(APP_AUTHOR)
        app.setApplicationDisplayName(APP_NAME)
    else:
        app = Application(sys.argv)
    
    # Set up signal handling for graceful shutdown
    import signal
    def signal_handler(signum, frame):
        logger_module.logger.info(f"Received signal {signum}, shutting down...")
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run application
    try:
        return app.run()
    except KeyboardInterrupt:
        logger_module.logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger_module.logger.critical(f"Fatal application error: {e}")
        return 1
    finally:
        logger_module.logger.info("Application shutdown complete")


if __name__ == "__main__":
    sys.exit(main())