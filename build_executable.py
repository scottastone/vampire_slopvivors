# Just a placeholder for the build script logic
import PyInstaller.__main__
import os

def build():
    # Define assets to include
    # We need to include the config folder and assets folder
    # Format: (source, dest)
    add_data = [
        ('config', 'config'),
        ('assets', 'assets')
    ]
    
    # Construct the --add-data arguments
    # On Windows it is ';', on Linux/Mac it is ':'
    separator = ';' if os.name == 'nt' else ':'
    
    args = [
        'src/main.py',
        '--name=Autoshooter',
        '--onefile',
        '--windowed',
    ]
    
    for source, dest in add_data:
        args.append(f'--add-data={source}{separator}{dest}')
        
    print("Building executable with args:", args)
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
