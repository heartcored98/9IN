import logging

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from parser import WebDriver
from utils import load_yml_config


settings = load_yml_config()
logger = logging.getLogger(__name__)


class KakaoPusher(WebDriver):
    def __init__(self, request):
        self.target_url = settings.URL_KAKAO_LOGIN
        WebDriver.__init__(self, target_url=self.target_url)
        self.login()
        self.push_msg(request)
        self.quit_driver()

    def login(self):
        path_id = '//*[@id="loginEmail"]'
        path_pw = '//*[@id="loginPw"]'
        path_btn = '//*[@id="login-form"]/fieldset/button'

        input_id = self.driver.find_element_by_xpath(path_id)
        input_id.send_keys(settings.KAKAO_ID)

        input_pw = self.driver.find_element_by_xpath(path_pw)
        input_pw.send_keys(settings.KAKAO_KEY)
        logger.debug('Entered id and path')

        # Login to the site
        self.click_btn(path_btn)
        self.driver.find_element_by_link_text("나중에 하기").click()
        self.is_visible('//*[@id="kakaoBody"]/div/div/div[2]/div[3]/a/div', 1.0)
        logger.debug('Logged in')

        # Connect to message page
        self.driver.get(settings.URL_KAKAO_MSG)
        self.is_visible('//*[@id="mArticle"]/div/form/div[2]/span/button[2]', 1.0)
        logger.debug('Connect to message feed page')


    def push_msg(self, request):
        # Enable when full size screenshot is needed
        self.driver.set_window_size(1920, 1920)
        logger.info('Sending message...')

        # Type Clicking
        type = request.get('type', None)
        path_img = '//*[@id="mArticle"]/div/form/div[1]/div[1]/div[2]/div/div[2]/label/span'
        path_video = '//*[@id="mArticle"]/div/form/div[1]/div[1]/div[2]/div/div[3]/label/span'
        if type == 'img':
            self.click_btn(path_img)
        elif type == 'video':
            self.click_btn(path_video)
        logger.debug('Select message type')

        # Content Write
        content = request.get('content', "오류 발생!")
        path_field = '//*[@id="messageWrite"]'
        textfield = self.driver.find_element_by_xpath(path_field)
        textfield.send_keys(content)
        logger.debug('Write content')

        # Link Write
        link = request.get('link', None)
        if link:
            name = request.get('name', '페이지 열기')
            path_link  = '//*[@id="mArticle"]/div/form/div[1]/div[1]/div[4]/div/div[4]/label/span'
            path_name = '//*[@id="btnName"]'
            path_url = '//*[@id="linkUpload"]'

            self.screenshot('before_path_link.png')
            self.is_visible(path_link)
            self.click_btn(path_link)
            element_name = self.driver.find_element_by_xpath(path_name)
            element_name.send_keys(name)

            self.click_btn(path_url)
            element_url = self.driver.find_element_by_xpath(path_url)
            element_url.clear()
            element_url.send_keys(link)
            logger.debug('Entered link')

        # Send Msg
        path_send = '//*[@id="mArticle"]/div/form/div[2]/span/button[2]'
        self.click_btn(path_send)
        logger.debug('Clicked send button')

        path_register = '//*[@id="mArticle"]/div/form/div[2]/button[4]'
        self.is_visible(path_register)
        self.click_btn(path_register)

        path_confirm = '/html/body/div[4]/div[2]/div/div/div[2]/button[2]'
        self.is_visible(path_confirm)

        # Confirm Message
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB * 2)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        logger.debug('Clicked confirmation button')
        logger.info('Message sent')

        # Return to waiting state
        # self.driver.get(settings.URL_KAKAO_MSG)


if __name__ == '__main__':

    pusher = KakaoPusher()
    pusher.login()
    request = {'content':'테스트 메시지2', 'link':'http://ara.kaist.ac.kr/board/Wanted/563979/?page_no=1'}
    pusher.push_msg(request)