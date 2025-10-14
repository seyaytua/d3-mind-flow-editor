#!/usr/bin/env python3
"""
Complete integration test for D3-Mind-Flow-Editor
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir.parent))
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing module imports...")
    
    try:
        # Core modules  
        from src.core.csv_parser import parse_mindmap_csv, parse_gantt_csv
        from src.core.d3_generator import D3Generator
        from src.core.export_manager import ExportManager
        from src.core.mermaid_parser import MermaidParser
        
        # Database modules
        from src.database.db_manager import DatabaseManager
        from src.database.models import Diagram, DiagramType
        
        # Utility modules
        from src.utils.config import Config
        from src.utils.logger import logger
        from src.utils.resolution_manager import ResolutionManager
        from src.utils.clipboard import ClipboardManager
        
        # UI modules (without creating instances that need display)
        # from src.ui.main_window import MainWindow
        from src.ui.input_panel import InputPanel
        from src.ui.preview_panel import PreviewPanel
        from src.ui.list_panel import ListPanel
        from src.ui.debug_tab import DebugTab
        from src.ui.help_tab import HelpTab
        from src.ui.settings_tab import SettingsTab
        from src.ui.dialogs import SaveDialog, ExportDialog
        
        print("✅ All core modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_csv_parsing():
    """Test CSV parsing functionality"""
    print("\n🔍 Testing CSV parsing...")
    
    try:
        from src.core.csv_parser import parse_mindmap_csv, parse_gantt_csv
        
        # Test mindmap CSV
        mindmap_csv = """プロジェクト,,,
,企画,,
,,市場調査,
,,競合分析,
,開発,,
,,設計,
,,,UI設計
,,,DB設計
,,実装,"""
        
        mindmap_data = parse_mindmap_csv(mindmap_csv)
        
        assert mindmap_data["name"] == "プロジェクト"
        assert len(mindmap_data["children"]) == 2
        print("✅ Mindmap CSV parsing works")
        
        # Test Gantt CSV
        gantt_csv = """task,start,end,category,progress,dependencies
要件定義,2024-01-01,2024-01-15,Phase1,1.0,
基本設計,2024-01-10,2024-01-25,Phase1,0.8,要件定義
詳細設計,2024-01-20,2024-02-10,Phase2,0.5,基本設計"""
        
        gantt_data = parse_gantt_csv(gantt_csv)
        
        assert len(gantt_data) == 3
        assert gantt_data[0]["task"] == "要件定義"
        print("✅ Gantt CSV parsing works")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV parsing error: {e}")
        return False

def test_d3_generation():
    """Test D3.js template generation"""
    print("\n🔍 Testing D3.js template generation...")
    
    try:
        from src.core.d3_generator import D3Generator
        from src.database.models import DiagramType
        
        generator = D3Generator()
        
        # Test mindmap generation
        mindmap_data = {
            "name": "テスト",
            "children": [
                {"name": "子1", "children": []},
                {"name": "子2", "children": []}
            ]
        }
        
        html_content = generator.generate_html("test content", DiagramType.MINDMAP, mindmap_data)
        assert "<!DOCTYPE html>" in html_content
        assert "d3.js" in html_content or "D3" in html_content
        print("✅ D3.js mindmap generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ D3 generation error: {e}")
        return False

def test_mermaid_parsing():
    """Test Mermaid parsing functionality"""
    print("\n🔍 Testing Mermaid parsing...")
    
    try:
        from src.core.mermaid_parser import MermaidParser
        
        mermaid_code = """flowchart TD
    A[開始] --> B{条件分岐}
    B -->|Yes| C[処理1]
    B -->|No| D[処理2]
    C --> E[終了]
    D --> E"""
        
        parsed_data = MermaidParser.parse_mermaid(mermaid_code)
        
        assert parsed_data is not None
        assert "nodes" in parsed_data
        assert "edges" in parsed_data
        print("✅ Mermaid parsing works")
        
        return True
        
    except Exception as e:
        print(f"❌ Mermaid parsing error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database functionality...")
    
    try:
        from src.database.db_manager import DatabaseManager
        from src.database.models import Diagram, DiagramType
        
        # Create test database
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        db_manager = DatabaseManager(db_path)
        
        # Test saving a diagram
        diagram = Diagram()
        diagram.title = "テストダイアグラム"
        diagram.diagram_type = DiagramType.MINDMAP
        diagram.mermaid_data = "test content"
        diagram.description = "テスト説明"
        
        saved_diagram_id = db_manager.save_diagram(diagram)
        assert saved_diagram_id is not None
        assert isinstance(saved_diagram_id, int)
        print("✅ Database save works")
        
        # Test loading diagrams
        diagrams = db_manager.get_all_diagrams()
        assert len(diagrams) >= 1
        print("✅ Database load works")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("\n🔍 Testing configuration management...")
    
    try:
        from src.utils.config import Config
        
        config = Config()
        
        # Test default values
        assert config.png_dpi > 0
        assert config.dpi_scaling in ["auto", "100%", "150%", "200%", "300%"]
        print("✅ Configuration defaults work")
        
        # Test setting values
        original_dpi = config.png_dpi
        config.png_dpi = 150
        assert config.png_dpi == 150
        
        # Restore
        config.png_dpi = original_dpi
        print("✅ Configuration setting works")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_ai_prompts():
    """Test AI prompt functionality"""
    print("\n🔍 Testing AI prompt system...")
    
    try:
        # Check that prompt files exist
        prompt_dir = Path("src/assets/prompts")
        
        mindmap_prompt = prompt_dir / "mindmap_prompt.txt"
        gantt_prompt = prompt_dir / "gantt_prompt.txt"
        flowchart_prompt = prompt_dir / "flowchart_prompt.txt"
        
        assert mindmap_prompt.exists(), "Mindmap prompt file missing"
        assert gantt_prompt.exists(), "Gantt prompt file missing"
        assert flowchart_prompt.exists(), "Flowchart prompt file missing"
        
        # Test prompt content
        mindmap_content = mindmap_prompt.read_text(encoding='utf-8')
        assert "CSV形式" in mindmap_content
        assert "マインドマップ" in mindmap_content
        print("✅ AI prompt files exist and contain expected content")
        
        return True
        
    except Exception as e:
        print(f"❌ AI prompt error: {e}")
        return False

def test_d3_templates():
    """Test D3.js template files"""
    print("\n🔍 Testing D3.js template files...")
    
    try:
        template_dir = Path("src/assets/d3_templates")
        
        mindmap_template = template_dir / "mindmap.html"
        gantt_template = template_dir / "gantt.html"
        flowchart_template = template_dir / "flowchart.html"
        
        assert mindmap_template.exists(), "Mindmap template missing"
        assert gantt_template.exists(), "Gantt template missing"
        assert flowchart_template.exists(), "Flowchart template missing"
        
        # Test template content
        mindmap_content = mindmap_template.read_text(encoding='utf-8')
        assert "<!DOCTYPE html>" in mindmap_content
        assert "d3" in mindmap_content
        assert "{{DIAGRAM_DATA}}" in mindmap_content
        print("✅ D3.js template files exist and contain expected placeholders")
        
        return True
        
    except Exception as e:
        print(f"❌ D3 template error: {e}")
        return False

async def test_export_functionality():
    """Test export functionality (async)"""
    print("\n🔍 Testing export functionality...")
    
    try:
        from src.core.export_manager import ExportManager
        from src.utils.config import Config
        from src.utils.resolution_manager import ResolutionManager
        
        # Create QApplication instance for resolution manager (headless)
        try:
            from PySide6.QtWidgets import QApplication
            import os
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            app = QApplication.instance()
            if app is None:
                app = QApplication(['test'])
        except:
            pass  # Skip GUI components in headless environment
            
        config = Config()
        resolution_manager = ResolutionManager(config)
        export_manager = ExportManager(config, resolution_manager)
        
        # Test HTML content for export
        test_html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Test Content</h1></body>
</html>"""
        
        # Test export method exists
        assert hasattr(export_manager, 'export_diagram'), "Export diagram method missing"
        assert callable(getattr(export_manager, 'export_diagram')), "Export diagram not callable"
        print("✅ Export diagram method available")
        
        # Test that _generate_standalone_html method exists
        assert hasattr(export_manager, '_generate_standalone_html'), "_generate_standalone_html method missing"
        print("✅ HTML generation method available")
        
        return True
        
    except Exception as e:
        print(f"❌ Export functionality error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting D3-Mind-Flow-Editor Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("CSV Parsing", test_csv_parsing),
        ("D3.js Generation", test_d3_generation),
        ("Mermaid Parsing", test_mermaid_parsing),
        ("Database", test_database),
        ("Configuration", test_configuration),
        ("AI Prompts", test_ai_prompts),
        ("D3.js Templates", test_d3_templates),
        ("Export Functionality", lambda: asyncio.run(test_export_functionality())),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! D3-Mind-Flow-Editor is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())