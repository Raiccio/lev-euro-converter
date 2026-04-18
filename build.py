"""
Build script for lev-euro-converter
Run this on Windows to create the .exe
"""

import subprocess
import sys
import os


def install_dependencies():
    """Install required packages"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "pyinstaller"])


def build_exe():
    """Build the .exe"""
    print("Building exe...")
    
    # Remove old build files if they exist
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
    
    if os.path.exists("lev-euro-converter.exe"):
        os.remove("lev-euro-converter.exe")
    
    # Build with PyInstaller
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=lev-euro-converter",
        "--windowed",
        "--add-data=converter_numbers.py;.",
        "main.py"
    ])
    
    print("Build complete!")
    print("Executable: dist/lev-euro-converter.exe")


def main():
    print("=" * 50)
    print("lev-euro-converter Build Script")
    print("=" * 50)
    
    # Check if dependencies are installed
    try:
        import docx
        print("python-docx: OK")
    except ImportError:
        install_dependencies()
    
    build_exe()
    
    print("=" * 50)
    print("Done! Find the .exe in dist/ folder")
    print("=" * 50)


if __name__ == "__main__":
    main()