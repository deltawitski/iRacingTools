import os
import pathlib
import re
import json
import configparser
from iRacingToolsResources import _internal_utils
from PySide6 import QtWidgets
import substance_painter as sp

from PySide6.QtCore import (
    QDateTime, QDir, QLibraryInfo, QSysInfo, Qt,
    QTimer, Slot, qVersion, QSize, QObject, QLoggingCategory)

from PySide6.QtGui import (
    QCursor, QDesktopServices, QGuiApplication, QIcon,
    QKeySequence, QShortcut, QStandardItem,
    QStandardItemModel, QAction)

from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox,
    QCommandLinkButton, QDateTimeEdit, QDial,
    QDialog, QDialogButtonBox, QFileSystemModel,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListView, QMenu, QPlainTextEdit,
    QProgressBar, QPushButton, QRadioButton,
    QScrollBar, QSizePolicy, QSlider, QSpinBox,
    QStyleFactory, QTableWidget, QTabWidget,
    QTextBrowser, QTextEdit, QToolBox, QToolButton,
    QTreeView, QVBoxLayout, QWidget, QFileDialog,
    QToolBar, QWidgetAction, QFrame, QTabBar, QDockWidget)

plugin_widgets      = []
updating_widgets    = []
project_ready       = False
metadata            = sp.project.Metadata("iRacingTools")
main_window         = sp.ui.get_main_window()
cfg                 = configparser.ConfigParser()

user_dir            = pathlib.Path.home()
onedrive_path       = os.environ.get("OneDrive")
iracing_dir         = os.path.join(onedrive_path, "Documents/iRacing")
if not os.path.exists(iracing_dir):
    iracing_dir     = os.path.join(user_dir, "Documents/iRacing")
paints_dir          = os.path.join(iracing_dir, "paint")
script_dir          = os.path.dirname(os.path.abspath(__file__))
resources_dir       = os.path.join(script_dir, "iRacingToolsResources")
cfg_file            = os.path.join(resources_dir, "cfg")
templates_file      = os.path.join(resources_dir, "templates")
paint_info_file     = os.path.join(resources_dir, "paint_info")
with open(templates_file) as file:
    templates_dict = json.load(file)
with open(paint_info_file) as file:
    paint_info_dict = json.load(file)
paint_info_list     = list(paint_info_dict.values())
paint_info_list     = sorted(paint_info_list, key=lambda x: x[0], reverse=False)
car_names           = [i[0] for i in paint_info_list]
paint_folders       = [i[1] for i in paint_info_list]
icon_iracing_white  = QIcon(os.path.join(resources_dir, "icons\\iRacing-Icon-BW-White.svg"))
icon_iracing_color  = QIcon(os.path.join(resources_dir, "icons\\iRacing-Icon-Color-White.svg"))
icon_folder         = QIcon(os.path.join(resources_dir, "icons\\icon_folder.svg"))
icon_clear          = QIcon(os.path.join(resources_dir, "icons\\icon_clear.svg"))
icon_open           = QIcon(os.path.join(resources_dir, "icons\\icon_open.svg"))
icon_settings       = QIcon(os.path.join(resources_dir, "icons\\icon_settings.svg"))
icon_export         = QIcon(os.path.join(resources_dir, "icons\\icon_export.svg"))
icon_mirror         = QIcon(os.path.join(resources_dir, "icons\\icon_mirror.svg"))
icon_mask           = QIcon(os.path.join(resources_dir, "icons\\icon_mask.svg"))
icon_preview        = QIcon(os.path.join(resources_dir, "icons\\icon_preview.svg"))
icon_copy_proj      = QIcon(os.path.join(resources_dir, "icons\\icon_copy_proj.svg"))
icon_paste_proj     = QIcon(os.path.join(resources_dir, "icons\\icon_paste_proj.svg"))
icon_iracing_text   = QIcon(os.path.join(resources_dir, "icons\\iRacing-Inline-Color-White.svg"))
icon_test           = QIcon(os.path.join(resources_dir, "icons\\iRacing-Icon-Color-White.svg")) #DELETE THIS AT SOME POINT

_internal_utils.cfg = cfg
_internal_utils.cfg_file = cfg_file

def get_plugin_dir() -> str:
    output      = None
    user_dir    = pathlib.Path.home()
    plugin_dir  = os.path.join(user_dir, "Documents/iRacing/Adobe/Adobe Substance 3D Painter/python/plugins")
    if os.path.exists(plugin_dir):
        output  = plugin_dir
    return output

def make_export_config(path: str, id: str, driver: str, custom_number: bool, team_paint: bool, decal: bool, index: int) -> dict:
    car = "car"
    if driver is not None:
        car = driver
    num = ""
    if custom_number is True and driver is None:
        num = "_num"
    team = ""
    if team_paint is True and driver is None:
        team = "_team"
    
    texture_set = sp.textureset.get_active_stack()
    
    car_info_list = paint_info_list[index]
    try:
        suffixes = car_info_list[2]
        suffix = suffixes[str(texture_set)]
    except IndexError:
        suffix = ""
    
    def make_base_map() -> dict:
        return {"fileName": "", "channels": [], "parameters": { "fileFormat": "tga",
                                                                "bitDepth": "8",
                                                                "dithering": False,
                                                                "sizeLog2": 11,
                                                                "paddingAlgorithm": "passthrough",
                                                                "dilationDistance": 0 }}
    
    export_config = {}
    export_config["exportPath"] = path
    export_config["exportShaderParams"] = False
    export_config["defaultExportPreset"] = "iracing"
    export_config["exportPresets"] = [{"name": "iracing", "maps": []}]
    albedo_r = {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"}
    albedo_g = {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"}
    albedo_b = {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
    albedo_a = {"destChannel": "A", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "user4"}
    albedo_map = make_base_map()
    albedo_map["fileName"] = f"{car}{num}{team}_{id}{suffix}"
    albedo_map["channels"].extend([albedo_r, albedo_g, albedo_b, albedo_a])
    export_config["exportPresets"][0]["maps"].append(albedo_map)
    if driver is None:
        spec_r = {"destChannel": "R", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "metallic"}
        spec_g = {"destChannel": "G", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "roughness"}
        spec_b = {"destChannel": "B", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "user0"}
        spec_a = {"destChannel": "A", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "user1"}
        spec_map = make_base_map()
        spec_map["fileName"] = f"{car}_spec{team}_{id}{suffix}"
        spec_map["channels"].extend([spec_r, spec_g, spec_b, spec_a])
        export_config["exportPresets"][0]["maps"].append(spec_map)
        if decal is True:
            decal_r = {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "user2"}
            decal_g = {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "user2"}
            decal_b = {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "user2"}
            decal_a = {"destChannel": "A", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "user3"}
            decal_map = make_base_map()
            decal_map["fileName"] = f"{car}_decal{team}_{id}{suffix}"
            decal_map["channels"].extend([decal_r, decal_g, decal_b, decal_a])
            export_config["exportPresets"][0]["maps"].append(decal_map)
    
    export_config["exportList"] = [{"rootPath": f"{texture_set}"}]
    return export_config

def print_metadata():
    global metadata
    keys    = metadata.list()
    values  = []
    types   = []
    out     = "         Metadata:\n\n"
    None if len(keys) >= 0 else print("No Metadata")
    for key in keys:
        value = metadata.get(key)
        values.append(value)
        types.append(type(value))
    for i, key in enumerate(keys):
        line = f"{key} : {values[i]}                    ({types[i]})\n"
        out += line
    print(out)

def find_car_info_key():
    global project_ready
    global metadata
    car = None
    if project_ready:
        car = metadata.get("car")
    if not car:
        path = metadata.get("path")
        if path:
            return car
        mesh_path = sp.project.last_imported_mesh_path()
        if mesh_path:
            car = pathlib.Path(mesh_path).stem
    return car

def find_car_type():
    global project_ready
    global metadata
    car_type = ""
    if project_ready:
        car_type = metadata.get("car_type")
    return car_type

def paint_folder(key):
    folder = paint_info_dict[key][1]
    if folder:
        return folder
    return None

def car_name(key):
    name = paint_info_dict[key][0]
    if name:
        return name
    return None

def paint_path(folder):
    path = os.path.join(paints_dir, folder)
    if path:
        return path
    return None

def find_custom_number_state():
    global project_ready
    global metadata
    state = False
    if project_ready:
        check = metadata.get("custom_number")
        if check:
            state = check
    return state

def find_team_paint_state():
    global project_ready
    global metadata
    state = False
    if project_ready:
        check = metadata.get("team_paint")
        if check:
            state = check
    return state

def find_decal_state():
    global project_ready
    global metadata
    state = False
    if project_ready:
        check = metadata.get("decal")
        if check:
            state = check
    return state

def find_customer_id():
    global project_ready
    global metadata
    global id_file
    if project_ready:
        export_id = metadata.get("export_id")
        if export_id:
            return export_id
        id = _internal_utils.read_cfg("Settings", "customerid")
        if id.isdecimal():
            export_id = id
            return export_id
    newest_file = None
    newest_time = 0
    for filename in os.listdir(iracing_dir):
        if filename.endswith(".log") and filename.startswith("iRacingSim"):
            file_time = os.path.getmtime(os.path.join(iracing_dir, filename))
            if file_time > newest_time:
                newest_time = file_time
                newest_file = os.path.join(iracing_dir, filename)
    if newest_file:
        with open(newest_file, "r") as file:
            content = file.read()
        pattern = r"custID:(.*?) "
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    return None

class ClearButton(QToolButton):
    def __init__(self):
        super().__init__()
        self.setIcon(icon_clear)
        self.setText("Clear")
        self.setToolTip("Clear")
        self.setStyleSheet("QToolButton { margin: 0px; padding: 0px; border: 0px; }")
        size = 10
        self.setIconSize(QSize(size, size))
        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)
        self.setEnabled(False)
        self.hide()

class MainButton(QPushButton):
    def __init__(self, tooltip: str, icon: QIcon):
        super().__init__()
        self.setIcon(icon)
        self.setToolTip(tooltip)
        self.set_style()
    
    def set_style(self):
        size = 25
        icon_size = 21
        style_sheet = f"""
                        QPushButton {{ 
                        margin: 0px; 
                        padding-top: 4px;
                        padding-bottom: 4px;
                        padding-left: 4px;
                        padding-right: 4px;
                        icon-size: {icon_size}px;
                        border: 1px solid #333333;
                        border-radius: 0px;
                        min-width: {size}px;
                        max-width: {size}px;
                        min-height: {size}px;
                        max-height: {size}px;
                        text-align: center;
                        background-color: #333333;
                        }}
                        QPushButton:hover{{
                        background-color: #262626;
                        }}
                        QPushButton:pressed{{
                        background-color: #666666;
                        }}
                        """
        self.setStyleSheet(style_sheet)

class SettingsButton(QPushButton):
    global main_window
    def __init__(self, tooltip: str, widget: QWidget):
        super().__init__()
        self.toolbar = None
        self.orientation = Qt.Orientation.Horizontal
        self.setIcon(icon_settings)
        self.setToolTip(tooltip)
        self.set_style()
        self.menu = QMenu(self)
        self.widget_action = QWidgetAction(main_window)
        self.widget_action.setDefaultWidget(widget)
        self.menu.addAction(self.widget_action)
        self.setMenu(self.menu)

    def set_style(self):
        max_size            = 25
        min_size            = 15
        width               = max_size
        height              = max_size
        icon_size           = 18
        radius              = 13
        top_right_mask      = 1
        bottom_right_mask   = 1
        bottom_left_mask    = 1
        if self.orientation == Qt.Orientation.Horizontal:
            bottom_left_mask    = 0
            width               = min_size
        if self.orientation == Qt.Orientation.Vertical:
            top_right_mask      = 0
            height              = min_size
        style_sheet = f"""
                        QPushButton {{
                        margin: 0px; 
                        padding-top: 4px;
                        padding-bottom: 4px;
                        padding-left: 4px;
                        padding-right: 4px;
                        icon-size: {icon_size}px;
                        border: 1px solid #333333;
                        border-top-left-radius: 0px;
                        border-top-right-radius: {radius*top_right_mask}px;
                        border-bottom-right-radius: {radius*bottom_right_mask}px;
                        border-bottom-left-radius: {radius*bottom_left_mask}px;
                        min-width: {width}px;
                        max-width: {width}px;
                        min-height: {height}px;
                        max-height: {height}px;
                        text-align: center;
                        background-color: #333333;
                        }}
                        QPushButton:hover{{
                        background-color: #262626;
                        }}
                        QPushButton:pressed{{
                        background-color: #666666;
                        }}
                        QPushButton::menu-indicator{{ 
                        image: none; 
                        }}
                        """
        self.setStyleSheet(style_sheet)
    
    def set_toolbar(self, toolbar: QToolBar):
        self.toolbar        = toolbar
        self.orientation    = self.toolbar.orientation()
        self.toolbar.orientationChanged.connect(self.toolbar_moved)
        self.set_style()

    def toolbar_moved(self):
        self.orientation = self.toolbar.orientation()
        self.set_style()

class IconLabel(QPushButton):
    def __init__(self):
        super().__init__()
        self.toolbar = None
        self.orientation = Qt.Orientation.Horizontal
        self.setToolTip("Plugin Info")
        self.set_style()
        self.setIcon(icon_iracing_text)
        
        self.PluginTools = PluginToolsWidget()
        
        self.menu = QMenu(self)
        self.widget_action = QWidgetAction(main_window)
        self.widget_action.setDefaultWidget(self.PluginTools)
        self.menu.addAction(self.widget_action)
        self.setMenu(self.menu)

    def set_style(self):
        height = 25
        width = 108
        icon_size = 100
        if self.orientation == Qt.Orientation.Vertical:
            width = 25
            icon_size = 20
        style_sheet = f"""
                        QPushButton {{ 
                        margin: 0px; 
                        padding-top: 4px;
                        padding-bottom: 4px;
                        padding-left: 4px;
                        padding-right: 4px;
                        icon-size: {icon_size}px;
                        border: 1px solid #333333;
                        border-radius: 0px;
                        min-width: {width}px;
                        max-width: {width}px;
                        min-height: {height}px;
                        max-height: {height}px;
                        text-align: center;
                        background-color: #333333;
                        }}
                        QPushButton:hover{{
                        background-color: #262626;
                        }}
                        QPushButton:pressed{{
                        background-color: #666666;
                        }}
                        QPushButton::menu-indicator{{
                        image: none;
                        }}
                        """
        self.setStyleSheet(style_sheet)

    def set_toolbar(self, toolbar: QToolBar):
        self.toolbar        = toolbar
        self.orientation    = self.toolbar.orientation()
        self.toolbar.orientationChanged.connect(self.toolbar_moved)

    def toolbar_moved(self):
        self.orientation = self.toolbar.orientation()
        if self.orientation == Qt.Orientation.Horizontal:
            self.setIcon(icon_iracing_text)
            self.set_style()
        if self.orientation == Qt.Orientation.Vertical:
            self.setIcon(icon_iracing_color)
            self.set_style()

class DynamicFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.toolbar = None
        self.orientation = Qt.Orientation.Horizontal
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("background-color: #262626;")
    
    def set_toolbar(self, toolbar: QToolBar):
        self.toolbar        = toolbar
        self.orientation    = self.toolbar.orientation()
        self.toolbar.orientationChanged.connect(self.toolbar_moved)

    def toolbar_moved(self):
        self.orientation = self.toolbar.orientation()
        if self.orientation == Qt.Orientation.Horizontal:
            self.setFrameShape(QFrame.VLine)
        if self.orientation == Qt.Orientation.Vertical:
            self.setFrameShape(QFrame.HLine)

def custom_seperator(toolbar: QToolBar):
    separator = DynamicFrame()
    separator.set_toolbar(toolbar)
    toolbar.addSeparator()
    toolbar.addWidget(separator)
    toolbar.addSeparator()

class PluginToolbar:
    global plugin_widgets
    global updating_widgets
    global main_window
    global project_ready
    def __init__(self):
        super().__init__()
        self.toolbar = sp.ui.add_toolbar("iRacingTools", "iRacingToolsToolbar", 1)
        plugin_widgets.append(self.toolbar)
        updating_widgets.append(self)
        self.toolbar_layout = self.toolbar.layout()
        self.toolbar_layout.setSpacing(0)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        custom_seperator(self.toolbar)
        
        self.iracing_icon = IconLabel()
        self.toolbar.addWidget(self.iracing_icon)
        self.iracing_icon.set_toolbar(self.toolbar)

        custom_seperator(self.toolbar)

        self.export_button = ExportWidget()
        self.toolbar.addWidget(self.export_button)
        
        self.export_settings                 = ExportSettingsWidget()
        self.export_settings_button          = SettingsButton("Export Settings", self.export_settings)
        self.toolbar.addWidget(self.export_settings_button)
        self.export_settings_button.set_toolbar(self.toolbar)
        self.export_settings.host            = self.export_settings_button
        self.export_button.settings_widget   = self.export_settings
        
        custom_seperator(self.toolbar)
        
        self.mirror_button = Mirror()
        self.toolbar.addWidget(self.mirror_button)
        self.mask_button = Mask()
        self.toolbar.addWidget(self.mask_button)
        self.copy_proj_button = CopyProj()
        self.toolbar.addWidget(self.copy_proj_button)
        self.paste_proj_button = PasteProj()
        self.toolbar.addWidget(self.paste_proj_button)
        self.preview_button = Preview()
        self.toolbar.addWidget(self.preview_button)
        
        custom_seperator(self.toolbar)
        
        self.metadata_check = QToolButton()
        self.toolbar.addWidget(self.metadata_check)
        self.metadata_check.setIcon(icon_test)
        self.metadata_check.clicked.connect(print_metadata)

    def project_change(self):
        self.export_button.setEnabled(project_ready)
        self.export_settings_button.setEnabled(project_ready)
        self.mirror_button.setEnabled(project_ready)
        self.mask_button.setEnabled(project_ready)
        self.copy_proj_button.setEnabled(project_ready)
        self.paste_proj_button.setEnabled(project_ready)
        self.preview_button.setEnabled(project_ready)
        self.metadata_check.setEnabled(project_ready)
        #self.toolbar.setEnabled(project_ready)
        pass

class Mirror(MainButton):
    global project_ready
    def __init__(self):
        super().__init__("Mirror", icon_mirror)
        self.clicked.connect(self.when_clicked)
        
    def when_clicked(self):
        if project_ready:
            stack = sp.textureset.get_active_stack()
            selected = sp.layerstack.get_selected_nodes(stack)
            for layer in selected:
                if isinstance(layer, (sp.layerstack.FillLayerNode, sp.layerstack.FillEffectNode)):
                    proj_type       = layer.get_projection_mode()
                    if proj_type.name in ["Triplanar", "Planar", "Spherical", "Cylindrical", "Warp"]:
                        proj_params = layer.get_projection_parameters()
                        uv_tiling   = proj_params.uv_transformation.scale
                        proj_params.uv_transformation.scale[0] = -1 * uv_tiling[0]
                        offset      = proj_params.projection_3d.offset
                        proj_params.projection_3d.offset[2]    = -1 * offset[2]
                        rotation    = proj_params.projection_3d.rotation
                        proj_params.projection_3d.rotation[0]  = 180 - rotation[0]
                        proj_params.projection_3d.rotation[2]  = -180 - rotation[2]
                        scale       = proj_params.projection_3d.scale
                        proj_params.projection_3d.scale[0]     = -1 * scale[0]
                        layer.set_projection_parameters(proj_params)

class Mask(MainButton):
    global project_ready
    def __init__(self):
        super().__init__("Mask", icon_mask)
        self.clicked.connect(self.when_clicked)
        
    def when_clicked(self):
        if project_ready:
            stack = sp.textureset.get_active_stack()
            selected = sp.layerstack.get_selected_nodes(stack)
            for layer in selected:
                if isinstance(layer, (sp.layerstack.FillLayerNode, sp.layerstack.GroupLayerNode, 
                                      sp.layerstack.PaintLayerNode, sp.layerstack.InstanceLayerNode)):
                    layer.add_mask(sp.layerstack.MaskBackground.Black)
                    content_position = sp.layerstack.InsertPosition.inside_node(layer, sp.layerstack.NodeStack.Content)
                    mask_position = sp.layerstack.InsertPosition.inside_node(layer, sp.layerstack.NodeStack.Mask)
                    anchor = sp.layerstack.insert_anchor_point_effect(content_position, layer.get_name())
                    fill_mask = sp.layerstack.insert_fill(mask_position)
                    fill_mask.set_name("Anchor Point Mask")
                    source = fill_mask.set_source(None, anchor)
                    source.alpha_matte = sp.source.AlphaMatte.ExtractAlpha

class CopyProj(MainButton):
    global project_ready
    global metadata
    def __init__(self):
        super().__init__("Copy 3D Projection", icon_copy_proj)
        self.clicked.connect(self.when_clicked)
        
    def when_clicked(self):
        if project_ready:
            stack = sp.textureset.get_active_stack()
            selected = sp.layerstack.get_selected_nodes(stack)
            for layer in selected:
                if isinstance(layer, (sp.layerstack.FillLayerNode, sp.layerstack.FillEffectNode)):
                    proj_type       = layer.get_projection_mode()
                    if proj_type.name in ["Triplanar", "Planar", "Spherical", "Cylindrical", "Warp"]:
                        proj_params = layer.get_projection_parameters()
                        proj_3d = {"offset" : proj_params.projection_3d.offset,
                                   "rotation" : proj_params.projection_3d.rotation,
                                   "scale" : proj_params.projection_3d.scale}
                        metadata.set("projection_3d", proj_3d)
        
class PasteProj(MainButton):
    global project_ready
    global metadata
    def __init__(self):
        super().__init__("Paste 3D Projection", icon_paste_proj)
        self.clicked.connect(self.when_clicked)
        
    def when_clicked(self):
        if project_ready:
            stack = sp.textureset.get_active_stack()
            selected = sp.layerstack.get_selected_nodes(stack)
            for layer in selected:
                if isinstance(layer, (sp.layerstack.FillLayerNode, sp.layerstack.FillEffectNode)):
                    proj_type       = layer.get_projection_mode()
                    if proj_type.name in ["Triplanar", "Planar", "Spherical", "Cylindrical", "Warp"]:
                        proj_params = layer.get_projection_parameters()
                        proj_3d = metadata.get("projection_3d")
                        if proj_3d:
                            proj_params.projection_3d.offset    = proj_3d["offset"]
                            proj_params.projection_3d.rotation  = proj_3d["rotation"]
                            proj_params.projection_3d.scale     = proj_3d["scale"]
                            layer.set_projection_parameters(proj_params)

class Preview(MainButton):
    global project_ready
    global main_window
    global plugin_widgets
    def __init__(self):
        super().__init__("Preview", icon_preview)
        self.clicked.connect(self.when_clicked)
        self.content_icon_button: QToolButton = None
        self.dock_widget        = None
        self.base_size          = 256
        self.size               = QSize(self.base_size, self.base_size)
        self.frame              = QFrame()
        self.layout             = QVBoxLayout()
        self.label              = QLabel()
        self.label.setFixedSize(self.size)
        self.layout.addWidget(self.label)
        self.frame.setLayout(self.layout)
    
    def update_preview(self):
        if self.content_icon_button:
            tag = self.content_icon_button.toolTip()
            tag = self.replace_between(tag, "width=", " ", f"{self.base_size}")
            tag = self.replace_between(tag, "height=", ">", f"{self.base_size}")
            self.label.setText(tag)
            
    def replace_between(self, string, start, end, replacement):
        pattern = f"{re.escape(start)}(.*?){re.escape(end)}"
        return re.sub(pattern, f"{start}{replacement}{end}", string)
    
    def when_clicked(self):
        if project_ready:
            if self.dock_widget:
                self.dock_widget.setVisible(not self.dock_widget.isVisible())
            else:
                stack       = sp.textureset.get_active_stack()
                root_layers = sp.layerstack.get_root_layer_nodes(stack)
                dilation    = None
                for layer in root_layers:
                    name    = layer.get_name()
                    if name == "Dilation":
                        dilation = layer
                if dilation:
                    tool_buttons: list[QToolButton] = main_window.findChildren(QToolButton)
                    for tool_button in tool_buttons:
                        if tool_button.objectName() == "wrappedWidget_collapsableButton":
                            if tool_button.isVisible() == True:
                                parent = tool_button.parentWidget().parentWidget()
                                layer_widgets = parent.findChildren(QWidget, "layerWidget")
                                for layer_widget in layer_widgets:
                                    name_frame: QWidget = layer_widget.findChild(QWidget, "name")
                                    label: QLabel = name_frame.findChild(QLabel)
                                    name = label.text()
                                    if name == "Dilation":
                                        self.content_icon_button = layer_widget.findChild(QWidget, "contentIcon")
                                        self.update_preview() 
                    
                    self.dock_widget = sp.ui.add_dock_widget(self.frame)
                    self.dock_widget.setWindowTitle("Preview")
                    self.dock_widget.setObjectName("preview_window")
                    self.dock_widget.setWindowIcon(icon_test)
                    self.dock_widget.setFloating(True)
                    self.dock_widget.setFixedSize(self.dock_widget.sizeHint())
                    self.dock_widget.setWidget(self.frame)
                    self.dock_widget.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)  
                    plugin_widgets.append(self.dock_widget)

class ExportWidget(MainButton):
    global project_ready
    def __init__(self):
        super().__init__("Export", icon_export)
        self.settings_widget: ExportSettingsWidget = None
        self.clicked.connect(self.export)

    def export(self):
        if project_ready:
            driver  = None
            path    = self.settings_widget.path.text()
            id      = self.settings_widget.id_sel.text()
            index   = self.settings_widget.car_sel.currentIndex()
            if path and id:
                name = self.settings_widget.car_sel.currentText()
                if name == "Driver Helmet":
                    driver    = "helmet"
                if name == "Driver Suit":
                    driver    = "suit"
                custom_number = self.settings_widget.custom_numb_sel.isChecked()
                team_paint    = self.settings_widget.team_sel.isChecked()
                decal         = self.settings_widget.decal_sel.isChecked()
                export_config = make_export_config(path, id, driver, custom_number, team_paint, decal, index)
                export_list   = list(sp.export.list_project_textures(export_config).values())
                export_result = sp.export.export_project_textures(export_config)
                exported      = list(export_result.textures.values())
                #print(export_list)
                #print(exported)
            else:
                self.show_settings()

    def show_settings(self):
        if self.settings_widget.host:
            self.settings_widget.host.showMenu()

class PluginToolsWidget(QFrame):
    global project_ready
    global updating_widgets
    global plugin_widgets
    def __init__(self):
        super().__init__()
        plugin_widgets.append(self)
        updating_widgets.append(self)
        self.layout             = QVBoxLayout()
        self.button = QPushButton("Test Button")
        
        self.layout.addWidget(self.button)
        
        self.setLayout(self.layout)
        self.set_defaults()
        
    def set_defaults(self):
        pass
    
    def project_change(self):
        global metadata
        self.setEnabled(project_ready)
        if project_ready:
            self.set_defaults()

class ExportSettingsWidget(QFrame):
    global project_ready
    global updating_widgets
    global plugin_widgets
    def __init__(self):
        super().__init__()
        plugin_widgets.append(self)
        updating_widgets.append(self)
        self.host: QPushButton  = None
        self.layout             = QVBoxLayout()
        self.label              = QLabel("Export Settings")
        self.line1              = QHBoxLayout()
        self.line2              = QHBoxLayout()
        self.line3              = QHBoxLayout()
        self.car_sel            = QComboBox()
        self.car_type_sel       = QComboBox()
        self.path_layout        = QHBoxLayout()
        self.path               = QLineEdit()
        self.path_clear         = ClearButton()
        self.path_sel           = QToolButton()
        self.path_open          = QToolButton()
        self.id_layout          = QHBoxLayout()
        self.id_sel             = QLineEdit()
        self.id_clear           = ClearButton()
        self.custom_numb_sel    = QCheckBox()
        self.team_sel           = QCheckBox()
        self.decal_sel          = QCheckBox()

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.line1)
        self.layout.addLayout(self.line2)
        self.layout.addLayout(self.line3)
        self.layout.addStretch()
        self.line1.addWidget(self.car_sel)
        self.line1.addWidget(self.car_type_sel)
        self.line1.addStretch()
        self.line2.addLayout(self.path_layout)
        self.path_layout.addWidget(self.path)
        self.path_layout.addWidget(self.path_clear)
        self.path_layout.setSpacing(0)
        self.line2.addWidget(self.path_sel)
        self.line2.addWidget(self.path_open)
        self.line3.addLayout(self.id_layout)
        self.id_layout.addWidget(self.id_sel)
        self.id_layout.addWidget(self.id_clear )
        self.id_layout.setSpacing(0)
        self.line3.addSpacing(20)
        self.line3.addWidget(self.custom_numb_sel)
        self.line3.addWidget(self.team_sel)
        self.line3.addWidget(self.decal_sel)
        self.line3.addStretch()
        self.setLayout(self.layout)
        self.setStyleSheet("border: 1px solid #1a1a1a;")
        self.set_defaults()

        self.car_sel.activated.connect(self.car_selected)
        self.car_type_sel.activated.connect(self.car_type_selected)
        self.path_sel.clicked.connect(self.open_file_dialog)
        self.path_open.clicked.connect(self.open_path)
        self.id_sel.textChanged.connect(self.id_changed)
        self.id_sel.editingFinished.connect(self.id_finished)
        self.custom_numb_sel.stateChanged.connect(self.custom_number_change)
        self.team_sel.stateChanged.connect(self.team_paint_change)
        self.decal_sel.stateChanged.connect(self.decal_change)
        self.path_clear.clicked.connect(self.clear_path)
        self.id_clear.clicked.connect(self.clear_id)

        self.dialog = QFileDialog()
        self.dialog.finished.connect(self.file_chosen)
        self.dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

    def set_defaults(self):
        self.label.setStyleSheet("border: 0px solid #1a1a1a;")
        self.car_sel.setPlaceholderText("Select Car")
        self.car_sel.setDisabled(False)
        self.car_sel.addItems(car_names)
        self.car_sel.setStyleSheet("border: 1px solid darkRed;")
        self.car_sel.setToolTip("Select iRacing Car")
        self.car_type_sel.setPlaceholderText("Select Car Type")
        self.car_type_sel.setDisabled(True)
        self.car_type_sel.setToolTip("Select iRacing Car Type")
        self.path.setPlaceholderText("Car Paint Folder")
        self.path.setReadOnly(True)
        self.path.setStyleSheet("border: 1px solid darkRed; ")
        self.path.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.path.setStyleSheet("background-color: #1a1a1a;")
        self.path_sel.setText("...")
        self.path_sel.setToolTip("Select Export Location Manually")
        self.path_sel.setStyleSheet("QToolButton { margin: 0px; padding: 5px; }")
        self.path_sel.setIcon(icon_folder)
        self.path_open.setText("open")
        self.path_open.setToolTip("Open Export Location in File Explorer")
        self.path_open.setStyleSheet("QToolButton { margin: 0px; padding: 5px; }")
        self.path_open.setIcon(icon_open)
        self.id_sel.setPlaceholderText("Enter ID")
        self.id_sel.setToolTip("Enter Customer or Team ID")
        self.id_sel.setStyleSheet("border: 1px solid darkRed;")
        self.id_sel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.id_sel.setFixedWidth(85)
        self.custom_numb_sel.setText("Custom Number")
        self.custom_numb_sel.setToolTip("Toggle Exporting as a Custom Number Paint")
        self.custom_numb_sel.setStyleSheet("border: 0px solid #1a1a1a;")
        self.team_sel.setText("Team Paint")
        self.team_sel.setToolTip("Toggle Exporting as a Team Paint")
        self.team_sel.setStyleSheet("border: 0px solid #1a1a1a;")
        self.decal_sel.setText("Decal")
        self.decal_sel.setToolTip("Toggle Exporting a Decal Texture")
        self.decal_sel.setStyleSheet("border: 0px solid #1a1a1a;")

    def project_change(self):
        global metadata
        self.setEnabled(project_ready)
        if project_ready:
            self.set_defaults()
            cust_id = find_customer_id()
            if cust_id:
                self.id_sel.setText(cust_id)
            current_car = find_car_info_key()
            if current_car:
                current_car_name = car_name(current_car)
                new_index = car_names.index(current_car_name)
                self.car_sel.setCurrentIndex(new_index)
                self.car_selected()
                if self.car_type_sel.isEnabled():
                    current_car_type = find_car_type()
                    if current_car_type:
                        new_index = self.car_type_sel.findText(current_car_type)
                        self.car_type_sel.setCurrentIndex(new_index)
                        self.car_type_selected()
            else:
                path = metadata.get("path")
                if path:
                    self.set_path(path)
                    self.export_dir_changed()
            custom_number_state = find_custom_number_state()
            self.custom_numb_sel.setChecked(custom_number_state)
            team_paint_state = find_team_paint_state()
            self.team_sel.setChecked(team_paint_state)
            decal_state = find_decal_state()
            self.decal_sel.setChecked(decal_state)

        else:
            self.car_sel.clear()
            self.car_sel.setStyleSheet("")
            self.car_type_sel.clear()
            self.car_type_sel.setStyleSheet("")
            self.path.clear()
            self.path.setStyleSheet("background-color: #1a1a1a;")
            self.id_sel.clear()
            self.id_sel.setStyleSheet("")
            self.id_clear.setEnabled(False)
            self.id_clear.hide()
            self.path_clear.setEnabled(False)
            self.path_clear.hide()
            self.path_open.setEnabled(False)

    def clear_path(self):
        self.set_path(path=None)
        self.export_dir_changed()
    
    def clear_id(self):
        self.id_sel.setText("")
        self.id_changed()
    
    def custom_number_change(self):
        global project_ready
        global metadata
        state = self.custom_numb_sel.isChecked()
        if project_ready:
            metadata.set("custom_number", state)

    def team_paint_change(self):
        global project_ready
        global metadata
        state = self.team_sel.isChecked()
        if project_ready:
            metadata.set("team_paint", state)
            
    def decal_change(self):
        global project_ready
        global metadata
        state = self.decal_sel.isChecked()
        if project_ready:
            metadata.set("decal", state)

    def id_finished(self):
        global metadata
        global id_file
        text = self.id_sel.text()
        if text.isdecimal():
            metadata.set("export_id", text)
            _internal_utils.write_cfg("Settings", "customerid", text)
        else:
            self.id_sel.clear()

    def id_changed(self):
        text = self.id_sel.text()
        if text.isdecimal():
            self.id_sel.setStyleSheet("")
            self.id_clear.setEnabled(True)
            self.id_clear.show()
        else:
            self.id_sel.setStyleSheet("border: 1px solid darkRed;")
            self.id_clear.setEnabled(False)
            self.id_clear.hide()

    def open_file_dialog(self):
        global user_dir
        start_dir = ""
        current_path = self.path.text()
        if current_path != "":
            start_dir = current_path
        self.dialog.setDirectory(start_dir)
        self.dialog.open()

    def file_chosen(self, result):
        if result == QFileDialog.Accepted:
            export_dir = self.dialog.selectedFiles()[0]
            self.set_path(export_dir)

            self.export_dir_changed()
        if self.host: 
            self.host.showMenu()
    
    def set_path(self, path):
        self.path.setText(path)
        if path:
            self.path.setStyleSheet("background-color: #1a1a1a;")
            self.path_open.setEnabled(True)
            self.path_clear.setEnabled(True)
            self.path_clear.show()
        else:
            self.path.setStyleSheet("border: 1px solid darkRed; background-color: #1a1a1a;")
            self.path_open.setEnabled(False)
            self.path_clear.setEnabled(False)
            self.path_clear.hide()
            self.car_sel.setStyleSheet("border: 1px solid darkRed;")

    def open_path(self):
        path = self.path.text()
        os.startfile(path)
    
    def car_selected(self):
        global metadata
        
        car     = None
        index   = self.car_sel.currentIndex()
        name    = car_names[index]
        folder  = paint_folders[index]
        if isinstance(folder, str):
            path = paint_path(folder)
            if os.path.exists(path):
                self.set_path(path=path)
                self.update_car_type_box(car_type=None)
                self.car_sel.setStyleSheet("")
        else:
            self.set_path(path=None)
            self.update_car_type_box(car_type=folder)
            self.car_sel.setStyleSheet("")
        for key, value in paint_info_dict.items():
            value = value[0]
            if value == name:
                car = key
                break
        if car:
            metadata.set("car", car)
            metadata.set("path", None)
            if name == "Driver Helmet" or name == "Driver Suit":
                self.custom_numb_sel.setEnabled(False)
                self.team_sel.setEnabled(False)
                self.decal_sel.setEnabled(False)
            else:
                self.custom_numb_sel.setEnabled(True)
                self.team_sel.setEnabled(True)
                self.decal_sel.setEnabled(True)
        else:
            self.custom_numb_sel.setEnabled(False)
            self.team_sel.setEnabled(False)
            self.decal_sel.setEnabled(False)

    def car_type_selected(self):
        global metadata
        folder      = None
        car_index   = self.car_sel.currentIndex()
        car_info    = paint_folders[car_index]
        key         = self.car_type_sel.currentText()
        if key:
            if isinstance(car_info, dict):
                folder = car_info[key]
            path = paint_path(folder)
            if os.path.exists(path):
                self.set_path(path=path)
                self.car_type_sel.setStyleSheet("")
                metadata.set("car_type", key)

    def update_car_type_box(self, car_type):
        if car_type:
            self.car_type_sel.clear()
            car_types   = list(car_type.keys())
            self.car_type_sel.addItems(car_types)
            self.car_type_sel.setDisabled(False)
            self.car_type_sel.setStyleSheet("border: 1px solid darkRed;")
        else:
            self.car_type_sel.clear()
            self.car_type_sel.setDisabled(True)
            self.car_type_sel.setStyleSheet("")

    def export_dir_changed(self):
        global metadata
        path                = self.path.text()
        folder              = os.path.basename(path)
        found_car_name      = None
        found_car_type      = None
        found_car_types     = None
        if folder:
            for index, item in enumerate(paint_folders):
                if isinstance(item, str):
                    if item == folder:
                        found_car_name  = car_names[index]
                elif isinstance(item, dict):
                    for key, value in item.items():
                        if value == folder:
                            found_car_name = car_names[index]
                            found_car_types = paint_folders[index]
                            found_car_type = key

        if found_car_name:
            new_car_index = self.car_sel.findText(found_car_name)
            self.car_sel.setCurrentIndex(new_car_index)
            self.car_sel.setStyleSheet("")
            self.car_selected
            if found_car_type:
                if found_car_types:
                    self.car_type_sel.clear()
                    self.car_type_sel.addItems(found_car_types)
                new_car_type_index = self.car_type_sel.findText(found_car_type)
                self.car_type_sel.setCurrentIndex(new_car_type_index)
                self.car_type_sel.setStyleSheet("")
                self.car_type_sel.setDisabled(False)
            else:
                self.car_type_sel.clear()
                self.car_type_sel.setStyleSheet("")
                self.car_type_sel.setDisabled(True)
        else:
            self.car_sel.setCurrentIndex(-1)
            if path:
                self.car_sel.setStyleSheet("")
            else:
                self.car_sel.setStyleSheet("border: 1px solid darkRed;")
            self.car_type_sel.clear()
            self.car_type_sel.setStyleSheet("")
            self.car_type_sel.setDisabled(True)
        if found_car_name is None:
            metadata.set("path", path)
            metadata.set("car", None)
            metadata.set("car_type", None)
            self.custom_numb_sel.setEnabled(False)
            self.team_sel.setEnabled(False)
            self.decal_sel.setEnabled(False)
        else:
            metadata.set("path", None)
            metadata.set("car", found_car_name)
            self.custom_numb_sel.setEnabled(True)
            self.team_sel.setEnabled(True)
            self.decal_sel.setEnabled(True)
            if found_car_type:
                metadata.set("car_type", found_car_type)
            else:
                metadata.set("car_type", None)

def on_project_change():
    global project_ready
    global updating_widgets
    widget: QObject
    for widget in updating_widgets:
        if isinstance(widget, ExportSettingsWidget):
            widget.project_change()
        elif isinstance(widget, PluginToolbar):
            widget.project_change()

def on_edition_start( arg ):
    global project_ready
    project_ready = True
    on_project_change()

def on_edition_stop( arg ):
    global project_ready
    project_ready = False
    on_project_change()

def project_closing( arg ):
    pass

def on_plugin_start():
    global project_ready
    global main_window
    if sp.project.is_open():
        project_ready = sp.project.is_in_edition_state()
    else:
        project_ready = False
    on_project_change()

def start_plugin():
    PluginToolbar()
    on_plugin_start()
    sp.event.DISPATCHER.connect(sp.event.ProjectEditionEntered, on_edition_start)
    sp.event.DISPATCHER.connect(sp.event.ProjectEditionLeft, on_edition_stop)
    sp.event.DISPATCHER.connect(sp.event.ProjectAboutToClose, project_closing)

def close_plugin():
    global plugin_widgets
    sp.event.DISPATCHER.disconnect(sp.event.ProjectEditionEntered, on_edition_start)
    sp.event.DISPATCHER.disconnect(sp.event.ProjectEditionLeft, on_edition_stop)
    sp.event.DISPATCHER.disconnect(sp.event.ProjectAboutToClose, project_closing)
    for widget in plugin_widgets:
        sp.ui.delete_ui_element(widget)
    plugin_widgets.clear()

if __name__ == "__main__":
    start_plugin()