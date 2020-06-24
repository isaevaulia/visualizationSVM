import CLOPE
import getBins
import Utils
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *  # TODO: change
from UtilityClasses import Cluster
import Constants

class CLOPEWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.workData = self.parent().globalData

        self.rowsToClusterize = list(self.workData)
        self.rowsToConsider = list(self.workData)

        self.resultClusters = []
        self.supposedClusterElems = set()

        self.cluster = None

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)

        self.repulsion_label = QLabel("Параметр отталкивания:")
        self.repulsion_edit = QLineEdit()
        self.repulsion_edit.setPlaceholderText("2 < repulsion < 3")
        self.layout.addWidget(self.repulsion_label)
        self.layout.addWidget(self.repulsion_edit)

        self.noise_limit_label = QLabel("Уровень шума:")
        self.noise_limit_edit = QLineEdit()
        self.noise_limit_edit.setPlaceholderText("3 < noise limit < 4")
        self.layout.addWidget(self.noise_limit_label)
        self.layout.addWidget(self.noise_limit_edit)

        self.confirmationButton = QPushButton("Выполнить")
        self.confirmationButton.clicked.connect(self.perform_algorithm)
        self.layout.addWidget(self.confirmationButton)

        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("CLOPE")
        self.show()

    def perform_algorithm(self):

        prepared_data = getBins.prepareData(
            Utils.readExcelData(
                'data/CarData1Lab.xlsx'
            )
        )  # TODO: change to parameter

        # Перемешивание данных
        seed = None
        np.random.seed(seed)
        # np.random.shuffle(prepared_data)

        transacts = {}
        for i in range(0, len(prepared_data)):
            for j in range(0, len(prepared_data[i])):
                if j != 0:
                    if prepared_data[i][j] != '?':
                        transacts[i][j] = prepared_data[i][j] + str(j)
                    else:
                        pass
                        # print('miss object')
                else:
                    transacts[i] = [''] * len(prepared_data[i])
                    transacts[i][j] = prepared_data[i][j] + str(j)

        clope = CLOPE.CLOPE(print_step=1000,
                            is_save_history=True,
                            random_seed=seed)

        # Начальные данные
        repulsion = float(self.repulsion_edit.text())  # TODO: +try
        noise_limit = int(self.noise_limit_edit.text())  # TODO: +try

        # Инициализируем алгоритм
        clope.init_clusters(transacts, repulsion, noise_limit)
        # df = get_count_clusters(transacts, clope)
        # clope.print_history_count(repulsion, seed)

        # Итерируемся
        while clope.next_step(transacts, repulsion, noise_limit) > 0:
            # clope.print_history_count(repulsion, seed)
            pass

        self.translateClusters(clope)

        self.removing()

    # Поменять имена переменных
    def translateClusters(self, clope):
        for num in sorted(clope.clusters.keys()):
            numsOfTransactions = []
            for k, v in clope.transaction.items():
                if v == num:
                    numsOfTransactions.append(k)
            # print(numsOfTransactions)
            trs = [self.workData._rows[i] for i in numsOfTransactions]
            cluster = Cluster(self.workData.buildClusterDataFromRows(trs))
            cluster.setColor(Constants.EXTENDED_COLOR_SET[(num-1) % len(Constants.EXTENDED_COLOR_SET)])
            cluster.setName("clope" + str(num))
            self.resultClusters.append(cluster)
        self.parent().addClusters(self.resultClusters)

    def removing(self):
        for cluster in self.parent().clusters:
            if cluster.getSize() < 3:
                cluster.setHidden(not cluster.isHidden())


    def closeEvent(self, event):
        self.parent().sphere = None
        self.parent().circle = None
        self.parent().refreshCanvas()
        self.parent().refreshClusterTable()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    df = CLOPEWindow()
    sys.exit(app.exec_())
