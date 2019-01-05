from webmonitor import WebDriver
from bs4 import BeautifulSoup


class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = 'https://ara.kaist.ac.kr/board/Wanted/'
        WebDriver.__init__(self, target_url=self.target_url)

    def login(self, id, key):
        path_id = '//*[@id="miniLoginID"]'
        path_pw = '//*[@id="miniLoginPassword"]'
        path_btn = '//*[@id="loginBox"]/dd/form/ul/li[3]/a[1]'

        input_id = self.driver.find_element_by_xpath(path_id)
        input_id.send_keys(id)

        input_pw = self.driver.find_element_by_xpath(path_pw)
        input_pw.send_keys(key)

        # Login to the site
        self.click_btn(path_btn)

    def get_article(self, url):
        self.get_url(url)
        html = self.get_source()
        start_idx = html.find('<div class="article "')
        end_idx = html.find('</div>', start_idx)
        html = html[start_idx+23:end_idx].replace('<br />', ' ').replace('\n', ' ')
        html = ' '.join(html.split())
        html = html.strip()
        article = BeautifulSoup(html, 'lxml')
        return article.text