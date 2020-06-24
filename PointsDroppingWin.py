from PyQt5.QtWidgets import *


class PointsDroppingWin(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)

        self.bar_level = 4.0
        self.previous_window = parent
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)
        self.drop_level_label = QLabel("Введите допустимое расстояние")
        self.drop_level_edit = QLineEdit()
        self.layout.addWidget(self.drop_level_label)
        self.layout.addWidget(self.drop_level_edit)

        self.confirmationButton1 = QPushButton("Отбросить по Евклидову расстоянию")
        self.confirmationButton2 = QPushButton("Отбросить по Манхэттэнскому расстоянию")

        self.confirmationButton1.clicked.connect(self.drop_points)
        self.confirmationButton2.clicked.connect(self.drop_points_manh)
        self.layout.addWidget(self.confirmationButton1)
        self.layout.addWidget(self.confirmationButton2)

        self.setGeometry(100, 100, 200, 150)
        self.setWindowTitle("Отбросить по расстоянию")
        self.show()

    def perf(self):
        print("everything is good")

    def drop_points(self):
        if(self.prepareData()):
            self.previous_window.drop_points(self.bar_level)

    def drop_points_manh(self):
        if(self.prepareData()):
            print("drop points manh")
            self.previous_window.drop_points_manh(self.bar_level)

    def prepareData(self):
        """ Подготавилвает данные, нужные для работы
        :return: возвращает True если подготовка выполнена успешно и False в противном случае
        """
        try:
            self.bar_level = float(self.drop_level_edit.text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Расстояние задано некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            return False
        return True
