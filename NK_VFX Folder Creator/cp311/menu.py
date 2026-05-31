import nuke
import os
import sys

# 1. SETUP PATHS
# Get the directory where this menu.py is located
base_dir = os.path.dirname(__file__) 
# If your script is in the same folder as menu.py, base_dir is enough.
# If it's in a subfolder called 'scripts', use: os.path.join(base_dir, 'scripts')
if base_dir not in sys.path:
    sys.path.append(base_dir)

# 2. DEFINE LAUNCHER
def launch_folder_creator():
    """
    Imports and launches the tool. 
    Using a local import inside the function prevents Nuke from slowing down on startup.
    """
    try:
        import vfx_folder_creator # The name of your .py file
        
        # We store the window in a global variable so Nuke's garbage 
        # collection doesn't delete it (and close the UI) immediately.
        global vfx_folder_tool_instance
        vfx_folder_tool_instance = vfx_folder_creator.VFXFolderCreator()
        vfx_folder_tool_instance.show()
        
    except Exception as e:
        nuke.message(f"Error launching VFX Folder Creator:\n{str(e)}")

# 3. ADD TO NUKE INTERFACE
def add_vfx_menu():
    """Adds the menu and commands to Nuke's top menu bar."""
    # Create a top-level menu
    m = nuke.menu("Nuke").addMenu("NK_Tools")
    
    # Add the command
    # If you have an icon, add icon="path/to/icon.png"
    m.addCommand("VFX Project Folder Creator", "launch_folder_creator()")

# Execute
add_vfx_menu()