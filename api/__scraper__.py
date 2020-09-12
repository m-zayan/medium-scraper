from typing import Union

from selenium import webdriver

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from parser.utils import Logger, OS, Reader, Writer, Requests
from errors.exceptions import WebDriverException, ScraperException, TimeoutException

__all__ = ['MediumScraper']

initialization_error_msg = 'Initialization Failed::'


class MediumScraper:

    name = 'medium-scraper'

    os_types = ['linux', 'windows']
    browsers = ['chrome', 'firefox']

    main_urls = {'root': {'class': None, 'url': 'https://medium.com./'},
                 'topics': {'class': 'js-sourceStream', 'url': 'https://medium.com./topics'}}

    def __init__(self, os_type: str, browser: str = 'chrome', topics: Union[str, list] = None,
                 scroll_step: Union[int, list] = 1, time_to_wait: float = 30.0,
                 reload_page_count: int = 1, cfg_filename: str = None, **kwargs):
        """
        Parameters
        ----------
        os_type: str
            'linux' or 'windows'

        browser:
            'chrome' or 'firefox',  default: browser = 'chrome'

        topics: Union[str, list]

            str: 'all' get all topics, topics names, separated by comma - ',', or list of topics names

        scroll_step: Union[int, list]

              int: scroll to - scrollHeight * scroll_step
              list: for each topic (i), scroll to - scrollHeight * scroll_step[i]

        time_to_wait: float

            driver.get(url=...), timeout

        reload_page_count: int

            if timeout --> reload

        cfg_filename: str

            *.json,  path, which could used to specify scraping settings, ex: to_path/config.json

        kwargs:
            extra parameters,  settings or the key of *.json file, {cfg_filename}
        """

        self.os_type = os_type

        self.__os_process__ = OS(os_type=self.os_type)

        self.browser = browser.lower()

        self.topics = topics

        self.scroll_step = scroll_step

        self.time_to_wait = time_to_wait
        self.reload_page_count = reload_page_count

        self.cfg_filename = cfg_filename

        self.kwargs = kwargs

        self.driver_path: str
        self.driver: webdriver.Remote

        self.topics_urls: list
        self.start_urls: dict

        self.options: Union[ChromeOptions, FirefoxOptions]

        self.scroll_height = None

    def init_model(self, set_quit=True):

        try:

            self.__init__model__()

        except (WebDriverException, ScraperException) as error:

            # Log error
            Logger.error(error)

            if set_quit:

                self.quit()

        else:

            if set_quit:

                self.quit()

    def run(self, set_quit=True):

        try:

            self.__get_posts_metadata__()

        except (WebDriverException, ScraperException) as error:

            # Log error
            Logger.error(error)

            if set_quit:

                self.quit()

        else:

            if set_quit:

                self.quit()

    def export_posts_urls_json(self, filename='posts_urls.json', overwrite=False, indent_level=3, sort_keys=False):

        if self.start_urls is not None:

            Writer.dict_to_json(json_filename=filename, content=self.start_urls,
                                overwrite=overwrite,  indent_level=indent_level, sort_keys=sort_keys)

        else:

            error_log = {'error_type': 'ValueError', 'message': 'Not urls to export'}

            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error('Export failed, Check log file')

    def export_posts_urls_csv(self, filename='posts_urls.csv', overwrite=False):

        keys = list(self.start_urls.keys())

        metadata = {key: [] for key in self.start_urls[keys[0]].keys()}
        metadata.setdefault('topic', [])

        for topic in self.start_urls.keys():

            topic_name = [topic] * len(self.start_urls[topic]['url'])

            metadata['topic'] += topic_name

            for key in self.start_urls[topic].keys():

                values = self.start_urls[topic][key]
                metadata[key] += values

        Writer.dict_to_csv(csv_filename=filename, content=metadata, overwrite=overwrite, use_pandas=True)

    def start_requests(self):

        if self.start_urls is None:

            error_log = {'error_type': 'ValueError', 'message': 'Not urls to iterate through'}
            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error(initialization_error_msg)

            return None

        for _ in self.start_urls.keys():
            pass

    def get(self, url):

        self.driver.set_page_load_timeout(time_to_wait=self.time_to_wait)

        if 'script_timeout' in self.kwargs.keys():

            self.driver.set_script_timeout(time_to_wait=self.kwargs['script_timeout'])

        else:

            self.driver.set_script_timeout(0.001)

        for i in range(self.reload_page_count):

            try:

                self.driver.get(url=url)

                break

            except TimeoutException as error:

                Logger.fail(str(i+1) + ': timeout::page has been reloaded')
                Logger.set_line(length=60)

                if i == self.reload_page_count - 1:

                    Logger.warning(error)

        self.scroll_height = self.driver.execute_script("return document.body.scrollHeight")

    def scroll_down(self, callback, delay=0.5, limit: int = -1, **meta):

        while True:

            # scroll to - document.body.scrollHeight
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            Requests.sleep(delay)

            cur_height = self.driver.execute_script("return document.body.scrollHeight")

            if cur_height > limit:
                break

        outputs = callback(**meta)

        return outputs

    def quit(self):

        self.driver.quit()

    def close(self):

        self.driver.close()

    def get_posts_count(self):

        count = 0

        for key in self.start_urls.keys():

            count += len(self.start_urls[key]['url'])

        return count

    def __init_web_driver__(self):

        self.__init_driver_options__()

        if self.browser == 'chrome':

            self.driver_path = self.__os_process__.locate_file(pattern='/chromedriver$', params='-i --regexp')[0]

            if self.driver_path is None:

                Logger.error(initialization_error_msg + 'Can\'t Find Chrome Driver Executable File')

            self.driver = webdriver.Chrome(options=self.options, executable_path=self.driver_path)

        elif self.browser == 'firefox':

            self.driver_path = self.__os_process__.locate_file(pattern='/geckodriver$', params='-i --regexp')[0]

            if self.driver_path is None:

                Logger.error(initialization_error_msg + 'Can\'t Find Firefox Driver Executable File')

            self.driver = webdriver.Firefox(options=self.options, executable_path=self.driver_path)

        else:  # Log Error
            pass

    def __init_driver_options__(self):

        if self.cfg_filename is not None:

            self.__set_config__()

        if self.browser == 'chrome':

            self.options = ChromeOptions()

        elif self.browser == 'firefox':

            self.options = FirefoxOptions()

        else:  # Log Error
            pass

    def __set_config__(self):

        self.kwargs = Reader.json_to_dict(self.cfg_filename)

        # ....., parsing, set options

    def __init__model__(self):

        self.__init_web_driver__()

        if self.driver is None:  # Log Error
            pass

        self.__init__urls__()

    def __init__urls__(self):

        if self.topics is not None:

            if not isinstance(self.topics, list) and self.topics != 'all':

                self.topics: str

                self.topics = self.topics.split(',')
                self.topics = list(map(lambda _str: _str.strip(), self.topics))

            if self.topics != 'all':

                self.topics = list(map(lambda name: name.lower(), self.topics))

                # Log Info
                Logger.info('Topics : ' + ', '.join(self.topics))

            info = MediumScraper.main_urls['topics']

            self.get(info['url'])

            self.__get_topics_urls__()

        else:

            info = MediumScraper.main_urls['root']

            self.get(info['url'])

            self.__get_taps_urls__()

    def __get_topics_urls__(self):

        topic_xpath = '//section/div/div/div/a'

        elements = self.driver.find_elements_by_xpath(xpath=topic_xpath)

        self.topics_urls = list()
        self.start_urls = dict()

        for element in elements:

            href = element.get_attribute('href')
            self.topics_urls.append(href)

    def __get_posts_metadata__(self):

        if len(self.topics_urls) > 0:

            def get_urls(topic_url):

                name = topic_url.split('/')[-1]

                if (isinstance(self.topics, list) and name in self.topics) \
                        or self.topics == 'all':

                    self.start_urls[name] = self.__get_metadata__(url=topic_url)

            for url in self.topics_urls:

                get_urls(url)

        else:

            pass

    def __get_metadata__(self, url):

        self.get(url)

        article_xpath = '//section/div/section/div/div/div/h3/a'
        datetime_xpath = '//section/div/section' + '/div' * 7

        def get_metadata():

            elements_url = self.driver.find_elements_by_xpath(xpath=article_xpath)
            elements_date = self.driver.find_elements_by_xpath(xpath=datetime_xpath)

            titles = list(map(lambda node: node.text, elements_url))
            _urls = list(map(lambda node: node.get_attribute('href'), elements_url))
            date = list(map(lambda node: node.text.split('\n')[0], elements_date))
            read_time = list(map(lambda node: node.text.split('\n')[-1], elements_date))

            _metadata = {'title': titles,
                         'url': _urls,
                         'date': date,
                         'read_time': read_time}

            return _metadata

        metadata = self.scroll_down(callback=get_metadata,
                                    delay=0.5,
                                    limit=self.scroll_height * self.scroll_step)

        return metadata

    def __get_taps_urls__(self):
        pass

    @staticmethod
    def __exec_ignore__(func):

        def inner(*args, **kwargs):

            try:

                func(*args, **kwargs)

            except (WebDriverException, ScraperException):
                pass

        return inner
