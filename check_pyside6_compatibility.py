#!/usr/bin/env python3
"""
PySide6 6.10+ Compatibility Check Tool
For D3-Mind-Flow-Editor
"""

def check_pyside6_compatibility():
    """Check PySide6 compatibility and available attributes"""
    
    print("🔍 PySide6 Compatibility Check")
    print("=" * 50)
    
    try:
        import PySide6
        print(f"✅ PySide6 Version: {PySide6.__version__}")
        
        # Check WebEngine availability
        try:
            from PySide6.QtWebEngineCore import QWebEngineSettings
            print("✅ QtWebEngineCore imported successfully")
            
            # Check WebAttribute structure
            if hasattr(QWebEngineSettings, 'WebAttribute'):
                print("✅ WebAttribute class found")
                web_attr = QWebEngineSettings.WebAttribute
                
                # Check critical attributes
                critical_attrs = [
                    'JavascriptEnabled',
                    'LocalContentCanAccessRemoteUrls', 
                    'LocalContentCanAccessFileUrls',
                    'DeveloperExtrasEnabled'  # This is the problematic one
                ]
                
                available_attrs = []
                missing_attrs = []
                
                for attr in critical_attrs:
                    if hasattr(web_attr, attr):
                        available_attrs.append(attr)
                    else:
                        missing_attrs.append(attr)
                
                print(f"✅ Available attributes: {available_attrs}")
                print(f"❌ Missing attributes: {missing_attrs}")
                
            else:
                print("❌ WebAttribute class not found - checking direct attributes")
                
                # Check direct attributes on QWebEngineSettings
                critical_attrs = [
                    'JavascriptEnabled',
                    'LocalContentCanAccessRemoteUrls',
                    'LocalContentCanAccessFileUrls',
                    'DeveloperExtrasEnabled'
                ]
                
                for attr in critical_attrs:
                    if hasattr(QWebEngineSettings, attr):
                        print(f"✅ Direct attribute available: {attr}")
                    else:
                        print(f"❌ Direct attribute missing: {attr}")
            
            # Test basic WebEngine functionality
            try:
                from PySide6.QtWebEngineWidgets import QWebEngineView
                print("✅ QWebEngineView import successful")
            except ImportError as e:
                print(f"❌ QWebEngineView import failed: {e}")
                
        except ImportError as e:
            print(f"❌ QtWebEngineCore import failed: {e}")
            
        # Check Qt Application
        try:
            from PySide6.QtWidgets import QApplication
            print("✅ QApplication import successful")
        except ImportError as e:
            print(f"❌ QApplication import failed: {e}")
            
    except ImportError as e:
        print(f"❌ PySide6 import failed: {e}")
        return False
        
    print("\n🎯 Compatibility Summary:")
    print("- PySide6 6.10+ changes WebEngine attribute structure")
    print("- DeveloperExtrasEnabled is removed (safe to skip)")
    print("- Use try/catch for all WebEngine settings")
    print("- Application should work with minimal settings")
    
    return True

if __name__ == "__main__":
    check_pyside6_compatibility()