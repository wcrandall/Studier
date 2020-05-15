import os.path
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class HelpView(QDialog):
    ui_path = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(ui_path, "Help.ui")

    def __init__(self):
        super(HelpView, self).__init__()
        uic.loadUi(self.ui_path, self)
        self.CloseButton.clicked.connect(self.close_button_clicked)


    def close_button_clicked(self):
        self.close()