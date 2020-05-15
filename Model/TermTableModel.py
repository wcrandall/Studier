from PyQt5 import QtCore

# the class that models the QtableView in mainview
class TermTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TermTableModel, self).__init__()
        self._data = data

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextAlignmentRole:
            # ensuring table data is centered
            return QtCore.Qt.AlignCenter
        elif role == QtCore.Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])
