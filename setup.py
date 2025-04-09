# setup.py
import subprocess, sys

# Function to check dependencies and install them if necessary
def check_dependencies():
    # Make sure that pip is installed
    try:
        import pip
        print("pip has been installed, the version is: ", pip.__version__)
    except ImportError:
        print("pip not detected, installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            print("pip installed successfully.")
            import pip
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pip: {e}")
            print("Please run this script with administrator privileges (e.g., 'sudo python script.py').")
            sys.exit(1)
    
    # Make sure pygame is installed
    try:
        import pygame
        print("Pygame has been installed, the version is: ", pygame.__version__)
    except ImportError:
        print("Pygame not detected, installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
            print("Pygame installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Pygame: {e}")
            print("Please run this script with administrator privileges (e.g., 'sudo python script.py').")
            sys.exit(1)

# Main script
if __name__ == "__main__":
    check_dependencies()