import os
import json
from types import new_class

import pandas as pd
import glob
import re

from pandas.io.formats.format import return_docstring

class PriceMachine:
    
    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 0
        self.result_columns = ['№', 'Наименование', 'цена', 'вес', 'файл', 'цена за кг']
        self.new_df = pd.DataFrame(columns=['Наименование', 'цена', 'вес'])

    def load_prices(self, file_path=''):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт
                
            Допустимые названия для столбца с ценой:
                розница
                цена
                
            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        '''

        list_files = [f for f in os.listdir(file_path) if os.path.isfile(f) and 'price' in str(f)]
        headers = []
        for file in list_files:
            # читаем только заголовки
            list_columns_file = pd.read_csv(file).columns.to_list()
            # Из заголовков выбираем индексы только необходимых нам колонок
            numbers_column = self._search_product_price_weight(list_columns_file, file)
            headers.append(numbers_column)

        frames = [self.new_df]
        for head in headers:
            #df = pd.read_csv(head[0], header=None, index_col=head[1:4]) #) # pd.read_csv(data[0], usecols=data[1:4])
            #df = pd.read_csv(head[0], usecols=head[1:4])
            #df = pd.DataFrame({'Наименование':[], 'цена':[], 'вес':[]})
            df = pd.read_csv(head[0], header= 0, index_col=head[1:4])
            #df = pd.concat([df, df1], axis=1, ignore_index=True)
            #df.columns = ['Наименование']
            #df = df.rename(columns={'0': '1', '1': '2', '2': '3'}
            # df = df(usecols=['Наименование', 'цена', 'вес'])
            df = df.get([], default="default_value")

            #df_reordered = df[0:3]
            #df = pd.read_csv(head[0], header=1, data={'Наименование':head[1], 'Цена':head[2], 'Вес':head[3]})
            frames.append(df)
            print(df)

        self.new_df = pd.concat(frames, axis=1, ignore_index=True)
        print(self.new_df )

        return self.new_df

    def _search_product_price_weight(self, headers, file):
        '''
            Возвращает номера столбцов
        '''
        valid_column_names = ['товар', 'название', 'наименование', 'продукт', 'розница', 'цена', 'вес', 'масса',
                              'фасовка']
        new_numbers_column = [file, None, None, None]
        column_counter = 0
        for i in headers:
            column_counter += 1
            if i in valid_column_names:
                ind = valid_column_names.index(i)
                if ind < 4:
                    ind_ins = 1
                elif ind > 5:
                    ind_ins = 3
                else:
                    ind_ins = 2
                new_numbers_column[ind_ins] = column_counter - 1


        return new_numbers_column

    def export_to_html(self, fname='output.html'):
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
    
    def find_text(self, text):

        filtered_df = self.new_df[self.new_df['Наименование'].str.contains(text)]

        print(filtered_df)



if __name__ == "__main__":
    pm = PriceMachine()
    print(pm.load_prices(os.getcwd()))

    while True:
        text = input('Введите часть названия товара:')
        if text == 'exit':
            break
        else:
            pm.find_text(text)


    print('the end')
    print(pm.export_to_html())

