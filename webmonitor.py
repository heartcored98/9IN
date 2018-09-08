from parser import WebDriver


class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = "http://ara.kaist.ac.kr/board/Wanted/"
        WebDriver.__init__(self, target_url=self.target_url)

    def login(self):
        path_id = '//*[@id="miniLoginID"]'
        path_pw = '//*[@id="miniLoginPassword"]'
        path_btn = '//*[@id="loginBox"]/dd/form/ul/li[3]/a[1]'

        input_id = self.driver.find_element_by_xpath(path_id)
        input_id.send_keys('whwodud98')

        input_pw = self.driver.find_element_by_xpath(path_pw)
        input_pw.send_keys('rocketboy7')


        self.click_btn(path_btn)
        self.screenshot('login.png')


if __name__ == '__main__':
    parser = ParserARA()
    # parser.screenshot()

    parser.login()