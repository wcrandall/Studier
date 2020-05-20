import os.path
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import Qt

class HelpView(QDialog):
    file_path = os.path.dirname(os.path.abspath(__file__))

    ui_path = os.path.join(file_path, "Help.ui")

    def __init__(self):
        super(HelpView, self).__init__()
        # taking out Question mark button by x button
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        uic.loadUi(self.ui_path, self)

        self.CloseButton.clicked.connect(self.close_button_clicked)


    def close_button_clicked(self):
        self.close()