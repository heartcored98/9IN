from bs4 import BeautifulSoup
import requests
import pandas as pd
from utils import load_yml_config

class HTMLTableParser:

    def feed(self, html_string):
        soup = BeautifulSoup(html_string, 'lxml')
        return [self.parse_html_table(table) for table in soup.find_all('table')]

    def parse_html_table(self, table):
        n_columns = 0
        n_rows = 0
        column_names = []

        # Find number of rows and columns
        # we also find the column titles if we can
        for row in table.find_all('tr'):

            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows += 1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)

            # Handle column names if we find them
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0, n_columns)
        df = pd.DataFrame(columns=range(len(column_names)), index=range(0, n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')

            for column in columns:
                df.iat[row_marker, column_marker] = " ".join(column.get_text().split())
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1

        new_header = dict()
        for i, name in enumerate(column_names):
            new_header[i] = name
        new_header[0] = 'N'
        new_header[1] = 'id'
        df.rename(columns = new_header, inplace=True)

        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(int)
            except ValueError:
                pass

        return df

def get_ara_table(url='https://ara.kaist.ac.kr/board/Wanted/', test_mode=False):
    html_string = requests.get(url).text
    parser = HTMLTableParser()
    table = parser.feed(html_string)[0]
    table.index = table['id']
    table = table.drop(columns=['N', '작성자', '말머리', '추천/조회', '글쓴날짜', 'id'])

    table = table[~table['제목'].str.contains('카풀')]
    if not test_mode:
        table = table[~table['제목'].str.contains('TEST')]
    return table



if __name__ == '__main__':
    settings = load_yml_config()
    print(get_ara_table())
