#!/usr/bin/env python3
"""
Simple entry point for D3-Mind-Flow-Editor
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    
    # Simple test window
    class SimpleTestWindow:
        def __init__(self):
            self.app = QApplication(sys.argv)
            self.show_test_dialog()
        
        def show_test_dialog(self):
            msg = QMessageBox()
            msg.setWindowTitle("D3-Mind-Flow-Editor")
            msg.setText("アプリケーションが正常に起動しました！\n\n主な機能:\n• マインドマップ作成\n• ガントチャート作成\n• フローチャート作成\n• AIプロンプト支援")
            msg.setInformativeText("現在、基本的なUI構造とパーサーが実装されています。")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
        
        def run(self):
            return 0

    if __name__ == "__main__":
        app = SimpleTestWindow()
        sys.exit(app.run())
        
except ImportError as e:
    print(f"PySide6 import error: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)