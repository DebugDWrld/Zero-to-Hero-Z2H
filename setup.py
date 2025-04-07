import subprocess, sys

def check_dependencies():
    # Make sure that pip is installed.
    try:
        import pip
    except ImportError:
        print("pip not detected, installing...")
        subprocess.check_call(['python', '-m', 'ensurepip', '--upgrade'])
        print("pip installed successfully.")
        sys.exit(0)
    else:
        print("pip has been installed, the version is: ", pip.__version__)
    
    #Make sure pygame is installed.
    try:
        import pygame
    except ImportError:
        print("Pygame not detected, installing...")
        subprocess.check_call(['pip', 'install', 'pygame'])
        print("Pygame installed successfully.")
    else:
        print("Pygame has been installed, the version is: ", pygame.__version__)

if __name__ == "__main__":
    check_dependencies()