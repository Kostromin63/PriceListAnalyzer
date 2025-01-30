import os

import numpy as np
import pandas as pd

from tabulate import tabulate

pd.options.mode.copy_on_write = True


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

        #frames = [self.new_df]
        for head in headers:

            df = self.new_df
            r_df = pd.read_csv(head[3], header=0, index_col=False, usecols=head[:3],
                             keep_default_na=False, na_filter=False)

            # Удалим пустые колонки и строки если есть
            cleaned_col = r_df.dropna(axis=1)
            cleaned_str = r_df.dropna(axis=0)

            # получаем список прочитаных колонок как в файле
            ax = r_df.axes
            cols_in_r_df = ax[1].values
            # формируем словарь для правильной сортировки колонок для переименования нужных нам 3-х колонок
            indx_column = self._search_product_price_weight(cols_in_r_df)
            dict_columns_r_df = dict(zip(indx_column, cols_in_r_df))

            col1_from_f = dict_columns_r_df.get(0)
            col2_from_f = dict_columns_r_df.get(1)
            col3_from_f = dict_columns_r_df.get(2)

            col1_from_df = self.result_columns[1]
            col2_from_df = self.result_columns[2]
            col3_from_df = self.result_columns[3]



            r_df.rename({col1_from_f : col1_from_df,
                                 col2_from_f : col2_from_df,
                                 col3_from_f : col3_from_df}, axis=1, errors="ignore", inplace=True)

            product_price = r_df[col2_from_df]
            weight = r_df[col3_from_df]

            price_kg = product_price // weight

            r_df['цена за кг'] = price_kg
            r_df['файл'] = head[3]

            cleaned_df = r_df.dropna(axis=1)
            df = pd.concat([df, r_df], axis=0, ignore_index=True)
            self.new_df = df

        new_df = self.new_df
        new_df['№'] = pd.Series(np.arange(1,len(new_df.index)+1))
        # new_df['№'].apply(lambda x: pd.Series(np.arange(len(int(x))), x.index))
        #self.apply(lambda x: pd.Series(np.arange(len(x)), x.index))

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
    
    def find_text(self, search_text):

        nomenclatures = self.new_df[self.new_df['Наименование'].str.contains(search_text, case=False)]
        nomenclatures.sort_values(by=['цена за кг'], ignore_index=True, inplace=True)
        nomenclatures['№'] = pd.Series(np.arange(1, len(nomenclatures.index) + 1))

        print(tabulate(nomenclatures, headers='keys', tablefmt='psql', showindex=False))
        # print(tabulate(nomenclatures, headers='keys', tablefmt='psql', showindex=False))
        # print(nomenclatures)

if __name__ == "__main__":
    pm = PriceMachine()
    print(pm.load_prices(os.getcwd()))

    while True:
        search_text = input('Введите часть названия товара:')
        if search_text == 'exit':
            break
        else:
            pm.find_text(search_text)

    print('the end')
    print(pm.export_to_html())
