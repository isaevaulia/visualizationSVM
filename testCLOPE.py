# -*- coding: utf-8 -*-
import CLOPE
import getBins
import Utils
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint


def get_count_clusters(data, clope):
    '''
    Вывод распределения по оценочному признаку

    Input parametres:
    data -- исходный список транзакций
    clope -- объект CLOPE (рез-тат кластеризации)
    '''
    answ = []
    # clope.transaction -- cловарь <№транзакции/№кластера>
    for item in range(0, clope.max_cluster_number):
        # генератор образа распределения
        answ.append({'aa': 0,
                     'ba': 0,
                     'ca': 0,
                     'da': 0,
                     'ea': 0,
                     'fa': 0,
                     'ga': 0,
                     'ha': 0})
        # print('cluster appended')
    # print('max_cluster_number:', clope.max_cluster_number)
    print('Final clusters:')
    pprint(clope.clusters)
    # itemTransact = № транзакции
    for itemTransact in clope.transaction:
        # = № кластера
        cluster = clope.transaction[itemTransact]
        # data[itemTransact] - исходная транзакция
        # data[itemTransact][-1] = значение ценового признака
        answ[cluster][data[itemTransact][-1]] += 1

    return pd.DataFrame(answ)


def printCLOPER(transacts, seed, noiseLimit):
    '''
    Отрисовка вариационных кривых для
    различных параметров отталкивания

    Input parametres:
    transacts -- подготовленный набор транзакций
    '''
    # noiseLimit = 0
    # seed = 0
    plt.figure(figsize=(20, 10))
    plt.subplot()

    # назначение функции np.hstack?
    # linspace = np.hstack((np.arange(1.2, 2.6, 0.2),
    #                       np.arange(2.6, 3.5, 0.1),
    #                       np.arange(3.5, 5, 0.5)))
    linspace = np.arange(1.6, 3.5, 0.1)
    linspace = [round(i, 3) for i in linspace]
    for r in linspace:
        clope = CLOPE.CLOPE(print_step=0,
                            is_save_history=True,
                            random_seed=seed)
        clope.init_clusters(transacts, r, noiseLimit)
        df = get_count_clusters(transacts, clope)
        df['sum'] = df['aa7'] + df['ba7'] + df['ca7'] + df['da7'] + df['ea7'] + df['fa7'] + df['ga7'] + df['ha7']
        df = df.sort_values(by='sum')
        plt.plot(list(df['sum']))
    # plt.title('Вариационные ряды для размера кластера при различных r')
    plt.xlabel('Порядковый номер отсортированных по размеру кластеров')
    plt.ylabel('Размер кластера')
    plt.legend(linspace)
    plt.show()


if __name__ == '__main__':
    preparedData = getBins.prepareData(
        Utils.readExcelData(
            'data/CarData1Lab.xlsx'
        )
    )

    # print('Here is prepared data:')
    # pprint(preparedData)

    # Перемешивание данных
    seed = 0
    # seed = 40
    np.random.seed(seed)
    np.random.shuffle(preparedData)

    transacts = {}
    for i in range(0, len(preparedData)):
        for j in range(0, len(preparedData[i])):
            # для создания списка признаков в else
            if j != 0:
                # j=8 - 9-й эл-т, price, пропускаем
                if j != 8:
                    if preparedData[i][j] != '?':
                        transacts[i][j] = preparedData[i][j] + str(j)
                    else:
                        print('miss object')
                else:
                    pass
            else:
                transacts[i] = [''] * (len(preparedData[i]) - 1)
                transacts[i][j] = preparedData[i][j] + str(j)

    # print('Transacts:')
    # pprint(transacts)

    clope = CLOPE.CLOPE(print_step=1000,
                        is_save_history=True,
                        random_seed=seed)

    # Начальные данные
    repulsion = 1.5
    noiseLimit = 3

    # Инициализируем алгоритм
    clope.init_clusters(transacts, repulsion, noiseLimit)
    clope.print_history_count(repulsion, seed)

    # Тест:
    # print('max_cluster_number', clope.max_cluster_number, '(инициализация)')
    # print('Clusters dict:')
    # pprint(clope.clusters)
    # print('Noise clusters dict:')
    # pprint(clope.noise_clusters)

    # Итерируемся
    while clope.next_step(transacts, repulsion, noiseLimit) > 0:
        clope.print_history_count(repulsion, seed)

        # Тест:
        # print('max_cluster_number', clope.max_cluster_number, '(итерация)')
        # print('Clusters dict:')
        # pprint(clope.clusters)
        # print('Noise clusters dict:')
        # pprint(clope.noise_clusters)
        # pass

    clope.print_history_count(repulsion, seed)
    # printCLOPER(transacts, seed, noiseLimit)

    print(get_count_clusters(preparedData, clope))
