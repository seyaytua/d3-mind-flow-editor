#!/usr/bin/env python3
"""
Basic startup test for D3-Mind-Flow-Editor
"""

import sys
import os
from pathlib import Path

# Set platform for headless environment
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test critical imports"""
    try:
        print("Testing PySide6 imports...")
        from PySide6.QtWidgets import QApplication, QMainWindow
        from PySide6.QtCore import QTimer
        print("✓ PySide6 imports successful")
        
        print("Testing application imports...")
        from src.utils.logger import logger
        from src.utils.config import Config
        from src.database.models import DiagramType
        print("✓ Application imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_basic_qt():
    """Test basic Qt functionality"""
    try:
        print("Testing Qt application creation...")
        from PySide6.QtWidgets import QApplication, QWidget
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            created_new = True
        else:
            created_new = False
            
        print("✓ QApplication created/found")
        
        # Test widget creation
        widget = QWidget()
        widget.setWindowTitle("Test Widget")
        print("✓ Widget creation successful")
        
        # Test timer
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.setSingleShot(True)
        print("✓ Timer creation successful")
        
        if created_new:
            app.quit()
            
        return True
    except Exception as e:
        print(f"✗ Qt test failed: {e}")
        return False

def test_application_components():
    """Test application component initialization"""
    try:
        print("Testing configuration...")
        from src.utils.config import Config
        config = Config()
        print("✓ Configuration initialization successful")
        
        print("Testing logger...")
        from src.utils.logger import logger
        logger.info("Test log message")
        print("✓ Logger test successful")
        
        print("Testing database models...")
        from src.database.models import DiagramType
        mindmap_type = DiagramType.MINDMAP
        print("✓ Database models test successful")
        
        return True
    except Exception as e:
        print(f"✗ Application components test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 D3-Mind-Flow-Editor - Basic Startup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Qt Functionality Test", test_basic_qt),
        ("Application Components Test", test_application_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed - Application should start successfully!")
        return 0
    else:
        print("⚠️ Some tests failed - Application may have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())