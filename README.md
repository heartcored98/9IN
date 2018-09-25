# 9IN
**9IN**은 카이스트 교내 커뮤니티 사이트에 올라오는 새 구인글이나 마감 여부를 모니터링해서 텔레그램 메시지로 보내주는 비영리 서비스입니다.
텅장을 통장으로 바꾸기 위해 애쓰시는 모든 카이스트 학우분들께 바칩니다.

# Motivation  
카이스트 교내 커뮤니티 사이트인 아라 Wanted 탭에는 다양한 구인글이 올라온다. 가끔씩 괜찮은 일거리가 올라오지만 아라의 접근성은 낮고 자주 확인하기에도 너무 번거로워서 새 글이 올라오면 모바일 푸쉬 알람이 오면 좋겠다는 생각이 들었다.   

# Screenshots

# Tech/Framework Used
- [Python 3.6.5](https://www.python.org/downloads/release/python-365/) (Favorite Language)
- [requests](https://pypi.org/project/requests/) (Fast Posts Pulling)
- [bs4](https://pypi.org/project/beautifulsoup4/) (Parsing HTML Table)
- [selenium](https://pypi.org/project/selenium/) (Posts Content Pulling)
- linux_chromedriver (Mate of Selenium)
- [python-telegram-bot](https://python-telegram-bot.org/) (Telegram Push Notification)
- [ubuntu systemd](https://wiki.ubuntu.com/systemd)  (Automaitc Start & Restart)

# TODO
- [X] Fix delete post error
- [X] Filtering carful articles
- [X] Add telegram push notification
- [ ] Add content preview
- [ ] Add personal searching, filtering keyword on telegram bot
- [ ] Add portal monitoring 
- [ ] Execute the push message function as subprocess
