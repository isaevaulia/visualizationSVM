from PyQt5.QtGui import *
from PyQt5.QtCore import *
import matplotlib
import time
from sklearn import svm
from sklearn.manifold import TSNE
matplotlib.use('agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from Lib import shutil
import xlwt
import GraphInspection
import TSNEW
from ClusterAdjustments import ClusterDialog
from ClusterPointsAdjustments import ClusterPointsView
from DBScanImplementation import DBScanWindow
from CLOPEImplementation import CLOPEWindow
from DataPreview import DataPreviewWindow
from AdditionalProjection import AdditionalProjectionWindow
from UtilityClasses import *
from TsneSolver import *
from SetTsneParamsWin import *
import Constants

class MainWindow(QMainWindow):
    """ Главное окно

    """
    sphere = None
    inspectionWindow = None
    TSNEWindow = None
    additionalProjectionWindow = None
    clusterPointsAdjustmentsWindow = None
    clusters = []
    selectedClusterIndexes = []

    def __init__(self):
        super().__init__()
        self._SV = []
        self.circle = None
        self.current_data_file_name = None
        self.temp_data_file_name = "tempdatafile.xlsx"

        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu("Файл")
        self.openFile = QAction('Открыть', self)
        self.openFile.triggered.connect(self.openFilePressed)
        self.fileMenu.addAction(self.openFile)
        self.optionsMenu = self.menubar.addMenu("Опции")
        self.additionalProjection = QAction("Доп. проекция", self)
        self.additionalProjection.triggered.connect(self.createAdditionalProjection)
        self.optionsMenu.addAction(self.additionalProjection)
        self.algorithmsMenu = self.menubar.addMenu("Алгоритмы")
        self.dbscanoption = QAction("Алгоритм DBScan", self)
        self.tsneoption = QAction("Алгоритм t-SNE", self)
        self.dbscanoption.triggered.connect(self.dbscanoptionChosen)
        self.tsneoption.triggered.connect(self.tsneoptionChosen)
        self.algorithmsMenu.addAction(self.dbscanoption)
        self.algorithmsMenu.addAction(self.tsneoption)
        self.algorithmsMenu.setEnabled(False)
        self.clopeoption = QAction("Алгоритм CLOPE", self)
        self.clopeoption.triggered.connect(self.clopeoptionChosen)
        self.algorithmsMenu.addAction(self.clopeoption)

        self.SVoption = QAction("Выделить опорные векторы", self)
        self.SVoption.triggered.connect(self.SVoptionChosen)
        self.algorithmsMenu.addAction(self.SVoption)

        self.TSNEoption = QAction("Применить t-sne", self)
        self.TSNEoption.triggered.connect(self.TSNEoptionChosen)
        self.algorithmsMenu.addAction(self.TSNEoption)

        self.mainTabs = QTabWidget()
        self.mainTabs.setStyleSheet("QTabWidget { border: 0px solid black }; ")
        self.setCentralWidget(self.mainTabs)
        self.figure = Figure()
        self.additional_figure = Figure()
        self.matrixWidget = FigureCanvas(self.figure)
        self.matrixWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.matrixWidget.setMinimumSize(640, 480)
        self.matrixWidget.resize(640, 480)
        self.matrixScrollArea = QScrollArea()
        self.matrixScrollArea.setWidget(self.matrixWidget)
        self.matrixScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.matrixScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mainTabs.addTab(self.matrixScrollArea, "Графики")
        self.dataWidget = QWidget()
        self.dataLayout = QVBoxLayout(self.dataWidget)
        self.dataTable = QTableWidget()
        self.dataLayout.addWidget(self.dataTable)
        self.mainTabs.addTab(self.dataWidget, "Данные")
        self.clustersWidget = QWidget()
        self.clustersLayout = QVBoxLayout(self.clustersWidget)
        self.clustersTable = QTableWidget()
        self.clustersTable.setColumnCount(6)
        self.clustersTable.setHorizontalHeaderLabels(
            ["Имя кластера", "Количество", "Маркер", "Скрыт", ""])

        self.clustersTable.setHorizontalHeaderItem(5, QTableWidgetItem("Действия"))
        self.clustersLayout.addWidget(self.clustersTable)
        self.mainTabs.addTab(self.clustersWidget, "Кластеры")

        self.setWindowTitle('Cluster Analysis 2.2')
        self.setWindowIcon(QIcon('icon\\app_icon.png'))
        self.setGeometry(100, 100, 640, 480)
        self.showMaximized()
        self.temp_tsne_size = 2

    def TSNEoptionChosen(self):
        """ Обработчик клика на кнопку "применить t-SNE" (не реализована ошибка)

                           """
        # Определяем модель и скорость обучения
        model = TSNE(learning_rate=100)
        x = []
        y = []
        for i in range(len(self.globalData._columns)):
            x.append(self.globalData._columns[i]._data)
        x = np.array(x).T.tolist()

        for yel in self.globalData._target:
            y.append(yel)
        transformed = model.fit_transform(x)
        # Представляем результат в двумерных координатах
        x_axis = transformed[:, 0]
        y_axis = transformed[:, 1]
        self.TSNEWindow = TSNEW.TWindow(self, x_axis, y_axis, x, y, self._SV)

    def SVoptionChosen(self):
        """ Обработчик клика на кнопку "Выделить опорные векторы" (не реализована ошибка)

                   """
        x = []
        y = []
        for i in range(len(self.globalData._columns)):
            x.append(self.globalData._columns[i]._data)
        x = np.array(x).T.tolist()

        for yel in self.globalData._target:
            y.append(yel)

        clf = svm.SVC(kernel='rbf')
        start = time.time_ns()
        clf.fit(x, y)
        end = time.time_ns()
        print("time SVC on all data:", end-start)
        indexSet = clf.support_
        self._SV = indexSet
        print('True SV', indexSet)
        sc = clf.score(x, y)

        print("Точность модели тсне", str(sc))

        columnCount = self.globalData.significantColumnCount()
        columns = self.globalData.getSignificantColumns()
        for i in range(0, columnCount):
            for j in range(0, columnCount):
                if i != j:
                    columnForAbscissas = columns[i]
                    columnForOrdinates = columns[j]
                    axes = self.figure.add_subplot(columnCount, columnCount, j * columnCount + i + 1)
                    xAll = columns[i]._data
                    yAll = columns[j]._data
                    target = self.globalData._target
                    Cluster.draw2DPointsSV(axes, xAll, yAll, target, plt.cm.coolwarm, 20, 'o')

                    xD = []
                    yD = []
                    target = []
                    for k in indexSet:
                        xD.append(columns[i].__getitem__(k))
                        yD.append(columns[j].__getitem__(k))
                        target.append(self.globalData._target[k])
                    Cluster.draw2DPointsSV(axes, xD, yD, target, plt.cm.Oranges, 6, '.')  # spring

                    axes.set_title(columnForOrdinates.getName() + "_" + columnForAbscissas.getName())
        self.matrixWidget.draw()


    def get_additional_figure(self):
        return self.additional_figure

    def set_tsne_params_pressed(self, p, d, i):
        """
        :param p:
        :param d:
        :param i:
        :return: None
        """
        if len(self.filename) > 0:
            columns, target = Utils.readExcelData(self.filename)
            d_data = GlobalData(columns, target)
            newData = DataPreviewWindow.preprocessData(d_data)                                               # вызываем диалог предобработки данных
            self.current_data_file_name = self.filename  # put into c_d_f_n filename
            shutil.copy(self.current_data_file_name, self.temp_data_file_name)  # copied data to temp file
            if newData is not None:
                self.startWorkingWithData(newData)

    def openFilePressed(self):
        """ Действия, выполняемые при нажатии кнопки открытия файла

        """
        self.filename = QFileDialog.getOpenFileName(self, 'Open file', 'data')[0]
        columns, target = Utils.readExcelData(self.filename)
        self.set_tsne_params_pressed(50.0, 2, 500)                                         #comment

    def startWorkingWithData(self, data):
        """ Инициализация данных в программе

        :param data: инициализируемые данные - это объект типа Data
        """

        self.globalData = data
        self.cleanupAppData()

        Utils.fillTableWithData(self.dataTable, self.globalData)
        self.initCanvas()
        self.algorithmsMenu.setEnabled(True)

    def add_tsne_to_temp_excel(self, num):
        book = xlwt.Workbook(self.temp_data_file_name)
        sh = book.add_sheet("tsne")

    def canvasClicked(self, event):
        """ Обработчик кликов мышью по области с графиками

        :param event: событие-клик
        """
        if event.inaxes is not None:
            ax = event.inaxes
            if (len(ax.lines)) != 0:
                self.inspectionWindow = GraphInspection.GraphInspectionWindow(self, ax)

    def addCluster(self, cluster):
        """
        Добавление кластера и прочие связанные с этим действия.
        Для добавления нового кластера необходимо использовать эту функцию.

        :param cluster: добавляемый кластер - это объект типа Cluster
        """
        self.clusters.append(cluster)
        self.addClusterToTable(cluster)
        self.refreshCanvas()

    # TODO: doc-string
    def addClusters(self, clusters):
        """

        :param clusters:
        :return:
        """
        self.clusters.extend(clusters)
        for cluster in clusters:
            self.addClusterToTable(cluster)
        self.refreshCanvas()

    def addClusterToTable(self, cluster):
        """
        Функция, добавляющая кластер в таблицу с кластерами. Вызывается функцией addCluster

        :param cluster: добавляемый кластер - это объект типа Cluster
        """
        self.clustersTable.setRowCount(self.clustersTable.rowCount() + 1)
        currentRowIndex = self.clustersTable.rowCount() - 1
        self.clustersTable.setItem(currentRowIndex, 0, QTableWidgetItem(cluster.getName()))
        self.clustersTable.setItem(currentRowIndex, 1, QTableWidgetItem(str(cluster.getSize())))

        figure = Figure()
        markerShapeCell = FigureCanvas(figure)
        markerShapeCell.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        axes = figure.add_subplot(111)
        axes.axis("off")
        markerSize = 8
        axes.plot([1], [1], linestyle="None", marker=cluster.getShape(), color=cluster.getColor(),
                  markersize=markerSize)
        markerShapeCell.draw()
        self.clustersTable.setCellWidget(currentRowIndex, 2, markerShapeCell)
        if cluster.isHidden():
            self.clustersTable.setItem(currentRowIndex, 3, QTableWidgetItem("Да"))
        else:
            self.clustersTable.setItem(currentRowIndex, 3, QTableWidgetItem("Нет"))

        clusterOptionsButton = QPushButton("Опции")
        clusterOptionsMenu = QMenu()
        self.clustersTable.setCellWidget(currentRowIndex, 4, clusterOptionsButton)
        index = QPersistentModelIndex(self.clustersTable.model().index(currentRowIndex, 4))

        adjustClusterPointsAction = QAction("Просмотр точек", self)
        adjustClusterPointsAction.triggered.connect(
            lambda *args, index=index: self.adjustClusterPoints(index.row()))
        clusterOptionsMenu.addAction(adjustClusterPointsAction)

        adjustClusterAction = QAction("Визуализация кластера", self)
        adjustClusterAction.triggered.connect(
            lambda *args, index=index: self.adjustCluster(index.row()))
        clusterOptionsMenu.addAction(adjustClusterAction)

        hideorshowClusterAction = QAction("Скрыть/показать кластер", self)
        hideorshowClusterAction.triggered.connect(
            lambda *args, index=index: self.hideorshowCluster(index.row()))
        clusterOptionsMenu.addAction(hideorshowClusterAction)

        removeClusterAction = QAction("Удалить кластер", self)
        removeClusterAction.triggered.connect(
            lambda *args, index=index: self.removeCluster(index.row()))
        clusterOptionsMenu.addAction(removeClusterAction)

        clusterOptionsButton.setMenu(clusterOptionsMenu)

        checkboxcontainer = QWidget()
        checkboxcontainer.setStyleSheet("background-color:#cccccc;")
        containerlayout = QVBoxLayout(checkboxcontainer)
        containerlayout.setAlignment(Qt.AlignCenter)
        clusterSelectCheckBox = QCheckBox()
        containerlayout.addWidget(clusterSelectCheckBox)
        clusterSelectCheckBox.stateChanged.connect(
            lambda *args, index=index, state=clusterSelectCheckBox.isChecked(): self.clusterSelect(index, state)
        )
        self.clustersTable.setCellWidget(currentRowIndex, 5, checkboxcontainer)

    def clusterSelect(self, index, state):
        if not state:
            self.selectedClusterIndexes.append(index)
        else:
            self.selectedClusterIndexes.remove(index)

    def adjustCluster(self, index):
        """ Вызывает диалог, измеяющий косметические параметры кластера

        :param index: индекс изменяемого кластера в массиве кластеров
        :return:
        """
        cluster = ClusterDialog.adjustCluster(self.clusters[index])
        if cluster is not None:
            self.clusters[index] = cluster
            # TODO: вместо обновления всей таблицы, обновлять только строку этого кластера refreshRow
            self.refreshClusterTable()
            # TODO: и перерисовывать только его точки
            self.refreshCanvas()

    def hideorshowCluster(self, index):
        """ Изменяет свойство видимости кластера и рендерит изменения.

        :param index: индекс изменяемого кластера в массиве кластеров
        """
        self.clusters[index].setHidden(not self.clusters[index].isHidden())
        self.refreshCanvas()
        self.refreshClusterTable()

    def removeCluster(self, index):
        """ Удаляет кластер из программы и рендерит изменения

        :param index: индекс удаляемого кластера в массиве кластеров
        """
        del self.clusters[index]
        self.clustersTable.removeRow(index)
        self.refreshCanvas()

    def adjustClusterPoints(self, index):
        """ Вызывает окно, позволяющее детально рассмотреть список точек в кластере.

        :param index:
        """
        self.clusterPointsAdjustmentsWindow = ClusterPointsView(self, self.clusters[index])

    def initCanvas(self):
        """ Служебная (вспомогательная) функция, инициализирующая канвас с графиками. Вызывается функцией startWorkingWithData

        """
        columns = self.globalData.getSignificantColumns()
        # globalData.addRow()
        target = self.globalData._target
        columnCount = self.globalData.significantColumnCount()

        #self.matrixWidget.resize((columnCount+self.temp_tsne_size+1) * 200, (columnCount+self.temp_tsne_size)* 200)
        self.matrixWidget.resize((columnCount + 1) * 200, (columnCount) * 200)
        for j in range(0, columnCount):
            for i in range(0, columnCount):
                columnForAbscissas = columns[i]
                columnForOrdinates = columns[j]
                axes = self.figure.add_subplot(columnCount, columnCount, j * columnCount + i + 1)
                axes.scatterMatrixXIndex = columnForAbscissas.getIndex()
                axes.scatterMatrixYIndex = columnForOrdinates.getIndex()
                if columnForAbscissas == columnForOrdinates:
                    axes.hist(columnForAbscissas, facecolor=Constants.DEFAULT_HISTOGRAM_COLOR)
                    axes.set_title("гистограмма " + columnForOrdinates.getName())
                else:
                    axes.plot(columnForAbscissas, columnForOrdinates, linestyle="None")
                    axes.scatter(columnForAbscissas, columnForOrdinates, c=target, cmap=plt.cm.coolwarm, s=20, edgecolors='k')
                    axes.set_title(columnForOrdinates.getName() + "_" + columnForAbscissas.getName())

        self.matrixWidget.mpl_connect('button_press_event', self.canvasClicked)
        self.figure.tight_layout()
        self.figure.set_size_inches(columnCount*2, columnCount*2)
        self.figure.subplots_adjust(wspace=1.0, hspace=1.0)
        self.matrixWidget.draw()
        self.matrixScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.matrixScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def get_temp_tsne_column(self, column_number):
        temp_list = list()
        for i in range(0,len(self.temp_tsne_data)):
            temp_list.append(list(self.temp_tsne_data).__getitem__(i).__getitem__(column_number))
        return temp_list

    def drop_nan_values(self, array):
        result = copy.deepcopy(array)
        for i in range(0,list(result).__len__()):
            result[i] = float(result[i])
            if math.isnan(result[i]):
                del result[i]

    """мой нир"""
    def refreshCanvasSV(self,indexSet):
        columnCount = self.globalData.significantColumnCount()
        columns = self.globalData.getSignificantColumns()
        for i in range(0, columnCount):
            for j in range(0, columnCount):
                if i != j:
                    columnForAbscissas = columns[i]
                    columnForOrdinates = columns[j]
                    axes = self.figure.add_subplot(columnCount, columnCount, j * columnCount + i + 1)
                    xAll = columns[i]._data
                    yAll = columns[j]._data
                    target = self.globalData._target
                    Cluster.draw2DPointsSV(axes, xAll, yAll, target ,  plt.cm.coolwarm, 20, 'o')

                    xD=[]
                    yD=[]
                    target = []
                    for k in indexSet:
                        xD.append(columns[i].__getitem__(k))
                        yD.append(columns[j].__getitem__(k))
                        target.append(self.globalData._target[k])
                    Cluster.draw2DPointsSV(axes,xD,yD, target , plt.cm.Oranges, 6, '.')     #  spring

                    axes.set_title(columnForOrdinates.getName() + "_" + columnForAbscissas.getName())
        self.matrixWidget.draw()

    def refreshCanvas(self):
        """ Полное обновление изображения. Очищает канвас и отрисовывает все заново.

        """
        columnCount = self.globalData.significantColumnCount()
        columns = self.globalData.getSignificantColumns()

        for i in range(0, columnCount):
            for j in range(0, columnCount):
                if i != j:
                    columnForAbscissas = columns[i]
                    columnForOrdinates = columns[j]
                    axes = self.figure.add_subplot(columnCount, columnCount, j * columnCount + i + 1)
                    for cluster in self.clusters:
                        cluster.draw2DProjection(axes, columns[i].getIndex(), columns[j].getIndex(), self.globalData._target, Constants.DEFAULT_MARKER_SIZE_BIG)
                    dummyCluster = self.globalData.getDummyCluster(self.clusters)
                    dummyCluster.draw2DProjection(axes, columns[i].getIndex(), columns[j].getIndex(), self.globalData._target, Constants.DEFAULT_MARKER_SIZE_SMALL)
                    axes.set_title(columnForOrdinates.getName() + "_" + columnForAbscissas.getName())


                    if self.sphere is not None:
                       point = self.sphere[0].getProjection(i, j)
                       self.circle = plt.Circle((point.getX(), point.getY()), self.sphere[1], color='green', fill=False)
                       axes.add_artist(self.circle)
        self.matrixWidget.draw()

    def refreshClusterTable(self):
        """ Полное обновление таблицы кластеров. Удаляет все строки и создает их заново.

        """
        self.clustersTable.setRowCount(0)
        for cluster in self.clusters:
            self.addClusterToTable(cluster)

    def cleanupAppData(self):
        """ Полностью удаляет все данные из программы.
        Используется функцией startWorkingWithData перед загрузкой нового файла с данными.

        """
        self.clustersTable.setRowCount(0)
        self.clusters.clear()
        self.figure.clear()

    def createAdditionalProjection(self):
        self.additionalProjectionWindow = AdditionalProjectionWindow(self)

    def dbscanoptionChosen(self):
        """ Вызывает окно алгоритма DBScan

        """
        self.dbscanwindow = DBScanWindow(self)

    def tsneoptionChosen(self):
        """ Вызов окна алгоритма t-SNE

        """
        self.tsnewindow = TSNE(self)

    def clopeoptionChosen(self):
        """ Вызов окна алгоритма CLOPE

        """
        self.clopewindow = CLOPEWindow(self)