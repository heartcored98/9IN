from parser import WebDriver
from utils import load_yml_config
from html_parser import HTMLTableParser
import pandas as pd

settings = load_yml_config()


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
    parser = ParserARA()
    # parser.screenshot()

    parser.login()
    table = parser.get_table()[0]

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(table)