from parser import WebDriver
from utils import load_yml_config


settings = load_yml_config()


class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = settings.URL_ARA
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

    def get_post_list(self, num=10):


if __name__ == '__main__':
    parser = ParserARA()
    # parser.screenshot()

    parser.login()