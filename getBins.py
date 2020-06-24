# -*- coding: utf-8 -*-
import Utils
import pandas as pd
from numpy import log2, floor


def getNamesOfBins(qnt: int):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    labels = []
    i = 0
    currentLen = 0
    letLen = len(letters)
    while len(labels) < qnt:
        labels.append(letters[i] + chr((currentLen // letLen) + 97))
        currentLen += 1
        i += 1
    return labels


def getNumberOfBins(qnt: int):
    return 1 + floor(log2(qnt))


def transformToRows(columns):
    rows = []

    # i - строка
    for i in range(0, len(columns[0])):
        rowArray = []
        # j - колонка
        for j in range(0, len(columns)):
            rowArray.append(columns[j][i])
        rows.append(rowArray)
    return rows


def prepareData(columns):
    newD = []

    # Категоризация колонок
    for col in columns:
        k = getNumberOfBins(len(col._data))
        newD.append(
            list(
                pd.cut(col._data,
                       bins=k,
                       labels=getNamesOfBins(k))
            )
        )
        # pprint(newD[-1])

    # Переход к транзакциям
    return transformToRows(newD)


if __name__ == '__main__':
    param = Utils.readExcelData('data/CarData1Lab.xlsx')
    # print(len(param[0]))
    # print(prepareData(param))
