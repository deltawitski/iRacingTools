import sys
import os

from iRacingToolsResources import _internal_utils

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)
app.setStyle('Fusion')

palette = QPalette()
palette.setColor(QPalette.Window, QColor(51, 51, 51)) #Window Background
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, QColor(43, 43, 43)) #Title Bar
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, Qt.white)
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, Qt.black)
app.setPalette(palette)

base_dir = os.path.dirname(__file__)
logo_path = os.path.join(base_dir, "iRacingToolsResources/icons/logo.ico")
icon_iracing_color = QIcon(logo_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("iRacing Tools Installer")
        self.setFixedSize(640, 480)
        self.setWindowIcon(icon_iracing_color)

window = MainWindow()
window.show()

#print(_internal_utils.is_plugin_installed())
#print(_internal_utils.check_version())
#print(_internal_utils.download_plugin())

app.exec()