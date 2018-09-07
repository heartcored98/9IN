
def get_response(content):

    if content == u"구이니와 돈벌기":
        dataSend = {
            "message": {
                "text": "구이니 명령어 목록!\n1. 구이니 - 최신 구인글 리스트 표시\n2. 도움말 - 서비스 소개"
            }
        }
    elif content == u"도움말":
        dataSend = {
            "message": {
                "text": "뜨는 구인 글마다 마감이라 만들어봤습니다."
            }
        }
    elif u"구이니" in content:
        dataSend = {
            "message": {
                "text": "안녕~~ 반가워 ㅎㅎ"
            }
        }
    elif u"안녕" in content:
        dataSend = {
            "message": {
                "text": "안녕~~ 반가워 ㅎㅎ"
            }
        }
    elif u"시발" in content or u"씨발" in content:
        dataSend = {
            "message": {
                "text": "욕은 나쁜 으른이들이 하는거에요~"
            }
        }
    elif u"누가" in content:
        dataSend = {
            "message": {
                "text": "17 전산학부가 만들어쑝!"
            }
        }
    else:
        dataSend = {
            "message": {
                "text": ""
            }
        }
    return dataSend