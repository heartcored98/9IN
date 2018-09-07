#!/home/ubuntu/anaconda3/bin/python3

# from pytz import timezone
from datetime import date, datetime
from multiprocessing import Pool
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Manager
from functools import partial
import time
import json
import pprint
import os, signal
import logging

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui
# from tqdm import tqdm

# from kor2eng import Kor2Eng
# from logger import setup_logging

FLAG_DEBUG = False

IDX_KT = (1, 7, 1, 50)
IDX_LG = (1, 10)
IDX_SKT = (2, 20)

BASE_PATH = '/home/ubuntu/server_dothome'
PHANTOMJS_PATH = '/usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'


class WebDriver:
    """Wrapper Class of webdriver which has useful functionality
    This class handle all the web browsing process with connecting to url,
    clicking button on website, extracting text on websites. Also it has
    its own retry decorator feature which enable auto-reconnection when
    initial attempt get failed.
    """

    def __init__(self, target_url, window=False):
        self.logger = logging.getLogger(__name__)

        self.count_reset = 0
        self.MAX_COUNT = 5

        self.target_url = target_url
        self.window = window
        self.driver = None
        self.start_driver()

    def set_counter(self, MAX_COUNT=5):
        self.MAX_COUNT = MAX_COUNT

    def reset_driver(self):
        self.logger.info("start resetting driver")
        if self.count_reset >= self.MAX_COUNT:
            self.quit_driver()
            # time.sleep(1)
            self.start_driver()
            self.count_reset = 0
        else:
            self.count_reset += 1
        self.logger.info("end resetting driver")

    def start_driver(self, **kwargs):
        self.logger.info("driver warming up")

        try:

            if not bool(kwargs):
                self.driver = webdriver.PhantomJS(PHANTOMJS_PATH)
            else:
                self.driver = webdriver.PhantomJS(PHANTOMJS_PATH, kwargs)
            """
            options = webdriver.ChromeOptions()
            options.add_argument("headless")  # remove this line if you want to see the browser popup
            self.driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/bin/chromedriver')
            """
        except:
            self.logger.critical("some error", exc_info=True)
        self.driver.get(self.target_url)
        self.logger.info("new driver generated")

    def quit_driver(self):
        try:
            if self.driver is not None:
                self.driver.service.process.send_signal(signal.SIGTERM)
                self.driver.quit()
                self.logger.info("driver terminated")

        except:
            self.logger.error('error in quit_driver', exc_info=True)

    def get_pid(self):
        try:
            if self.driver is not None:
                return self.driver.service.process.pid
        except:
            return -1

    def _retry(func):
        def retried_func(*args, **kwargs):
            MAX_TRIES = 2
            tries = 1
            while True:
                try:
                    resp = func(*args, **kwargs)
                    return resp
                except NoSuchElementException:
                    raise NoSuchElementException
                except:
                    logger = logging.getLogger(__name__)
                    error = "error is occured {} times @{}".format(str(tries), func.__name__)
                    logger.error(error, exc_info=True)
                    tries += 1
                    # time.sleep(0.5)
                    if tries > MAX_TRIES:
                        raise
                    continue

        return retried_func

    def is_visible(self, locator, timeout=1.0):
        try:
            ui.WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False
        except:
            self.logger.error("error in is_visible", exc_info=True)
            return False

    @_retry
    def get_text(self, path):
        try:
            if self.is_visible(path):
                context = self.driver.find_element_by_xpath(path)
                return context.text
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            raise NoSuchElementException

        except Exception:
            self.logger.error("error in get text", exc_info=True)
            raise


    # @_retry
    def click_btn(self, path):
        try:
            if self.is_visible(path):
                btn = self.driver.find_element_by_xpath(path)
                btn.click()
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            pass
        except Exception:
            self.logger.error("error in click_btn", exc_info=True)
            raise

class Parser:
    def __init__(self, target_url="", region="SEOUL", device="", window=False, cpu_count=2, timeout=20):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Parser [{}/{}] is created".format(region, device))

        self.flag_translate = True
        self.target_url = target_url
        self.driver = WebDriver(window=window, target_url=self.target_url)
        self.region = region
        self.device = device
        self.cpu_count = cpu_count
        self.timeout = timeout
        self.logger.info("Parser [{}/{}] is setup".format(region, device))

    @classmethod
    def abortable_worker(cls, func, *args, **kwargs):
        timeout = kwargs.get('timeout', None)
        p = ThreadPool(1)
        res = p.apply_async(func, args=args)
        try:
            out = res.get(timeout)  # Wait timeout seconds for func to complete.
            p.terminate()
            return out
        except multiprocessing.TimeoutError:
            p.terminate()
            print("Aborting due to timeout", args)
            return "Failed"

    @classmethod
    def make_date(cls, hour=None, minute=None, time_shift=0, now=False):
        dt_now = datetime.now(timezone('Asia/Seoul'))
        date_today = date(dt_now.year, dt_now.month, dt_now.day)
        date_yesterday = date.fromordinal(date_today.toordinal() + time_shift)
        dt_now = datetime(year=date_yesterday.year, month=date_yesterday.month, day=date_yesterday.day)
        if now:
            return datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
        if hour is None:
            dt_program = datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day, hour=0, minute=0)
            return dt_program.strftime('%Y-%m-%d')
        else:
            dt_program = datetime(year=dt_now.year, month=dt_now.month, day=dt_now.day, hour=hour, minute=minute)
            return dt_program.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def str2date(cls, date_str):
        if len(date_str) > 10:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        return date

    def handle_empty_dict(self, dictionary):
        if not bool(dictionary):
            dt_program = self.make_date(hour=0, minute=0)
            name_program = "information is not available"
            dictionary[dt_program] = name_program
        return dictionary

    def convert_englist(self, program_name):
        if self.flag_translate:
            eng_name = Kor2Eng.convert(program_name)
            return eng_name
        else:
            return program_name

    def get_channel_list(self, time_shift):
        # Override Here #
        return dict(), dict()

    def save_channel_data(self, time_shift=0):
        generated_date = str(self.make_date(now=True))
        target_date = str(self.make_date(time_shift=time_shift))

        self.logger.warning("start crawling [{}/{}] on {}".format(self.region, self.device, target_date))
        self.driver.start_driver()
        dict_list, dict_time = self.get_channel_list(time_shift=time_shift)
        num_list = len(dict_list)

        outjson = {
            'region': self.region,
            'device': self.device,
            'target_date': target_date,
            'generated_date': generated_date,
            'channel_size': num_list,
            'dict_channel_list': dict_list,
            'dict_channel_time': dict_time
        }
        filename = BASE_PATH + '/channel_datas/{}_{}_{}.json'.format(self.region,
                                                                     self.device,
                                                                     target_date)
        preview = pprint.pformat(outjson, depth=1)
        self.logger.warning("end crawling [{}/{}] channels [{}/{}]\n{}\n".format(len(dict_time),
                                                                                 len(dict_list),
                                                                                 self.region,
                                                                                 self.device,
                                                                                 preview))
        try:
            with open(filename, 'w') as outfile:
                json.dump(outjson, outfile, ensure_ascii=False)
        except:
            error = 'error in saving json'
            self.logger.error(error, exc_info=True)

    def update_channel_data(self):
        self.logger.warning("start updating database")
        dirname = BASE_PATH + '/channel_datas'
        date_now = str(self.make_date())
        fname = '{}_{}_{}.json'.format(self.region, self.device, date_now)
        if fname not in os.listdir(dirname):
            self.save_channel_data()
        self.save_channel_data(time_shift=1)
        self.logger.warning("end updating database")


class ParserKT(Parser):
    def __init__(self):
        kt_url = "http://tv.kt.com/tv/channel/pChInfo.asp"
        Parser.__init__(self, target_url=kt_url, device='KT')
        self.NUM_CHANNEL = 274
        self.logger.info("initialize driver done")

    @staticmethod
    def convert_name(original_name):
        live_idx = original_name.find('방송중')
        if live_idx is -1:
            return original_name
        else:
            conv_name = original_name[4:]
            return conv_name

    def get_target_channel_time(self, count, time_shift):
        path_hour = '//*[@id="listSchedulePanel"]/ul/li[1]' \
                    '/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(str(count))
        path_min = '//*[@id="listSchedulePanel"]/ul/li[1]' \
                   '/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(str(count))
        path_name = '//*[@id="listSchedulePanel"]/ul/li[1]' \
                    '/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(str(count))

        hour = self.driver.get_text(path_hour)
        minute = self.driver.get_text(path_min).split('\n')
        name = self.driver.get_text(path_name).split('\n')

        list_channel_time = list()
        for i, _ in enumerate(minute):
            dt_program = self.make_date(hour=int(hour), minute=int(minute[i]), time_shift=time_shift)
            name_program = self.convert_name(name[i])
            name_program = self.convert_englist(name_program)
            list_channel_time.append((dt_program, name_program))
        return list_channel_time

    def get_channel_time(self, time_shift):
        dict_channel_time = dict()
        count = 1
        while True:
            try:
                list_channel_time = self.get_target_channel_time(count=count, time_shift=time_shift)
                for dt_program, name_program in list_channel_time:
                    dict_channel_time[dt_program] = name_program
                count += 1
            except NoSuchElementException:
                break

        dict_channel_time = self.handle_empty_dict(dict_channel_time)
        return dict_channel_time

    def parse_channel(self, col, row, time_shift):
        channel_path = '//*[@id="listChannelPanel"]/ul[{}]/li[{}]'.format(str(col), str(row))
        channel_text = self.driver.get_text(path=channel_path)
        separate_index = channel_text.find(' ')
        num_channel = int(channel_text[:separate_index])
        name_channel = channel_text[separate_index + 1:]

        time_path = '// *[ @ id = "linkChannel{}"] / span'.format(str(num_channel))
        try:
            self.driver.click_btn(path=time_path)
            time.sleep(1)
        except:
            error = "error in click_btn tab {},{}".format(str(col), str(row))
            self.logger.error(error, exc_info=True)
            raise

        if time_shift > 0:
            next_path = '//*[@id="listSchedulePanel"]/ul/li[1]/div/div[1]/div/a[2]'
            # TODO insert try except
            self.driver.click_btn(path=next_path)
            self.logger.info("move to next day tab")
            time.sleep(1)

        if num_channel > 608:
            dict_time = dict()
        else:
            dict_time = self.get_channel_time(time_shift=time_shift)
        dict_time = self.handle_empty_dict(dict_time)
        return num_channel, name_channel, dict_time

    def get_channel_list(self, time_shift):
        dict_channel_list = dict()
        dict_channel_time = dict()
        idx11, idx12, idx21, idx22 = IDX_KT[0], IDX_KT[1], IDX_KT[2], IDX_KT[3]
        try:
            assert idx11 == 1 and idx12 == 7 and idx21 == 1 and idx22 == 50
        except:
            self.logger.critical("idx should be 1, 7, 1, 50 not {}, {}, {}, {}".format(str(idx11),
                                                                                       str(idx12),
                                                                                       str(idx21),
                                                                                       str(idx22)))
        for col in range(idx11, idx12):  # should be range(1, 7)
            for row in range(idx21, idx22):  # should be range(1, 50)
                self.driver.reset_driver()
                try:
                    t_start = time.time()
                    num_channel, name_channel, dict_time = self.parse_channel(col=col, row=row,
                                                                              time_shift=time_shift)
                    t_process = time.time() - t_start

                    dict_channel_list[num_channel] = name_channel
                    dict_channel_time[num_channel] = dict_time
                    self.logger.warning("\tcrawled [{:>3}/{:2}] ({:3.2f}s) [{}]".format(str(num_channel),
                                                                                        len(dict_time),
                                                                                        t_process,
                                                                                        name_channel))
                except NoSuchElementException:
                    continue
                except:
                    error = "error in parse_chanel {}/{}".format(str(col), str(row))
                    self.logger.error(error, exc_info=True)
                    continue

        self.driver.quit_driver()
        return dict_channel_list, dict_channel_time


class ParserLG(Parser):
    def __init__(self):
        lg_url = "https://www.uplus.co.kr/css/chgi/chgi/RetrieveTvContentsMFamily.hpi"
        Parser.__init__(self, target_url=lg_url, device='LG')

        self.driver.set_counter(MAX_COUNT=1)
        self.NUM_CHANNEL = 188
        self.logger.info("initialize driver done")

    @staticmethod
    def convert_name(original_name):
        name = original_name
        tags = ['해', '수', '자', 'HD',
                'All', '15', '19', '7']
        for tag in tags:
            separate_index = original_name.find(tag, len(name) - 4)
            if separate_index > 0:
                name = original_name[:separate_index]
        return name

    def get_target_channel_time(self, count, time_shift):
        path_time = '//*[@id="SCHEDULE"]/div/div[2]/table/tbody/tr[{}]/td[1]'.format(str(count))
        path_name = '//*[@id="SCHEDULE"]/div/div[2]/table/tbody/tr[{}]/td[2]'.format(str(count))

        times = self.driver.get_text(path=path_time).split(':')
        name_program = self.driver.get_text(path=path_name)

        dt_program = self.make_date(hour=int(times[0]), minute=int(times[1]), time_shift=time_shift)
        name_program = self.convert_name(original_name=name_program)

        name_program = self.convert_englist(program_name=name_program)
        return dt_program, name_program

    def get_channel_time(self, time_shift):
        dict_channel_time = dict()
        count = 1
        while True:
            try:
                dt_program, name_program = self.get_target_channel_time(count, time_shift=time_shift)
                dict_channel_time[dt_program] = name_program
                count += 1
            except NoSuchElementException:
                # If found any NSE error, stop looking down and return the current time dictionary
                break
        # TODO make handle empty dict
        if not bool(dict_channel_time):
            dt_program = self.make_date(hour=0, minute=0)
            name_program = "information is not available"
            dict_channel_time[dt_program] = name_program
        return dict_channel_time

    def parse_channel(self, tab, id_channel, time_shift):
        tab_path = '//*[@id="{}"]'.format(str(tab))
        try:
            self.driver.click_btn(path=tab_path)
            time.sleep(1)
        except:
            error = "error in click_btn tab {}".format(str(tab))
            self.logger.error(error, exc_info=True)
            raise

        channel_path = '//*[@id="{}"]'.format(str(id_channel))
        self.driver.click_btn(path=channel_path)
        time.sleep(1)

        if time_shift > 0:
            next_path = '//*[@id="SCHEDULE"]/div/div[1]/div[1]/a[2]'
            self.driver.click_btn(path=next_path)
            time.sleep(1)
            self.logger.info("move to next day tab")

        channel_text = self.driver.get_text(path=channel_path)
        start_index = channel_text.find('(Ch.')
        end_index = channel_text.find(')', start_index)

        num_channel = int(channel_text[start_index + 4:end_index])
        name_channel = channel_text[:start_index]
        dict_time = self.get_channel_time(time_shift=time_shift)

        return num_channel, name_channel, dict_time

    def get_channel_list(self, time_shift):
        dict_channel_list = dict()
        dict_channel_time = dict()
        id_tab_dict = dict()
        id_tab_dict[1] = [101, 111, 112, 132,
                          152, 153, 154, 155,
                          156, 157, 158]
        num_channel_tab_list = [25, 18, 15, 17,
                                47, 22, 14, 19]
        for i, num_channel_tab in enumerate(num_channel_tab_list):
            id_tab_dict[i + 2] = [100 + i for i in range(1, num_channel_tab + 1)]

        idx_start = IDX_LG[0]
        idx_end = IDX_LG[1]
        try:
            assert idx_start == 1 and idx_end == 10
        except:
            self.logger.critical("idx should be 1, 10 not {}, {}".format(str(idx_start), str(idx_end)))

        for tab in range(idx_start, idx_end):  # should be 1, 10
            for id_channel in id_tab_dict[tab]:
                self.driver.reset_driver()
                try:
                    t_start = time.time()
                    num_channel, name_channel, dict_time = self.parse_channel(tab=tab, id_channel=id_channel,
                                                                              time_shift=time_shift)
                    t_process = time.time() - t_start
                    dict_channel_list[num_channel] = name_channel
                    dict_channel_time[num_channel] = dict_time
                    self.logger.warning("\tcrawled [{:>3}/{:2}] ({:3.2f}s) [{}]".format(str(num_channel),
                                                                                        len(dict_time),
                                                                                        t_process,
                                                                                        name_channel))
                except NoSuchElementException:
                    continue
                except:
                    id_channel += 1
                    error = "error in parse_chanel {}/{}".format(str(tab), str(id_channel))
                    self.logger.error(error, exc_info=True)
                    continue

        self.driver.quit_driver()
        return dict_channel_list, dict_channel_time


class ParserSKT(Parser):
    dict_channel_list = dict()
    dict_channel_time = dict()
    remain_channel = list()

    def __init__(self):
        skt_url = "http://www.skbroadband.com/content/realtime/Realtime_List.do"
        Parser.__init__(self, target_url=skt_url, device='SKT')
        self.NUM_CHANNEL = 226
        self.driver.set_counter(MAX_COUNT=1)
        self.logger.info("initialize driver done")

    def get_target_channel_time(self, count, time_shift):
        path_time = '//*[@id="board2"]/div[4]/table/tbody/tr[{}]/th'.format(str(count))
        path_name = '// *[ @ id = "board2"] / div[4] / table / tbody / tr[{}] / td[1]'.format(str(count))
        times = self.driver.get_text(path=path_time).split(':')
        name_program = self.driver.get_text(path=path_name)

        dt_program = self.make_date(hour=int(times[0]), minute=int(times[1]), time_shift=time_shift)
        name_program = self.convert_englist(program_name=name_program)
        return dt_program, name_program

    def get_channel_time(self, time_shift):
        dict_channel_time = dict()
        count = 1
        if time_shift == 0:
            while True:
                try:
                    dt_program, name_program = self.get_target_channel_time(count, time_shift=time_shift)
                    dict_channel_time[dt_program] = name_program
                    count += 1
                except NoSuchElementException:
                    # If found any NSE error, stop looking down and return the current time dictionary
                    break
        else:
            start = False
            while True:
                try:
                    dt_program, name_program = self.get_target_channel_time(count, time_shift=time_shift)
                    dict_channel_time[dt_program] = name_program
                    count += 1
                    start = True
                except NoSuchElementException:
                    # If found any NSE error, stop looking down and return the current time dictionary
                    if start:
                        break
                    else:
                        count += 1
                        continue

        if not bool(dict_channel_time):
            dt_program = self.make_date(hour=0, minute=0)
            name_program = "information is not available"
            dict_channel_time[dt_program] = name_program
        return dict_channel_time

    def parse_channel(self, tab, id_channel, time_shift):
        tab_path = '//*[@id="li-C020{}0000"]/span/a'.format(str(tab))
        try:
            self.driver.click_btn(path=tab_path)
            time.sleep(1)
        except:
            error = "error in click_btn tab {}".format(str(tab))
            self.logger.error(error, exc_info=True)
            raise

        channel_path = '//*[@id="RealtimeModel"]/ul/li[{}]/a'.format(str(id_channel))
        self.driver.click_btn(path=channel_path)
        time.sleep(1)
        list_path = '//*[@id="RealtimeModel"]/div[3]/ul/li[2]/a'
        self.driver.click_btn(path=list_path)
        time.sleep(1)
        if time_shift > 0:
            next_path = '//*[@id="board2"]/div[2]/div/ul/li[2]/a'
            self.driver.click_btn(path=next_path)
            time.sleep(1)
            self.logger.info("move to next day")

        num_path = '//*[@id="RealtimeModel"]/div[2]/ul/li[1]'
        num_channel = self.driver.get_text(path=num_path)
        start_index = num_channel.find('[')
        end_index = num_channel.find(']')
        num_channel = num_channel[start_index + 1:end_index]

        name_channel = self.driver.get_text(path=channel_path)
        dict_time = self.get_channel_time(time_shift=time_shift)
        return num_channel, name_channel, dict_time

    @classmethod
    def async_parse_channel(cls, tab, id_channel, time_shift, dict_channel_list, dict_channel_time,
                            list_remain_channel):
        num_channel = -1
        name_channel = ""
        flag_done = False
        dict_time = dict()
        t_start = time.time()

        parser = ParserSKT()
        print("start crawling {} - {}", tab, id_channel)
        try:
            t_start = time.time()
            num_channel, name_channel, dict_time = parser.parse_channel(tab, id_channel, time_shift)
            flag_done = True
            t_process = time.time() - t_start
            parser.logger.critical("\tcrawled [{:>3}/{:2}] ({:5.2f}s) [{}]".format(str(num_channel),
                                                                                  len(dict_time),
                                                                                  t_process,
                                                                                  name_channel))

        except NoSuchElementException:
            t_process = time.time() - t_start
            parser.logger.warning("\tcrawled [{:>5}] ({:5.2f}s) [{}/{}]".format("Fail", t_process, tab, id_channel))

        except:
            t_process = time.time() - t_start
            parser.logger.warning("\tcrawled [{:>5}] ({:5.2f}s) [{}/{}]".format("Fail", t_process, tab, id_channel))
            error = "error in parse_chanel {}/{}".format(str(tab), str(id_channel))
            parser.logger.error(error, exc_info=True)

        finally:
            parser.driver.quit_driver()
            output_dict = {"num_channel": num_channel,
                           "name_channel": name_channel,
                           "dict_time": dict_time,
                           "channel": (tab, id_channel),
                           "flag_done": flag_done}
            return output_dict, dict_channel_list, dict_channel_time, list_remain_channel

    @classmethod
    def async_parse_channel_callback(cls, arg):
        logger = logging.getLogger(__name__)
        x = arg[0]
        dict_channel_list = arg[1]
        dict_channel_time = arg[2]
        list_remain_channel = arg[3]
        if type(x) is dict:
            if x['flag_done']:

                num_channel = x['num_channel']
                name_channel = x['name_channel']
                dict_time = x['dict_time']
                channel = x['channel']

                logger.info("\tstart callback of ", channel)
                try:
                    logger.info("\tbefore", channel, dict_channel_list, list_remain_channel)
                    dict_channel_list[num_channel] = name_channel
                    dict_channel_time[num_channel] = dict_time
                    if channel in list_remain_channel:
                        list_remain_channel.remove(channel)
                    logger.info("\tafter", channel, dict_channel_list, list_remain_channel)
                    logger.info("\tend callback of ", channel)

                except:
                    error = "Error occured during callback"
                    logger.error(error, exc_info=True)

    def wait(self, sleep=120):
        for _ in tqdm(range(sleep), total=sleep, unit='sec'):
            time.sleep(1)

    def get_channel_list(self, time_shift):
        """Top-level crawling function which crawl list of channel with their time-table.

        Args:
            (int) time_shift : crawl today if 0 and crawl tomorrow if 1

        Returns:
            (dict) dict_channel_list : key-number of channel, item-name of broadcaster
            (dict) dict_channel_time : key-number of channel, item-dictionary of time table
        """

        id_tab_dict = dict()
        num_channel_tab_list = [7, 4, 10, 7, 16,
                                10, 18, 13, 11, 11,
                                21, 6, 16, 4, 20,
                                10, 24, 16, 2]

        for i, num_channel_tab in enumerate(num_channel_tab_list):
            id_tab_dict[i + 2] = [i for i in range(1, num_channel_tab + 1)]

        idx_start = 13#IDX_SKT[0] # must be >= 2
        idx_end = IDX_SKT[1]
        try:
            assert idx_start == 2 and idx_end == 20
        except:
            self.logger.critical("idx should be 2, 20 not {}, {}".format(str(idx_start), str(idx_end)))

        crawling_pool = Pool(processes=self.cpu_count)
        crawled_res = list()
        abortable_func = partial(Parser.abortable_worker, ParserSKT.async_parse_channel, timeout=20)

        manager = Manager()
        dict_channel_list = manager.dict()
        dict_channel_time = manager.dict()
        list_remain_channel = manager.list()

        # initialize all target channel key value (tab, id_channel)
        for tab in range(idx_start, idx_end):
            for id_channel in id_tab_dict[tab]:
                list_remain_channel.append((tab, id_channel))
        num_goal_channel = len(list_remain_channel)

        # repeat crawling until remaining target channel is zero.
        iteration = 0
        count = 0
        while len(list_remain_channel) > 0:
            t_start = time.time()
            num_channel = len(list_remain_channel)
            for channel in list_remain_channel:


                # decentralize network-load with waiting 2 seconds.
                count += 1
                if count > 20:
                    self.wait(sleep=60)
                    count = 0
                time.sleep(5)
                tab = channel[0]
                id_channel = channel[1]

                # start crawling single channel asynchronously with multiprocessing object
                res = crawling_pool.apply_async(abortable_func,
                                                (tab, id_channel,
                                                 time_shift,
                                                 dict_channel_list,
                                                 dict_channel_time,
                                                 list_remain_channel),
                                                 callback=ParserSKT.async_parse_channel_callback)
                crawled_res.append(res)

            # wait until all crawling job is done
            for r in crawled_res:
                r.wait()

            # report with last iteration
            t_consumed = time.time() - t_start
            num_done_channel = num_channel-len(list_remain_channel)
            report = "\tIter [{:>2}] [{:>3}/{:3}]| Finish ({:>2})ch Took ({:4.2f}s) | Avg ({:3.2f}s/ch)"\
                     .format(iteration, num_goal_channel-len(list_remain_channel),
                     num_goal_channel, num_done_channel,
                     t_consumed, t_consumed/num_done_channel)
            self.logger.critical(report)
            iteration += 1

        # release pool process
        crawling_pool.close()
        crawling_pool.join()
        crawling_pool.terminate()


def initialize_variable(debug=False):
    logger = logging.getLogger(__name__)
    if debug:
        logger.warning("//======== DEBUG MODE ========//")
        global IDX_KT
        global IDX_LG
        global IDX_SKT
        IDX_KT = (1, 2, 1, 6)
        IDX_LG = (8, 9)
        IDX_SKT = (2, 3)
        logger.warning("//======== VARIABLE INITIALIZATION DONE ========//")


def update_channel_data():
    # kt_parser = ParserKT()
    # kt_parser.update_channel_data()

    # lg_parser = ParserLG()
    # lg_parser.update_channel_data()
    #
    skt_parser = ParserSKT()
    skt_parser.update_channel_data()


if __name__ == "__main__":
    """
    print("start parsing inside code")
    setup_logging()
    print("finish setup logging")
    initialize_variable(debug=False)
    print("finish variable init")
    update_channel_data()
    print("end parsing inside code")
    """

    skt = ParserSKT()
    skt.get_channel_list(0)
