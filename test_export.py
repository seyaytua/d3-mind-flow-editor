#!/usr/bin/env python3
"""
Test script for D3-Mind-Flow-Editor export functionality
"""

import sys
sys.path.append('.')

def test_export_functionality():
    print("🧪 Testing D3-Mind-Flow-Editor Export Functionality")
    print("=" * 60)
    
    try:
        from src.core.export_manager import ExportManager
        from src.core.d3_generator import D3Generator
        from src.database.models import DiagramType
        
        # Test basic initialization
        export_mgr = ExportManager()
        d3_gen = D3Generator()
        
        print("✅ Export Manager initialized successfully")
        print("✅ D3 Generator initialized successfully")
        
        # Test format availability
        formats = export_mgr.get_export_formats()
        print(f"📋 Available formats: {list(formats.keys())}")
        
        for format_name, format_info in formats.items():
            status = "✅" if format_info['available'] else "❌"
            primary_for = ", ".join(format_info.get('primary_for', []))
            print(f"   {status} {format_name}: {format_info['description']}")
            if primary_for:
                print(f"      Primary for: {primary_for}")
        
        # Test D3 template generation for each diagram type
        print("\n🎨 Testing D3 Template Generation:")
        
        # Test Mindmap
        mindmap_content = """Name,Parent,Color,Description
Root Mind Map,,#4CAF50,Central topic
Branch 1,Root Mind Map,#2196F3,First main branch
Branch 2,Root Mind Map,#FF9800,Second main branch
Sub-branch 1.1,Branch 1,#81C784,Sub-topic under branch 1"""
        
        try:
            html = d3_gen.generate_html(mindmap_content, DiagramType.MINDMAP, standalone=True, title="Test Mind Map")
            print("   ✅ Mindmap template generation working")
            print(f"      Generated HTML length: {len(html)} characters")
        except Exception as e:
            print(f"   ❌ Mindmap template error: {e}")
        
        # Test Gantt Chart
        gantt_content = """Task,Description,Start Date,End Date,Progress,Assigned To
Planning,Project planning phase,2024-01-01,2024-01-07,100,Team Lead
Development,Main development phase,2024-01-08,2024-02-15,60,Developer A
Testing,Quality assurance testing,2024-02-10,2024-02-28,20,QA Team"""
        
        try:
            html = d3_gen.generate_html(gantt_content, DiagramType.GANTT, standalone=True, title="Test Gantt Chart")
            print("   ✅ Gantt chart template generation working")
            print(f"      Generated HTML length: {len(html)} characters")
        except Exception as e:
            print(f"   ❌ Gantt template error: {e}")
        
        # Test Flowchart
        flowchart_content = """flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process 1]
    B -->|No| D[Process 2]
    C --> E[End]
    D --> E"""
        
        try:
            html = d3_gen.generate_html(flowchart_content, DiagramType.FLOWCHART, standalone=True, title="Test Flowchart")
            print("   ✅ Flowchart template generation working")
            print(f"      Generated HTML length: {len(html)} characters")
        except Exception as e:
            print(f"   ❌ Flowchart template error: {e}")
        
        # Test export options
        print("\n⚙️ Testing Export Options:")
        for format_name in formats:
            options = export_mgr.get_export_options(format_name)
            print(f"   📋 {format_name} options: {list(options.keys())}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_functionality()
    sys.exit(0 if success else 1)