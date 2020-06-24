from PyQt5.QtWidgets import *


class SetTsneParams(QMainWindow):
    def __init__(self, parent, in_len):
        super().__init__(parent)

        # Default
        self.previous_window = parent
        self.perplexity = 50.0
        self.dim = 2
        self.iterations = 500

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.perplexity_label = QLabel("Перплексия")
        self.perplexity_edit = QLineEdit()
        self.layout.addWidget(self.perplexity_label)
        self.layout.addWidget(self.perplexity_edit)

        self.dim_label = QLabel("Новая размерность(исх. = "+str(in_len)+")")
        self.dim_edit = QLineEdit()
        self.layout.addWidget(self.dim_label)
        self.layout.addWidget(self.dim_edit)

        self.iterations_label = QLabel("Число итераций")
        self.iterations_edit = QLineEdit()
        self.layout.addWidget(self.iterations_label)
        self.layout.addWidget(self.iterations_edit)

        self.confirmationButton1 = QPushButton("Готово")

        self.confirmationButton1.clicked.connect(self.set_params)
        self.layout.addWidget(self.confirmationButton1)

        self.setGeometry(100, 100, 200, 150)
        self.setWindowTitle("Параметры t-SNE")
        self.show()

    def perf(self):
        print("everything is good")

    def set_params(self):  # TODO: временно исключен промежуточный этап
        if self.prepareData():  # TODO: what is this func doing?
            self.close()
            self.previous_window.set_tsne_params_pressed(self.perplexity, self.dim, self.iterations)

    def prepareData(self):
        """ Подготавилвает данные, нужные для работы
        :return: возвращает True если подготовка выполнена успешно и False в противном случае
        """
        try:
            self.perplexity = float(self.perplexity_edit.text())
            self.dim = int(self.dim_edit.text())
            self.iterations = int(self.iterations_edit.text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("задано некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            return False
        return True
