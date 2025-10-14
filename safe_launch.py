#!/usr/bin/env python3
"""
Safe launch script for D3-Mind-Flow-Editor
Comprehensive pre-flight checks and graceful error handling
"""

import sys
import os
import traceback
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))


def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print(f"Error: Python 3.8+ required, found {sys.version}")
        return False
    print(f"✓ Python version: {sys.version}")
    return True


def check_pyside6():
    """Check PySide6 availability and version"""
    try:
        import PySide6
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        version = PySide6.__version__
        print(f"✓ PySide6 version: {version}")
        
        # Test basic Qt functionality with offscreen platform for headless environment
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            created_app = True
        else:
            created_app = False
            
        timer = QTimer()
        
        if created_app:
            app.quit()
        
        print("✓ PySide6 basic functionality test passed (offscreen mode)")
        return True
        
    except ImportError as e:
        print(f"✗ PySide6 import error: {e}")
        print("Please install: pip install PySide6>=6.6.0")
        return False
    except Exception as e:
        print(f"✗ PySide6 functionality test failed: {e}")
        return False


def check_webengine():
    """Check WebEngine availability (optional)"""
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("✓ WebEngine available")
        return True
    except ImportError:
        print("⚠ WebEngine not available - preview may be limited")
        return False


def check_playwright():
    """Check Playwright availability (optional for export)"""
    try:
        import playwright
        try:
            version = playwright.__version__
        except AttributeError:
            version = "version unknown"
        print(f"✓ Playwright available: {version}")
        return True
    except ImportError:
        print("⚠ Playwright not available - export functionality may be limited")
        return False
    except Exception as e:
        print(f"⚠ Playwright check failed: {e}")
        return False


def check_application_modules():
    """Check application module availability"""
    try:
        # Test core imports
        from src.utils.logger import logger
        from src.utils.config import Config
        from src.database.models import DiagramType
        from src.core.d3_generator import D3Generator
        
        print("✓ Core application modules available")
        return True
        
    except ImportError as e:
        print(f"✗ Application module import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Application module test failed: {e}")
        return False


def run_safe_mode():
    """Run application in safe mode with minimal functionality"""
    print("\n🛡️ Starting in SAFE MODE...")
    
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import Qt
        
        # Set offscreen platform for headless environment
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        # Use existing QApplication instance if available
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create simple safe mode window
        window = QWidget()
        window.setWindowTitle("D3-Mind-Flow-Editor - Safe Mode")
        window.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Status message
        status_label = QLabel("アプリケーションはセーフモードで動作しています。\n\n一部の機能が制限されている可能性があります。\n完全な機能を使用するには、依存関係を確認してください。")
        status_label.setWordWrap(True)
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        
        # Close button
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(window.close)
        layout.addWidget(close_button)
        
        window.setLayout(layout)
        window.show()
        
        print("✓ Safe mode window displayed")
        return app.exec()
        
    except Exception as e:
        print(f"✗ Safe mode failed: {e}")
        print("Critical error - cannot continue")
        return 1


def run_full_mode():
    """Run application in full mode"""
    print("\n🚀 Starting in FULL MODE...")
    
    try:
        # Set offscreen platform for headless environment
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        # Import and run the main application
        from src.main import main
        return main()
        
    except Exception as e:
        print(f"✗ Full mode startup failed: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        print(f"\n⚠️ Falling back to safe mode...")
        return run_safe_mode()


def main():
    """Main entry point with comprehensive checks"""
    print("🔍 D3-Mind-Flow-Editor - Safe Launch")
    print("=" * 50)
    
    # Pre-flight checks
    checks_passed = 0
    total_checks = 0
    
    # Essential checks
    if check_python_version():
        checks_passed += 1
    total_checks += 1
    
    if check_pyside6():
        checks_passed += 1
    total_checks += 1
    
    if check_application_modules():
        checks_passed += 1
    total_checks += 1
    
    # Optional checks (don't affect startup decision)
    check_webengine()
    check_playwright()
    
    print(f"\n📊 Essential checks: {checks_passed}/{total_checks} passed")
    
    # Decide startup mode
    if checks_passed == total_checks:
        return run_full_mode()
    elif checks_passed >= 2:  # At least Python and PySide6
        print("\n⚠️ Some checks failed - attempting full mode with fallbacks...")
        return run_full_mode()
    else:
        print("\n🛡️ Critical checks failed - starting in safe mode...")
        return run_safe_mode()


if __name__ == "__main__":
    sys.exit(main())