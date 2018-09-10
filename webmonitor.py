from parser import WebDriver
from utils import load_yml_config
from html_parser import HTMLTableParser
import pandas as pd
import requests
import os

settings = load_yml_config()


class MonitorARA():
    def __init__(self):
        self.target_url = settings.URL_ARA
        self.table_parser = HTMLTableParser()
        self.path_data_ara = settings.PATH_DATA_ARA
        self.p_table = self.load_table()

    def load_table(self):
        if os.path.isfile(self.path_data_ara):
            table = pd.read_csv(self.path_data_ara)
            table = table.drop(columns=['id.1'])
            table.index = table['id']
        else:
            table = self.get_table()
            self.save_table(table)
        return table

    def save_table(self, table):
        table.to_csv(self.path_data_ara)

    def set_p_table(self, table):
        self.p_table = table

    def get_table(self):
        html_string = requests.get(self.target_url).text
        table = self.table_parser.parse_html(html_string)[0]
        table.index = table['id']
        table = table.drop(columns=['N', '작성자', '말머리'])
        return table

    def find_update(self, p_table, c_table):
        set_p_index = set(p_table.index.values)
        set_c_index = set(c_table.index.values)
        set_new_posts = set_c_index - set_p_index
        set_old_posts = set_c_index - set_new_posts

        changed_posts = dict()
        finished_posts = dict()
        for id in set_old_posts:
            p_title = p_table.loc[[id]]['제목'].values[0]
            c_title = c_table.loc[[id]]['제목'].values[0]
            if p_title != c_title:
                if '마감' in c_title:
                    finished_posts[id] = c_title
                else:
                    changed_posts[id] = [p_title, c_title]

        new_posts = dict()
        for id in set_new_posts:
            c_title = c_table.loc[[id]]['제목'].values[0]
            new_posts[id] = c_title

        return new_posts, changed_posts, finished_posts

    def generate_url(self, index):
        template_url = 'http://ara.kaist.ac.kr/board/Wanted/{}/?page_no=1'
        return template_url.format(index)





class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = settings.URL_ARA
        self.table_parser = HTMLTableParser()
        WebDriver.__init__(self, target_url=self.target_url)

    def login(self):
        path_id = '//*[@id="miniLoginID"]'
        path_pw = '//*[@id="miniLoginPassword"]'
        path_btn = '//*[@id="loginBox"]/dd/form/ul/li[3]/a[1]'

        input_id = self.driver.find_element_by_xpath(path_id)
        input_id.send_keys(settings.ARA_ID)

        input_pw = self.driver.find_element_by_xpath(path_pw)
        input_pw.send_keys(settings.ARA_KEY)

        # Login to the site
        self.click_btn(path_btn)
        # self.screenshot('login.png')

    def get_table(self):
        path_table = '//*[@id="board_content"]/table'
        table = self.driver.find_element_by_xpath(path_table)
        html_string = table.get_attribute('innerHTML')
        html_string = self.driver.page_source
        tables = self.table_parser.parse_html(html_string)
        return tables


if __name__ == '__main__':
    # parser = ParserARA()
    # parser.screenshot()
    # parser.login()
    # table = parser.get_table()[0]

    monitor = MonitorARA()
    # Find new, changed, finished post test
    """
    with pd.option_context('display.max_rows', None, 'display.max_columns',
                           None):
        table = monitor.get_table()
        table = table.drop(table.index[[0,1,2,3,4,5,6,7,8]])
        old_table = table.drop([563752, 563762, 563779, 563783, 563794, 563798, 563809, 563818])
        old_table.at[563865, '제목'] = '슬라이드 제작 실험 || 2시간 소요 || 3만원 지급'
        old_table.at[563824, '제목'] = '[2시간, 2만원] 시선 추적 장치를 이용한 스마트 글래스 문자입력 실험... '

        # print(old_table)
        # print(table)

        monitor.find_update(old_table, table)
    """
    while True:
        new_table = monitor.get_table()
        new_posts, changed_posts, finished_posts = monitor.find_update(monitor.p_table, new_table)
        monitor.set_p_table(new_table)
        monitor.save_table(new_table)
        print(new_posts, changed_posts, finished_posts)

