from parser import WebDriver

PATH_SCREENSHOT_DIR = './screenshot'

# TODO : install headless chrome

class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = "http://ara.kaist.ac.kr/board/Wanted/"
        WebDriver.__init__(self, target_url=self.target_url)

    def screenshot(self, name="shoot.png"):
        filename = "{}/{}".format(PATH_SCREENSHOT_DIR, name)
        self.driver.save_screenshot(filename)


if __name__ == '__main__':
    parser = ParserARA()
    parser.screenshot()
