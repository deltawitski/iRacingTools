import PyInstaller.__main__
import os
from iRacingToolsResources import _internal_utils

current_dir = os.path.dirname(os.path.abspath(__file__))
installer_py = os.path.join(current_dir, 'installer.py')

plugin_dir = _internal_utils.find_substance_plugin_dir()

exe_name = "iRacingTools"

script_name = installer_py
options = [
    "--onefile", 
    "--windowed", 
    "--distpath", current_dir, 
    "--name", exe_name,
    f"--add-data={_internal_utils.images}:images",
    f"--icon={_internal_utils.images}"
]

argument_list = [script_name] + options

PyInstaller.__main__.run(argument_list)