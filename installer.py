import sys
import os
import threading

from iRacingToolsResources import _internal_utils

from iRacingToolsResources._internal_utils import images

from PySide6.QtCore import Qt, QSize, Signal, QRect
from PySide6.QtGui import QPalette, QColor, QIcon, QShowEvent, QFont, QPainter, QBrush
from PySide6.QtWidgets import ( 
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QStackedWidget, QPushButton, QProgressBar, 
    QLabel, QLineEdit, QFileDialog, QToolButton, QMessageBox, 
    QFrame, QSizePolicy, QListWidget, QListWidgetItem
)

app = QApplication(sys.argv)
app.setStyle('Fusion')

bg_dark     = QColor(43, 43, 43)
bg_light    = QColor(51, 51, 51)
ir_red      = QColor(212, 43, 39)
ir_blue     = QColor(34, 68, 136)
bg_shadow   = QColor(38, 38, 38)

palette = QPalette()
palette.setColor(QPalette.Window, bg_light) #Window Background
palette.setColor(QPalette.Base, bg_dark) #Title Bar
palette.setColor(QPalette.ColorRole.Base, bg_light) #Alternating BG Colors
palette.setColor(QPalette.ColorRole.AlternateBase, bg_shadow) #Alternating BG Colors
palette.setColor(QPalette.ColorRole.Highlight, ir_blue)

app.setPalette(palette)

base_dir = os.path.dirname(__file__)
logo_path = os.path.join(base_dir, "iRacingToolsResources/icons/logo.ico")
icon_iracing_color = QIcon(logo_path)

def GetCustomerID() -> str:
    id = _internal_utils.read_cfg("Settings", "customerid")
    if id and id.isdecimal():
        return id
    else:
        return None

def GetPaintsDir() -> str:
    dir = _internal_utils.read_cfg("Settings", "paints_dir")
    if dir and os.path.exists(dir):
        return dir
    else:
        return None

def GetTemplateDir() -> str:
    dir = _internal_utils.read_cfg("Settings", "templates_dir")
    if dir and os.path.exists(dir):
        return dir
    else:
        return None

def Download(parent, Path=None):
    if _internal_utils.download_plugin(Path) == True:
        parent.Downloaded()
        
class TextEntry(QLineEdit):
    def __init__(self, Parent, Width, FontSize):
        super().__init__()
        self.parent = Parent
    
        self.setStyleSheet(f"""
        QLineEdit {{
            background-color: {bg_shadow.name()};
            border: 3px solid {bg_light.name()};
        }}""")
        font = self.font()
        font.setPointSize(FontSize)
        self.setFont(font)
        self.setFixedWidth(Width)

class DirSelect(QWidget):
    dir_selected_signal = Signal(str)
    def __init__(self, Parent, Width, Caption="Select Folder"):
        super().__init__()
        self.parent = Parent
        self.caption = Caption
        
        self.path_layout = QHBoxLayout()
        self.setLayout(self.path_layout)
        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setStyleSheet(f"""
        QLineEdit {{
            background-color: {bg_shadow.name()};
            border: 1px solid {bg_light.name()};
        }}""")
        font = self.line_edit.font()
        font.setPointSize(12)
        self.line_edit.setFont(font)
        self.line_edit.setFixedWidth(Width)
        self.button = QToolButton()
        self.button.setText("Change")
        self.button.clicked.connect(self.SelectDir)
        self.path_layout.addWidget(self.line_edit)
        self.path_layout.addWidget(self.button)
        
    def SelectDir(self):
        dir = QFileDialog.getExistingDirectory(self, self.caption, ".")
        if dir:
            self.dir_selected_signal.emit(os.path.normpath(dir))

class ProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(500)
        self.max = self.maximum()
        self.setStyleSheet(f"""
        QProgressBar {{
            border: 1px solid {bg_light.name()};
            text-align: center;
            background-color: {bg_shadow.name()};
        }}
        QProgressBar::chunk {{
            background-color: {ir_blue.name()};
        }}
        """)
        
    def setLooping(self, arg__1: bool):
        if arg__1 == True:
            self.setMaximum(0)
        else:
            self.setMaximum(self.max)
        
class InstallWindow(QWidget):
    installed_signal = Signal(str)
    def __init__(self, parent=None):
        super().__init__()
        self.parent: MainWindow = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.plugin_dir = None
    
        self.title = QLabel()
        self.title.setText("Install Plugin")
        title_font = QFont("Verdana", 24, QFont.Weight.Bold)
        self.title.setFont(title_font)
        
        self.label1 = QLabel()
        self.label1.setText("Substance Plugins Folder")
        label1_font = QFont("Verdana", 14, QFont.Weight.Bold)
        self.label1.setFont(label1_font)
        
        self.label2 = QLabel()
        self.label2.setText(f"<font color=#c3c3c3>(C:/Users/username/Documents/Adobe/Adobe Substance 3D Painter)</font>")
        label2_font = QFont("Verdana", 8, True)
        self.label2.setFont(label2_font)
        
        self.path_sel = DirSelect(self, 500)
        self.path_sel.dir_selected_signal.connect(self.dirSelected)
        
        self.button = QPushButton("Install")
        self.button.setFixedWidth(125)
        self.button.setFixedHeight(35)
        self.button.clicked.connect(self.Install)
        
        self.progress_bar = ProgressBar()
        
        self.layout.addSpacing(5)
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.path_sel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        
    def dirSelected(self, Dir):
        self.plugin_dir = Dir
        if self.plugin_dir:
            self.path_sel.line_edit.setText(self.plugin_dir)
            self.button.setEnabled(True)
    
    def showEvent(self, event: QShowEvent):
        self.progress_bar.setLooping(False)
        self.parent.finish.setEnabled(False)
        self.parent.back.setEnabled(False)
        self.parent.next.setEnabled(False)
        self.parent.cancel.setEnabled(True)
        self.button.setEnabled(False)
        
        if self.plugin_dir is None:
            self.plugin_dir = _internal_utils.find_substance_plugin_dir()
        if self.plugin_dir:
            self.path_sel.line_edit.setText(self.plugin_dir)
            self.button.setEnabled(True)

        super().showEvent(event)
        
    def Downloaded(self):
        self.installed_signal.emit("Installed")
    
    def Install(self):
        plugin_dir = self.path_sel.line_edit.text()
        self.parent.cancel.setEnabled(True)
        self.parent.next.setEnabled(False)
        self.parent.finish.setEnabled(False)
        self.button.setEnabled(False)
        thread = threading.Thread(target=Download, args=(self,plugin_dir))
        thread.start()
        self.progress_bar.setLooping(True)
        
class UpdateWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent: MainWindow = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    
        self.title = QLabel()
        self.title.setText("Update Plugin")
        title_font = QFont("Verdana", 24, QFont.Weight.Bold)
        self.title.setFont(title_font)
        
        self.label1 = QLabel()
        label1_font = QFont("Verdana", 18, QFont.Weight.Bold)
        self.label1.setFont(label1_font)
        
        self.label2 = QLabel()
        label2_font = QFont("Verdana", 10)
        self.label2.setFont(label2_font)
        
        self.button = QPushButton()
        self.button.setFixedWidth(125)
        self.button.setFixedHeight(35)
        self.button.clicked.connect(self.Update)
        
        self.progress_bar = ProgressBar()
        
        self.layout.addSpacing(5)
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        
    def Checks(self):
        missing, matches, local, new = _internal_utils.check_version()
        
        self.progress_bar.setLooping(False)
        self.parent.finish.setEnabled(False)
        self.parent.back.setEnabled(False)
        self.parent.next.setEnabled(not missing)
        self.parent.cancel.setEnabled(True)
        self.button.setEnabled(True)

        if missing is True:
            label1_text = f"<font color=#dd2e22>Missing File(s)</font>"
            label2_text = "One or more files are missing from plugin installation."
            button_text = "Update"
            
        elif matches is False:
            label1_text = "<font color=#dbd124>New Version Available</font>"
            label2_text = "There is a newer version of the plugin available."
            button_text = "Update"
            
        else:
            label1_text = "<font color=#4ec33c>Version is Up to Date</font>"
            label2_text = "No update necessary, but you can force one."
            button_text = "Force Update"
        
        self.label1.setText(label1_text)
        self.label2.setText(label2_text)
        self.button.setText(button_text)
    
    def showEvent(self, event: QShowEvent):
        self.Checks()

        super().showEvent(event)
        
    def Downloaded(self):
        self.Checks()
    
    def Update(self):
        self.parent.cancel.setEnabled(True)
        self.parent.next.setEnabled(False)
        self.parent.finish.setEnabled(False)
        self.button.setEnabled(False)
        thread = threading.Thread(target=Download, args=(self,))
        thread.start()
        self.progress_bar.setLooping(True)

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent: MainWindow = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.title = QLabel()
        self.title.setText("Plugin Settings")
        title_font = QFont("Verdana", 24, QFont.Weight.Bold)
        self.title.setFont(title_font)
        
        self.label1 = QLabel()
        self.label1.setText("iRacing ID")
        label1_font = QFont("Verdana", 16)
        self.label1.setFont(label1_font)
        self.id_sel = TextEntry(self, 125, 16)
        self.id_sel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.id_sel.editingFinished.connect(self.id_set)
        
        self.blabel = QLabel()
        self.blabel.setText("Set location to create Paints and Templates Directories")
        blabel_font = QFont("Verdana", 12)
        self.blabel.setFont(blabel_font)
        self.button = QPushButton()
        self.button.setText("Select")
        self.button.clicked.connect(self.SetDirs)
        
        self.label2 = QLabel()
        self.label2.setText("Paints Directory")
        label2_font = QFont("Verdana", 10)
        self.label2.setFont(label2_font)
        self.paints_entry = DirSelect(self, 500)
        self.paints_entry.dir_selected_signal.connect(self.paints_dir_set)
        
        self.label3 = QLabel()
        self.label3.setText("Templates Directory")
        label3_font = QFont("Verdana", 10)
        self.label3.setFont(label3_font)
        self.templates_entry = DirSelect(self, 500)
        self.templates_entry.dir_selected_signal.connect(self.templates_dir_set)
        
        self.layout.addSpacing(5)
        
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addStretch()
        
        self.layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.id_sel, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addStretch()
        
        self.layout.addWidget(self.blabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addStretch()
        
        self.layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.paints_entry, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addStretch()
        
        self.layout.addWidget(self.label3, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.templates_entry, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.layout.addStretch()
    
    def id_set(self):
        id = self.id_sel.text()
        if id and id.isdecimal():
            _internal_utils.write_cfg("Settings", "customerid", id)
            self.Checks()
    
    def paints_dir_set(self, dir: str):
        _internal_utils.write_cfg("Settings", "paints_dir", dir)
        self.Checks()
    
    def templates_dir_set(self, dir: str):
        _internal_utils.write_cfg("Settings", "templates_dir", dir)
        self.Checks()
    
    def SetDirs(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Folder to Create Paints and Templates Folder in", ".")
        if dir:
            paints = os.path.normpath(os.path.join(dir, "Paints"))
            templates = os.path.normpath(os.path.join(dir, "Templates"))
            
            reply = QMessageBox.question(
                self, "Create Paints and Templates Folders",
                f"{paints}\n{templates}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                os.makedirs(paints, exist_ok=True)
                os.makedirs(templates, exist_ok=True)
                _internal_utils.write_cfg("Settings", "paints_dir", paints)
                _internal_utils.write_cfg("Settings", "templates_dir", templates)
                self.Checks()
    
    def Checks(self):
        cust_id = GetCustomerID()
        self.id_sel.setText(cust_id)
        
        paints_dir = GetPaintsDir()
        self.paints_entry.line_edit.setText(paints_dir)
        
        template_dir = GetTemplateDir()
        self.templates_entry.line_edit.setText(template_dir)
        enabled = True if template_dir != None else False
        self.parent.next.setEnabled(enabled)
        
    def showEvent(self, event: QShowEvent):
        self.parent.cancel.setEnabled(True)
        self.parent.back.setEnabled(True)
        self.parent.finish.setEnabled(False)
        
        self.Checks()

        super().showEvent(event)
        
class TemplatesWindow(QWidget):
    
    class PaintTemplate(QListWidgetItem):
        def __init__(self, key: str, data: dict):
            super().__init__()
            self.key = key
            self.data_dict = data
            self.setText(self.data_dict["Name"])
            self.file_id = self.data_dict["FileID"]
            
            self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            self.setCheckState(Qt.CheckState.Unchecked)
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent: MainWindow = parent
        self.data_dict = {}
        self.downloader = None
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    
        self.title = QLabel()
        self.title.setText("Download Templates")
        title_font = QFont("Verdana", 24, QFont.Weight.Bold)
        self.title.setFont(title_font)
        
        self.button = QPushButton("Download")
        self.button.setFixedWidth(125)
        self.button.setFixedHeight(35)
        self.button.clicked.connect(self.StartDownload)
        
        self.selects = QWidget()
        self.selects_layout = QHBoxLayout()
        self.selects.setLayout(self.selects_layout)
        self.select_all = QPushButton("Select All")
        self.select_all.setFixedSize(75, 25)
        self.select_all.clicked.connect(lambda: self.SelectAll(True))
        self.deselect_all = QPushButton("Deselect All")
        self.deselect_all.setFixedSize(75, 25)
        self.deselect_all.clicked.connect(lambda: self.SelectAll(False))
        self.selects_layout.addWidget(self.select_all, alignment=Qt.AlignmentFlag.AlignTop)
        self.selects_layout.addWidget(self.deselect_all, alignment=Qt.AlignmentFlag.AlignTop)
        self.selects_layout.addSpacing(100)
        self.selects_layout.addWidget(self.button)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.itemClicked)
        self.template_list.setFixedHeight(150)
        self.template_list.setFixedWidth(350)
        self.template_list.setAlternatingRowColors(True)
        '''self.template_list.setStyleSheet(f"""
            QListWidget {{
                border: 3px solid {bg_light.name()};
            }}
            QListWidget::item {{ 
                background-color: {bg_light.name()};
            }}
            QListWidget::item:alternate {{ 
                background-color: {bg_shadow.name()};
            }}
        """)'''
        
        self.label1 = QLabel()
        self.label1.setText("")
        label1_font = QFont("Verdana", 8, True)
        self.label1.setFont(label1_font)
        
        self.current_progress_bar = ProgressBar()
        
        self.label2 = QLabel()
        self.label2.setText("")
        label2_font = QFont("Verdana", 8, True)
        self.label2.setFont(label2_font)
        
        self.total_progress_bar = ProgressBar()
        
        self.layout.addSpacing(5)
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.template_list, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.selects, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.current_progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.total_progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
    
    def SelectAll(self, bool):
        for index in range(self.template_list.count()):
            item = self.template_list.item(index)
            if bool is True:
                item.setCheckState(Qt.CheckState.Checked)
                item.setBackground(ir_blue)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setBackground(QBrush())
        self.selectionChange()
        
    def itemClicked(self, item: PaintTemplate):
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setBackground(QBrush())
        else:
            item.setCheckState(Qt.CheckState.Checked)
            item.setBackground(ir_blue)
        item.setSelected(False)
        self.selectionChange()
    
    def selectionChange(self):
        can_download = False
        for index in range(self.template_list.count()):
            item = self.template_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                can_download = True
                break
        self.button.setEnabled(can_download)
    
    def PopulateList(self):
        self.template_list.clear()
        
        data_key_list = list(self.data_dict.keys())
        data_key_list = sorted(self.data_dict, key=lambda key: self.data_dict[key]["Name"], reverse=False)
        
        for key in data_key_list:
            item = self.PaintTemplate(key, self.data_dict[key])
            self.template_list.addItem(item)
    
    def Checks(self):
        self.template_list.setEnabled(True)
        self.parent.cancel.setEnabled(True)
        self.parent.back.setEnabled(True)
        self.parent.next.setEnabled(False)
        self.parent.finish.setEnabled(True)
        self.button.setEnabled(False)
        self.select_all.setEnabled(True)
        self.deselect_all.setEnabled(True)
        
        self.label1.setText("")
        self.label2.setText("")
        self.current_progress_bar.setValue(-1)
        self.total_progress_bar.setValue(-1)
        
        new_data = _internal_utils.get_data()
        if self.data_dict != new_data:
            self.data_dict = new_data
            self.PopulateList()
        
        self.selectionChange()
    
    def showEvent(self, event: QShowEvent):
        self.Checks()

        super().showEvent(event)
        
    def StartDownload(self):
        templates = {}
        for index in range(self.template_list.count()):
            item = self.template_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                name = item.key
                file_id = item.file_id
                if file_id:
                    templates[name] = file_id
                
        if templates:
            self.parent.back.setEnabled(False)
            self.parent.finish.setEnabled(False)
            self.button.setEnabled(False)
            self.select_all.setEnabled(False)
            self.deselect_all.setEnabled(False)
            self.template_list.setEnabled(False)
            
            self.current_progress_bar.setLooping(True)
            self.total_progress_bar.setLooping(True)
            
            self.downloader = _internal_utils.download_templates(templates)
            self.downloader.download_prog.connect(self.DownloadProgress)
            self.downloader.download_finished.connect(self.DownloadFinished)
            
    def DownloadProgress(self, Name: str, Current: float, Total: float):
        self.current_progress_bar.setValue(int(Current * 100))
        self.total_progress_bar.setValue(int(Total * 100))
        self.label1.setText(Name)
        self.label2.setText("Total")
        self.current_progress_bar.setLooping(False)
        self.total_progress_bar.setLooping(False)
    
    def DownloadFinished(self, Failed: list):
        self.downloader = None
        self.Checks()
        print(Failed)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.size = QSize(640, 480)

        self.setWindowTitle("iRacing Tools Installer")
        self.setFixedSize(self.size)
        self.setWindowIcon(QIcon(images))
        
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.lower_layout = QHBoxLayout()
        
        self.stack = QStackedWidget()
        self.stack.setFixedHeight(400)
        self.stack.setStyleSheet(f"background-color: {bg_dark.name()};")
        
        self.install_window = InstallWindow(self)
        self.install_window.installed_signal.connect(self.InstallCheck)
        self.update_window = UpdateWindow(self)
        self.settings_window = SettingsWindow(self)
        self.templates_window = TemplatesWindow(self)
        self.stack.addWidget(self.install_window)
        self.stack.addWidget(self.update_window)
        self.stack.addWidget(self.settings_window)
        self.stack.addWidget(self.templates_window)
        
        self.lower_widget = QWidget()
        self.lower_widget.setFixedHeight(50)
        self.lower_widget.setStyleSheet(f"background-color: {bg_dark.name()};")
        self.lower_widget.setLayout(self.lower_layout)
        
        self.cancel = QPushButton("Cancel")
        self.cancel.setFixedWidth(100)
        self.cancel.clicked.connect(QApplication.quit)
        
        self.back = QPushButton("Back")
        self.back.setFixedWidth(100)
        self.back.setEnabled(False)
        self.back.clicked.connect(lambda: self.NextBack(False))
        
        self.next = QPushButton("Next")
        self.next.setFixedWidth(100)
        self.next.setEnabled(False)
        self.next.clicked.connect(lambda: self.NextBack(True))
        
        self.finish = QPushButton("Finish")
        self.finish.setFixedWidth(100)
        self.finish.setEnabled(False)
        self.finish.clicked.connect(QApplication.quit)
        
        self.lower_layout.addWidget(self.cancel, alignment=Qt.AlignmentFlag.AlignLeft)
        self.lower_layout.addStretch()
        self.lower_layout.addWidget(self.back)
        self.lower_layout.addWidget(self.next)
        self.lower_layout.addStretch()
        self.lower_layout.addWidget(self.finish, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.layout.addWidget(self.stack)
        self.layout.addWidget(self.lower_widget, alignment=Qt.AlignmentFlag.AlignBottom)
        self.main_widget.setLayout(self.layout)
        
        self.setCentralWidget(self.main_widget)
    
    def NextBack(self, Next: bool):
        index = self.stack.currentIndex()
        
        if Next is True:
            index = index + 1
            self.stack.setCurrentIndex(index)
        else:
            index = index - 1
            self.stack.setCurrentIndex(index)
    
    def InstallCheck(self):
        if _internal_utils.is_plugin_installed() is True:
            self.stack.setCurrentIndex(1)
        
    def showEvent(self, event: QShowEvent):
        self.InstallCheck()
        super().showEvent(event)

window = MainWindow()
window.show()

app.exec()