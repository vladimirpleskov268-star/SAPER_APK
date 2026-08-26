import os
import sys
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_tools():
    print("=" * 60)
    print("[*] MINESWEEPER 2D - BUILD & PACKAGING CHECKER")
    print("=" * 60)
    
    # Check Python version
    print(f"[*] Python Version: {sys.version.split()[0]}")
    
    # Check Pygame
    try:
        import pygame
        print(f"[✓] Pygame Version: {pygame.__version__}")
    except ImportError:
        print("[!] Pygame is missing. Run: pip install pygame-ce")
        
    # Check Briefcase
    try:
        import briefcase
        print(f"[✓] Briefcase is installed.")
    except ImportError:
        print("[!] Briefcase is missing. Run: pip install briefcase")
        
    # Check WSL / Linux environment
    wsl_available = False
    try:
        res = subprocess.run(["wsl", "--list"], capture_output=True, text=True)
        if res.returncode == 0:
            wsl_available = True
            print("[✓] WSL (Windows Subsystem for Linux) is detected.")
        else:
            print("[!] WSL is not installed on this machine.")
    except Exception:
        print("[!] WSL is not available.")
        
    print("\n" + "=" * 60)
    print("🚀 HOW TO BUILD YOUR APK FILE:")
    print("=" * 60)
    print("METHOD 1: GitHub Actions (Recommended 1-Click Free Build in Cloud)")
    print("  1. Push this folder to a GitHub repository.")
    print("  2. Go to 'Actions' tab on GitHub.")
    print("  3. Click 'Build Android APK' -> 'Run workflow'.")
    print("  4. Download the ready .apk file from Artifacts!\n")
    
    print("METHOD 2: Buildozer (via WSL / Linux / Google Colab)")
    print("  1. Run: pip install buildozer cython")
    print("  2. Run: buildozer android debug")
    print("  3. Your APK will be created in bin/Minesweeper2D-1.0.0-debug.apk\n")
    
    print("METHOD 3: Local Desktop Run (PC / Test)")
    print("  Run: python main.py")
    print("=" * 60)

if __name__ == "__main__":
    check_tools()
