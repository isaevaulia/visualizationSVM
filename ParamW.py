from PyQt5.QtWidgets import *

class ParamWindow(QDialog):
    def __init__(self,parent):
        super().__init__(parent)

        self.parent = parent
        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle("Выберите параметры")

        self.kernel = QLabel('Kernel')
        self.c = QLabel('C')
        self.gamma = QLabel('Gamma')

        self.kernelEdit = QLineEdit()
        self.cEdit = QLineEdit()
        self.gammaEdit = QLineEdit()

        self.OKButton = QPushButton("OK")
        self.OKButton.clicked.connect(self.OKclick)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.kernel, 1, 0)
        self.grid.addWidget(self.kernelEdit, 1, 1)
        self.grid.addWidget(self.c, 2, 0)
        self.grid.addWidget(self.cEdit, 2, 1)
        self.grid.addWidget(self.gamma, 3, 0)
        self.grid.addWidget(self.gammaEdit, 3, 1)
        self.grid.addWidget(self.OKButton, 4, 2)

        self.setLayout(self.grid)
        self.show()

    def OKclick(self):
        self.parent.kernel = self.kernelEdit.text()
        self.parent.c = int(self.cEdit.text())
        self.parent.gamma = float(self.gammaEdit.text())
        self.close()


