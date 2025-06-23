import os
import pathlib
import configparser
import json
import threading

from PySide6.QtCore import Signal, QObject

try:
    import requests
    can_update = True
    
except ImportError:
    import subprocess
    import sys
    
    try:
        python_exe = os.path.join(os.path.dirname(sys.executable), "resources/pythonsdk/python.exe")
        subprocess.check_call([python_exe, "-m", "pip", "install", "requests"])
        import requests
        can_update = True
        
    except subprocess.CalledProcessError:
        can_update = False

cfg = configparser.ConfigParser()
cfg_file = None

def get_data() -> dict:
    output = {}
    plugin_dir = find_substance_plugin_dir()
    if plugin_dir:
        resources_dir = os.path.join(plugin_dir, "iRacingToolsResources")
        data_file = os.path.join(resources_dir, "data")
        if os.path.exists(data_file):
            with open(data_file) as file:
                data_dict = json.load(file)
            if data_dict:
                output = data_dict
        
    return output

def get_cfg_file() -> str:
    global cfg_file
    plugin_dir = find_substance_plugin_dir()
    if plugin_dir:
        resources_dir = os.path.join(plugin_dir, "iRacingToolsResources")
        test_path = os.path.join(resources_dir, "cfg")
        if os.path.exists(test_path):
            cfg_file = test_path
            return cfg_file
        else:
            with open(test_path, 'w') as f:
                pass
            if os.path.exists(test_path):
                cfg_file = test_path
                return cfg_file
            else:
                return None
    else:
        return None

class download_templates(QObject):
    download_prog = Signal(str, float, float)
    download_finished = Signal(list)
    
    def __init__(self, templates: dict):
        super().__init__()
        self.templates_dir = read_cfg("Settings", "templates_dir")
        self.templates = templates
    
        if self.templates_dir and self.templates:
            self.download_thread = threading.Thread(target=self.Download)
            self.download_thread.start()
        
        else:
            if not self.templates_dir:
                self.download_finished.emit(["Couldn't find templates directory."])
            else:
                self.download_finished.emit(["No templates to download."])
            
    def Download(self):
        target = self.templates_dir
        total_seg = 1 / len(self.templates)
        failed = []
        chunk_size = 8192
        for index, (file_name, file_id) in enumerate(self.templates.items()):
            total_start = index / len(self.templates)
            curr_chunk = 0
            
            #try: docs.google.com/uc?export=download&id=FileID
            base_url = "https://docs.google.com/uc"
            session = requests.Session()
            params = {
                "export": "download",
                "id": file_id
            }
            response = session.get(base_url, params=params, stream=True)
            
            os.makedirs(target, exist_ok=True)
            file_path = os.path.join(target, f"{file_name}.spp")

            try:
                total_size = int(response.headers.get('content-length', 0))
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            curr_chunk += len(chunk)
                            curr_prog = curr_chunk / total_size
                            total_prog = total_start + (total_seg * curr_prog)
                            self.download_prog.emit(file_name, curr_prog, total_prog)

            except Exception as exception:
                os.remove(file_path)
                failed.append(f"{file_name} failed to download with exception: {exception}")
                
        self.download_finished.emit(failed)

def get_github_data() -> dict:
    repo_owner = "deltawitski"
    repo_name = "iRacingTools"
    repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/main?recursive=1"
    response = requests.get(repo_url)
    
    file_paths = {}
    exclude_files = ["installer.py", ".gitattributes", "README.md", "iRacingToolsResources/cfg", ".build.py"]
    
    if response.status_code == 200:
        repo_data = response.json()

        if "tree" in repo_data:
            for item in repo_data["tree"]:
                if item["type"] == "blob":
                    path = item["path"]
                    if not path in exclude_files:
                        file_paths[path] = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{path}"
        
    return file_paths

def download_plugin(Path=None) -> bool:
    downloads = {}
    file_paths = get_github_data()
    if file_paths:
        plugin_dir = find_substance_plugin_dir() if Path is None else Path
        
        if not plugin_dir: return False
        
        for path, url in file_paths.items():
            response = requests.get(url)
            
            if response.status_code == 200:
                download_file = os.path.normpath(os.path.join(plugin_dir, path))
                downloads[download_file] = response   
            
            else:
                return False
            
        for download_file, response in downloads.items():
            dir = os.path.dirname(download_file)
            os.makedirs(dir, exist_ok=True)  
            
            with open(download_file, "wb") as file:
                file.write(response.content)
            
        return True

def check_version() -> tuple[bool, bool, str, str]:
    """
    Compares local version of the plugin with the current version on Github.

    Returns
    -------
    tuple[bool, str, str]
        A tuple containing:
        * Bool representing whether files are missing from local version.
        * Bool representing whether the local version matches the current version.
        * String representing the local version
        * String representing the current version on Github
    """
    file_paths = get_github_data()
    if file_paths:
        plugin_dir = find_substance_plugin_dir()
        missing_files = False
        matches_current = False
        local_version = None
        current_version = None
        
        if plugin_dir:
        
            for path, url in file_paths.items():
                local_path = os.path.normpath(os.path.join(plugin_dir, path))
                
                if os.path.basename(path) == "version":
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        content = response.text
                        current_version = content
                
                if os.path.exists(local_path):
                    
                    if os.path.basename(local_path) == "version":
                        
                        with open(local_path, "r") as file:
                            content = file.read()
                            local_version = content
                        
                else:
                    missing_files = True
        
        if local_version != None and current_version != None:
            matches_current = local_version == current_version
        
        output = (missing_files, matches_current, local_version, current_version)
        return output

def is_plugin_installed() -> bool:
    plugin_dir = find_substance_plugin_dir()
    if plugin_dir:
        if os.path.exists(os.path.join(plugin_dir, "iRacingTools.py")):
            return True
        else: return False

def find_substance_plugin_dir():
    user_dir = pathlib.Path.home()
    plugin_dir = os.path.normpath(os.path.join(user_dir, "Documents/Adobe/Adobe Substance 3D Painter/python/plugins"))
    if os.path.exists(plugin_dir): return plugin_dir
    else: return None

def read_cfg(section, option):
    global cfg_file
    value = None
    if cfg_file is None:
        get_cfg_file()
    if os.path.exists(cfg_file):
        cfg.read(cfg_file)
        if cfg.has_section(section):
            if cfg.has_option(section, option):
                value = cfg.get(section, option)
    return value

def write_cfg(section, option, value):
    global cfg_file
    if cfg_file is None:
        get_cfg_file()
    if os.path.exists(cfg_file):
        cfg.read(cfg_file)
        if not cfg.has_section(section):
            cfg.add_section(section)
        cfg.set(section, option, value)
        with open(cfg_file, 'w') as configfile:
            cfg.write(configfile)
        
images = os.path.join(find_substance_plugin_dir(), "iRacingToolsResources/icons/logo.ico")