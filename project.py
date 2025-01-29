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
        self.new_df = pd.DataFrame(columns=['№', 'Наименование', 'цена', 'вес', 'файл', 'цена за кг'])

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
            numbers_column = self._search_product_price_weight(list_columns_file)
            # в конец списка добавляем имя файла
            numbers_column.append(file)
            headers.append(numbers_column)

        frames = [self.new_df]
        for head in headers:

            df = self.new_df
            r_df = pd.read_csv(head[3], header=0, index_col=False, usecols=head[:3],
                             keep_default_na=False, na_filter=False)

            ax = r_df.axes
            cols_in_r_df = ax[1].values
            #r_df = df.get([cols_in_r_df], default="default_value")
            indx_column = self._search_product_price_weight(cols_in_r_df)
            dict_columns_r_df = dict(zip(indx_column, cols_in_r_df))

            r_df.rename(columns={dict_columns_r_df.get(0): self.result_columns[1],
                                 dict_columns_r_df.get(1): self.result_columns[2],
                                 dict_columns_r_df.get(2): self.result_columns[3]})
            #r_df.rename(columns={'название' : 'Yfbsjadk'})

            r_df['файл'] = head[0]
            df = pd.concat([df, r_df], axis=1, ignore_index=True)

            b = 6


            #df.rename(columns={"A": "a", "B": "c"})
            #df = pd.concat([df, df1], axis=1, ignore_index=True)
            #df.columns = ['Наименование']
            # df = df(usecols=['Наименование', 'цена', 'вес'])
            #df = df.get([])
            #ax = df.axes

            #df['цена за кг'] = df['цена'] / df['вес']
            # col = df.get([0], default="default_value")



            #df_reordered = df[0:3]
            #frames.append(df)
            #print(df)

        #new_df = pd.concat(frames, axis=0, ignore_index=True)
        # new_df['цена за кг'] = new_df['цена'] / new_df['вес']
#        new_df['№'] = df.index
        self.new_df = df
        #print(self.new_df )

        return self.new_df

    def _search_product_price_weight(self, headers):
        '''
            Возвращает номера столбцов
        '''
        valid_column_names = ['товар', 'название', 'наименование', 'продукт', 'розница', 'цена', 'вес', 'масса',
                              'фасовка']
        new_numbers_column = [None, None, None]
        column_counter = 0
        for i in headers:
            column_counter += 1
            if i in valid_column_names:
                ind = valid_column_names.index(i)
                if ind < 4:
                    ind_ins = 0
                elif ind > 5:
                    ind_ins = 2
                else:
                    ind_ins = 1
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
        '''
        result = result + '\t' + self.new_df.to_html() + '\n'+'</body>'
        html_file = open(fname, "w+", encoding='utf-8')
        html_file.write(result)
        html_file.close()
        self.result = result
        return result
    
    def find_text(self, text):

        nomenclatures = self.new_df[self.new_df[6].str.contains(text)]

        print(nomenclatures)



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
