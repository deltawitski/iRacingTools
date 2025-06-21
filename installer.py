import sys
import os
import threading

from iRacingToolsResources import _internal_utils

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPalette, QColor, QIcon, QShowEvent, QFont
from PySide6.QtWidgets import ( 
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QStackedWidget, QPushButton, QProgressBar, 
    QLabel, QLineEdit, QFileDialog, QToolButton
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
app.setPalette(palette)

base_dir = os.path.dirname(__file__)
logo_path = os.path.join(base_dir, "iRacingToolsResources/icons/logo.ico")
icon_iracing_color = QIcon(logo_path)

def Download(parent, Path=None):
    _internal_utils.download_plugin(Path)
    show_event = QShowEvent()
    QApplication.sendEvent(parent, show_event)

class DirSelect(QWidget):
    def __init__(self, Parent, Width):
        super().__init__()
        self.parent = Parent
        
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
        self.path_layout.addWidget(self.line_edit)
        self.path_layout.addWidget(self.button)

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
        
        self.button = QPushButton("Install")
        self.button.setFixedWidth(125)
        self.button.setFixedHeight(35)
        self.button.clicked.connect(self.Install)
        
        self.progress_bar = ProgressBar()
        
        self.layout.addStretch()
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.path_sel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        
    def showEvent(self, event: QShowEvent):
        self.progress_bar.setLooping(False)
        self.parent.finish.setEnabled(False)
        self.parent.next.setEnabled(False)
        self.parent.cancel.setEnabled(True)
        self.button.setEnabled(False)
        
        plugin_dir = _internal_utils.find_substance_plugin_dir()
        if plugin_dir:
            self.path_sel.line_edit.setText(plugin_dir)
            self.button.setEnabled(True)

        self.installed_signal.emit("Installed")
        super().showEvent(event)
        
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
        #self.progress_bar.setLooping(True)
        
        self.layout.addStretch()
        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.label2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        
    def showEvent(self, event: QShowEvent):
        self.progress_bar.setLooping(False)
        self.parent.finish.setEnabled(True)
        self.parent.next.setEnabled(True)
        self.parent.cancel.setEnabled(False)
        self.button.setEnabled(True)
        
        missing, matches, local, new = _internal_utils.check_version()
        
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

        super().showEvent(event)
        
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
        
    def showEvent(self, event: QShowEvent):

        super().showEvent(event)
        
class TemplatesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent: MainWindow = parent
        
    def showEvent(self, event: QShowEvent):

        super().showEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.size = QSize(640, 480)

        self.setWindowTitle("iRacing Tools Installer")
        self.setFixedSize(self.size)
        self.setWindowIcon(icon_iracing_color)
        
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.lower_layout = QHBoxLayout()
        
        self.stack = QStackedWidget()
        self.stack.setFixedHeight(400)
        self.stack.setStyleSheet(f"background-color: {bg_dark.name()};")
        
        self.install_window = InstallWindow(self)
        self.install_window.installed_signal.connect(self.InstallCheck)
        self.update_window = UpdateWindow(self)
        self.stack.addWidget(self.install_window)
        self.stack.addWidget(self.update_window)
        
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
        
        self.next = QPushButton("Next")
        self.next.setFixedWidth(100)
        self.next.setEnabled(False)
        
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
    
    def InstallCheck(self):
        if _internal_utils.is_plugin_installed() is True:
            self.stack.setCurrentIndex(1)
        
    def showEvent(self, event: QShowEvent):
        self.InstallCheck()
        super().showEvent(event)

window = MainWindow()
window.show()

#print(_internal_utils.is_plugin_installed())
#print(_internal_utils.check_version())
#print(_internal_utils.download_plugin())

app.exec()