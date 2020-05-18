from View.MainView import MainView
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5 import QtGui
import os

# launching application
try:
    file_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(file_path, "StudierLogo.png")
    app = QApplication(sys.argv)
    app.setApplicationName("Studier")
    app.setWindowIcon(QtGui.QIcon(icon_path))
    window = MainView()
    window.show()
    app.exec_()
except Exception as e:
    print(str(e))
