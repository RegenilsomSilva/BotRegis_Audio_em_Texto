import os
import shutil
import sys

def copy_pysimplegui():
    """Copy PySimpleGUI from system installation to virtual environment"""
    try:
        # Source: Installed PySimpleGUI location
        source = r"C:\Users\RegenilsonSilveira\AppData\Local\Programs\Python\Python311\Lib\site-packages\PySimpleGUI"
        
        # Destination: Virtual environment
        venv_path = os.path.join(os.path.dirname(__file__), '.env')
        dest = os.path.join(venv_path, 'Lib', 'site-packages', 'PySimpleGUI')
        
        if os.path.exists(source):
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            # Copy the package
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
            
            print("✅ PySimpleGUI copied successfully to virtual environment")
            return True
    except Exception as e:
        print(f"❌ Error copying PySimpleGUI: {e}")
        return False

if __name__ == "__main__":
    copy_pysimplegui()