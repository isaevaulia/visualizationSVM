import copy
import time
from sklearn import svm
import ParamW
from ScaleAdjustments import *
from UtilityClasses import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class TWindow(QMainWindow):
    """ Окно детального изучения графика.

    """
    clusterAdjustmentWindow = None
    scalingAdjustmentWindow = None

    def __init__(self, parent, x_tsne, y_tsne, x, y, SV):
        super().__init__(parent)

        self.allData = parent.globalData
        self._x = x
        self._SV = SV
        self._x_tsne = x_tsne
        self._y_tsne = y_tsne
        self.target = y

        self.menubar = self.menuBar()
        self.parametersMenu = self.menubar.addMenu("Параметры")

        self._selectionPolygon = []
        self._selectedPoints = []
        self._modelIndex = []
        self._xData = []
        self._yData = []
        self.setGeometry(100, 100, 1500, 480)
        self.setWindowTitle("TSNE")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QHBoxLayout(self.centralWidget)
        self.layout.setContentsMargins(0,0,0,0)

        self.tabWidget = QTabWidget()
        self.layout.addWidget(self.tabWidget)

        self.figure = Figure()
        self.barWidget = FigureCanvas(self.figure)

        self.layout.addWidget(self.barWidget)
        self.setLayout(self.layout)

        self._axes = self.figure.add_subplot(111)
        self._axes.scatter(x_tsne, y_tsne, c=self.target, cmap=plt.cm.coolwarm)

        self.barWidget.draw()

        # "МОЁ"
        self.supportVectorView = QWidget()
        self.tabWidget.addTab(self.supportVectorView, "Точки")
        self.supportVectorViewLayout = QVBoxLayout(self.supportVectorView)

        self.tableHeaderSV = QLabel("Выделенные точки")
        self.tableHeaderSV.setAlignment(Qt.AlignCenter)
        self.supportVectorViewLayout.addWidget(self.tableHeaderSV)

        self.pointsTable = QTableWidget()
        self.pointsTable.setColumnCount(3)
        self.pointsTable.setHorizontalHeaderLabels(["абсцисса", "ордината",""])
        self.supportVectorViewLayout.addWidget(self.pointsTable)

        self.buttonGroupSV = QWidget()
        self.buttonGroupSVLayout = QGridLayout(self.buttonGroupSV)
        self.clearSelectionButtonSV = QPushButton("Очистить выделение")
        self.clearSelectionButtonSV.clicked.connect(self.clearSelection)
        self.selectionCompleteButtonSV = QPushButton("Завершить выделение")
        self.selectionCompleteButtonSV.clicked.connect(self.selectionCompleted)
        self.noteOnAllGraphButtonSV = QPushButton("Выделить на др. графиках")
        self.noteOnAllGraphButtonSV.clicked.connect(self.noteOnAll)
        self.noteTrueButtonSV = QPushButton("Выделить опорные векторы")
        self.noteTrueButtonSV.clicked.connect(self.noteTrueSV)
        self.noteCancelSV = QPushButton("Отменить выделение на др. графиках")
        self.noteCancelSV.clicked.connect(self.noteCancel)
        self.addSelectionButton = QPushButton("Добавить выделение")
        self.addSelectionButton.clicked.connect(self.addSelection)
        self.buildModelButton = QPushButton("Построить модель")
        self.buildModelButton.clicked.connect(self.buildModel)
        self.buttonGroupSVLayout.addWidget(self.selectionCompleteButtonSV, 1, 1)
        self.buttonGroupSVLayout.addWidget(self.clearSelectionButtonSV, 1, 2)
        self.buttonGroupSVLayout.addWidget(self.noteOnAllGraphButtonSV, 2, 1)
        self.buttonGroupSVLayout.addWidget(self.noteTrueButtonSV, 2, 2)
        self.buttonGroupSVLayout.addWidget(self.addSelectionButton, 3, 1)
        self.buttonGroupSVLayout.addWidget(self.noteCancelSV, 3, 2)
        self.buttonGroupSVLayout.addWidget(self.buildModelButton, 4, 1)
        self.supportVectorViewLayout.addWidget(self.buttonGroupSV)

        cid2 = self.barWidget.mpl_connect('button_press_event', self.onclick)

        self.show()


    def buildModel(self):
        """ Обработчик клика на кнопку "Построить модель"

                   """
        if self._selectedPoints == []:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Плоскость не может быть построена")
            msg.setInformativeText("Не выделено ни одной точки")
            msg.setStyleSheet(  # TODO разобраться как выровнять кнопку ОК по центру
                'QMessageBox {text-align: center;}\n QPushButton:center{margin: auto;}\n QPushButton:hover{color: #2b5b84;}')
            msg.setWindowTitle("Внимание")
            msg.exec_()
        else:
            """SVM"""
            self.kernel = "linear"
            self.c = 1
            self.gamma = 'scale'
            win = ParamW.ParamWindow(self)
            win.exec_()

            x = []
            y = []
            for i, point in enumerate(self._selectedPoints):
                x.append(self._x[point.getIndex()])
                y.append(self.target[point.getIndex()])

            start = time.time_ns()
            clf = svm.SVC(kernel=self.kernel, C = self.c, gamma = self.gamma)
            clf.fit(x, y)
            end = time.time_ns()
            print(end - start)

            index_set = set()
            for i in clf.support_:
                index_set.add(self._selectedPoints[i].getIndex())
            self._modelIndex = index_set
            print('Our SV (after T-SNE)', index_set)

            x = []
            y = []
            for i in range(self.allData.__len__()):
                x.append(self.allData.__getitem__(i)._dataArray)

            for yel in self.allData._target:
                y.append(yel)
            sc = clf.score(x, y)

            print("Точность модели тсне", str(sc))

            selectedXData = []
            selectedYData = []
            for i in index_set:
                selectedXData.append(self._x_tsne[i])
                selectedYData.append(self._y_tsne[i])
            self._axes.plot(selectedXData, selectedYData,
                            linestyle="None",
                            marker='.',
                            color='k',
                            markersize=6)
            self.barWidget.draw()



    def noteTrueSV(self):
        if (self._SV == []):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Опорные векторы не были найдены")
            msg.setInformativeText("Примените алгоритм Выделить опорные векторы")
            msg.setStyleSheet(  # TODO разобраться как выровнять кнопку ОК по центру
                'QMessageBox {text-align: center;}\n QPushButton:center{margin: auto;}\n QPushButton:hover{color: #2b5b84;}')
            msg.setWindowTitle("Внимание")
            msg.exec_()
        else:
            self.refreshPlot()
            points = []
            for i in self._SV:
                point = Point(self._x_tsne[i], self._y_tsne[i], i)
                points.append(point)

            selectedXData = []
            selectedYData = []
            for i, point in enumerate(points):
                selectedXData.append(point.getX())
                selectedYData.append(point.getY())
            self._axes.plot(selectedXData, selectedYData,
                            linestyle="None",
                            marker=Constants.DEFAULT_SELECTION_SHAPE,
                            color=Constants.DEFAULT_SELECTION_COLOR,
                            markersize=5)
            self.barWidget.draw()



    def onclick(self, event):
        """ Обработчик клика мыши.

        :param event: событие - клик мыши
        """
        mousex, mousey = event.xdata, event.ydata
        self._axes = event.inaxes
        if (mousex != None) and (mousey != None):
            point = Point(mousex, mousey, None)
            self._selectionPolygon.append(point)
            # почему два, а не один? Программирование наугад.
            lineAmount = 2
            # рисуем выделение
            Utils.drawBrokenLine(self._selectionPolygon, self.barWidget)


    def clearSelection(self):
        """ Обработчик клика на кнопку "Очистать выделение"

        """
        self.refreshPlot()
        self.pointsTable.setRowCount(0)
        self._selectedPoints = []
        self._selectionPolygon = []
        self.barWidget.draw()

    def selectionCompleted(self):
        """ Обработчик клика на кнопку "Завершить выделение"
        """
        #self._selectedPoints.clear()
        self.pointsTable.setRowCount(0)
        if len(self._selectionPolygon) < 3:
            self.statusBar().showMessage("Область выделения не определена")
        else:
            points = []
            for i in range(0, len(self._x_tsne)):
                point = Point(self._x_tsne[i], self._y_tsne[i], i)
                for cluster in self.parent().clusters:
                    innerClusterData = cluster.getInnerData()
                    if innerClusterData.getRowByRowOriginalIndex(i) is not None and innerClusterData.getRowByRowOriginalIndex(i).isHidden():
                        point.setHidden(True)
                        break
                points.append(point)
            for point in points:
                if Utils.crossingNumberAlgorithm(point, self._selectionPolygon) and not point.isHidden():
                    self._selectedPoints.append(point)

            selectedXData = []
            selectedYData = []
            verticalHeaders = []
            for i, point in enumerate(self._selectedPoints):
                verticalHeaders.append(str(point.getIndex()))
                selectedXData.append(point.getX())
                selectedYData.append(point.getY())
                self.pointsTable.setRowCount(self.pointsTable.rowCount() + 1)
                self.pointsTable.setItem(i, 0, QTableWidgetItem(str(point.getX())))                    #заносят индексы в таблицу
                self.pointsTable.setItem(i, 1, QTableWidgetItem(str(point.getY())))
                removePointButton = QPushButton("Убрать")
                index = QPersistentModelIndex(self.pointsTable.model().index(i, 2))
                removePointButton.clicked.connect(
                    lambda *args, index=index: self.removePoint(index.row()))
                self.pointsTable.setCellWidget(i, 2, removePointButton)
            self._axes.plot(selectedXData, selectedYData,
                            linestyle = "None",
                                marker = Constants.DEFAULT_SELECTION_SHAPE,
                                color = Constants.DEFAULT_SELECTION_COLOR,
                                markersize = 3)
            self.pointsTable.setVerticalHeaderLabels(verticalHeaders)
            # # #
            self.all_points = copy.deepcopy(self._selectedPoints)
            # # #
            Utils.drawPolygon(self._selectionPolygon, self.barWidget)

    def noteOnAll(self):
        """отмечает выделенные точки на всех графиках"""
        if self._selectedPoints == []:
             msg = QMessageBox()
             msg.setIcon(QMessageBox.Warning)
             msg.setText("Точки не могут быть выделены на всех графиках")
             msg.setInformativeText("Не выделено ни одной точки на данном графике")
             msg.setStyleSheet( #TODO разобраться как выровнять кнопку ОК по центру
                 'QMessageBox {text-align: center;}\n QPushButton:center{margin: auto;}\n QPushButton:hover{color: #2b5b84;}')
             msg.setWindowTitle("Внимание")
             msg.exec_()
        else:
            indexSet = set()
            for point in self._selectedPoints:
                indexSet.add(point.getIndex())
            self.parent().refreshCanvasSV(indexSet)


    def noteCancel(self):
        self.parent().refreshCanvas()

    def addSelection(self):
        self._selectionPolygon = []
        return "hello"

    def refreshPlot(self):
        """ Очищает график и рисует его заново.

        """
        while len(self._axes.lines) > 0:  # С удалением в matplotlib большие странности. По какой-то причине
            del self._axes.lines[-1]  # нет нормального способа очистить график (или я чего-то не понял?).
            # Но подобные циклы делают дело.
        self._axes.plot(self._xData, self._yData,
                        linestyle="None"
                        )
        # Рисуем сначала все кластеры последовательно, а потом фантомный кластер состоящий из точек,
        # не принадлежащих ни одному кластеру

        self._axes.scatter(self._x_tsne, self._y_tsne, c=self.target, cmap=plt.cm.coolwarm)

    def removePoint(self, index):
        """ Удаляет точку из выделения

        :param index: идентификатор точки
        """
        del self._selectedPoints[index]
        self.pointsTable.removeRow(index)
        self.refreshPlot()

        selectedXData = [] # TODO избавиться от дублирования кода и сделать функцию drawSelectedPoints.
        # Речь идет о таком же механизме рисования в selectionCompleted
        selectedYData = []
        for i, point in enumerate(self._selectedPoints):
            selectedXData.append(point.getX())
            selectedYData.append(point.getY())
            self._axes.plot(selectedXData, selectedYData,
                            linestyle="None",
                            marker=Constants.DEFAULT_SELECTION_SHAPE,
                            color=Constants.DEFAULT_SELECTION_COLOR,
                            markersize=Constants.DEFAULT_SELECTION_POINT_SIZE)
        Utils.drawPolygon(self._selectionPolygon, self.barWidget)


