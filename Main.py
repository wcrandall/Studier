from View.MainView import MainView
from PyQt5.QtWidgets import QApplication

# launching application
try:
    app = QApplication([])
    window = MainView()
    window.show()
    app.exec_()
except Exception as e:
    print(str(e))
