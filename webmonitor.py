from parser import WebDriver


class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = "http://ara.kaist.ac.kr/board/Wanted/"
        WebDriver.__init__(self, target_url=self.target_url)

    def login(self):
        pass


if __name__ == '__main__':
    parser = ParserARA()
    parser.screenshot()
