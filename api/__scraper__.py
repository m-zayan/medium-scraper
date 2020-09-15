from typing import Union, List

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from parser.utils import Logger, OS, Reader, Writer, Requests
from errors.exceptions import WebDriverException, ScraperException, TimeoutException

__all__ = ['MediumScraper']

initialization_error_msg = 'Initialization Failed::'
limited_access_indicator = ['You\'ve read all of your free stories this month.', 'To keep reading this story']
post_image_indicator = 'Image for post'


class MediumScraper:

    name = 'medium-scraper'

    os_types = ['linux', 'windows']
    browsers = ['chrome', 'firefox']

    main_urls = {'root': {'class': None, 'url': 'https://medium.com./'},
                 'topics': {'class': None, 'url': 'https://medium.com./topics'}}

    def __init__(self, os_type: str, updatedb: bool = False, browser: str = 'chrome', topics: Union[str, list] = None,
                 scroll_step: Union[int, list] = 1, time_to_wait: float = 30.0,
                 reload_page_count: int = 1, ignore_limited_access=True, cfg_filename: str = None, **kwargs):
        """
        Parameters
        ----------
        os_type: str
            'linux' or 'windows'

        updatedb: str
            set updatedb=true, if the driver recently installed, or initialization has been failed
                default, updatedb=False

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
        self.__updatedb__ = updatedb
        self.__os_process__ = OS(os_type=self.os_type)

        self.browser = browser.lower()

        self.topics = topics

        self.scroll_step = scroll_step

        self.time_to_wait = time_to_wait
        self.reload_page_count = reload_page_count

        self.ignore_limited_access = ignore_limited_access

        self.cfg_filename = cfg_filename

        self.kwargs = kwargs

        self.driver_path: str
        self.driver: webdriver.Remote

        self.topics_urls: list
        self.metadata: dict

        self.posts_content: dict

        self.options: Union[ChromeOptions, FirefoxOptions]

        self.scroll_height = None

    def init_model(self, set_quit=True):

        try:

            self.__init__model__()

            Logger.info('No. of topics :', str(len(self.topics_urls)))
            Logger.set_line(length=50)

        except (WebDriverException, ScraperException) as error:

            # Log error
            Logger.error(error)

            if set_quit:

                self.quit()

        else:

            if set_quit:

                self.quit()

    def run(self, scrape_content=False, export_metadata_json=True, export_metadata_csv=True,
            export_data_json=True, export_data_csv=True, export_overwrite=True, set_quit=True):

        try:

            self.__get_posts_metadata__()

            Logger.info('No. of posts :', str(self.get_posts_count()))

            if export_metadata_json:

                self.export_metadata_json(filename='posts_metadata.json', overwrite=export_overwrite, indent_level=3,
                                          sort_keys=False)

            if export_metadata_csv:

                self.export_metadata_csv(filename='posts_metadata.csv',
                                         overwrite=export_overwrite)

            if scrape_content:

                self.__get_data__()

            if export_data_json:

                self.export_data_json(filename='posts_content.json', overwrite=export_overwrite, indent_level=3,
                                      sort_keys=False)

            if export_data_csv:

                self.export_data_csv(filename='posts_content.csv', overwrite=export_overwrite)

        except (WebDriverException, ScraperException) as error:

            # Log error
            Logger.error(error)

            if set_quit:

                self.quit()

        else:

            if set_quit:

                self.quit()

    def scrape_content_from_file(self, metadata_filename='posts_metadata.json',
                                 export_json=True, export_csv=True,
                                 export_overwrite=True, timeout_export=False, set_quit=True):

        try:

            _metadata = Reader.json_to_dict(metadata_filename)

            setattr(self, 'metadata', _metadata)

            if not hasattr(self, 'posts_content'):

                setattr(self, 'posts_content', dict())

            n_post = self.get_posts_count()

            Logger.info('No. of posts :', str(n_post))

            if n_post > 0:

                setattr(self, 'timeout_export', timeout_export)

                self.__get_data__()

            if export_json:

                setattr(self, 'export_json', export_json)

                self.export_data_json(filename='posts_content.json', overwrite=export_overwrite, indent_level=3,
                                      sort_keys=False)

            if export_csv:

                setattr(self, 'export_csv', export_csv)

                self.export_data_csv(filename='posts_content.csv', overwrite=export_overwrite)

        except (WebDriverException, ScraperException) as error:

            # Log error
            Logger.error(error)

            if set_quit:

                self.quit()

        else:

            if set_quit:

                self.quit()

    def export_metadata_json(self, filename='posts_urls.json', overwrite=False, indent_level=3, sort_keys=False):

        if self.metadata is not None:

            Writer.dict_to_json(json_filename=filename, content=self.metadata,
                                overwrite=overwrite,  indent_level=indent_level, sort_keys=sort_keys)

        else:

            error_log = {'error_type': 'ValueError', 'message': 'No urls to export'}

            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error('Export failed, Check log file')

    def export_metadata_csv(self, filename='posts_urls.csv', overwrite=False):

        if self.metadata is not None:

            keys = list(self.metadata.keys())

            metadata = {key: [] for key in self.metadata[keys[0]].keys()}
            metadata.setdefault('topic', [])

            for topic in self.metadata.keys():

                topic_name = [topic] * len(self.metadata[topic]['url'])

                metadata['topic'] += topic_name

                for key in self.metadata[topic].keys():

                    values = self.metadata[topic][key]
                    metadata[key] += values

            Writer.dict_to_csv(csv_filename=filename, content=metadata, overwrite=overwrite, use_pandas=True)

        else:

            error_log = {'error_type': 'ValueError', 'message': 'No urls to export'}

            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error('Export failed, Check log file')

    def export_data_json(self, filename='posts_content.json', overwrite=False, indent_level=3, sort_keys=False):

        if self.posts_content is not None:

            Writer.dict_to_json(json_filename=filename, content=self.posts_content,
                                overwrite=overwrite,  indent_level=indent_level, sort_keys=sort_keys)

        else:

            error_log = {'error_type': 'ValueError', 'message': 'No data to export'}

            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error('Export failed, Check log file')

    def export_data_csv(self, filename='posts_content.csv', overwrite=False):

        if self.posts_content is not None:

            Writer.dict_to_csv(csv_filename=filename, content=self.posts_content, overwrite=overwrite, use_pandas=True)

        else:

            error_log = {'error_type': 'ValueError', 'message': 'No data to export'}

            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error('Export failed, Check log file')

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

                if i < self.reload_page_count - 1:

                    Logger.fail(str(i+1) + ': timeout::page has been reloaded')
                    Logger.set_line(length=60)

                else:

                    Logger.fail(str(i + 1) + ': timeout::page reload Limit has been exceed\n'
                                             '\tdo you want to try again - [y/n]: ', end='')
                    ok = input()

                    Logger.set_line(length=60)

                    if ok.lower() == 'y':

                        self.time_to_wait = float(input('time to wait :'))
                        self.reload_page_count = int(input('reload count :'))

                        self.get(url)

                    elif ok.lower() == 'n':

                        self.___timeout_export__()
                        Logger.error(error)

                    else:

                        self.___timeout_export__()

                        Logger.fail('Abort')
                        Logger.error(error)

        self.scroll_height = self.driver.execute_script("return document.body.scrollHeight")

    def scroll_down(self, callback, delay=0.5, limit: int = -1, **meta):

        for i in range(limit):

            # scroll to - document.body.scrollHeight
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            Logger.info_r(f'steps : {i+1}/{limit}')

            Requests.sleep(delay)

        Logger.info('', end='\n')
        Logger.set_line(length=50)

        outputs = callback(**meta)

        return outputs

    def find_elements_by_xpath(self, xpath, raise_error=True):

        try:

            return self.driver.find_elements_by_xpath(xpath)

        except WebDriverException as error:

            if raise_error:

                raise error

            else:
                return []

    def find_element_by_xpath(self, xpath, raise_error=True):

        try:

            return self.driver.find_element_by_xpath(xpath)

        except WebDriverException as error:

            if raise_error:

                raise error

            else:

                return None

    @staticmethod
    def node_find_element_by_xpath(node, xpath, raise_error=True):

        if node is None:

            return None

        try:

            return node.find_element_by_xpath(xpath)

        except WebDriverException as error:

            if raise_error:

                raise error

            else:

                return None

    @staticmethod
    def node_find_elements_by_xpath(node, xpath, raise_error=True):

        if node is None:

            return []

        try:

            return node.find_elements_by_xpath(xpath)

        except WebDriverException as error:

            if raise_error:

                raise error

            else:

                return None

    @staticmethod
    def safe_get_attribute(element, attr_name, default):

        return getattr(element, attr_name, default)

    def quit(self):

        self.driver.quit()

    def close(self):

        self.driver.close()

    def get_post_content(self, url):

        if not hasattr(self, 'posts_content'):

            setattr(self, 'posts_content', dict())

        self.__get_post_content__(url)

    def get_posts_count(self):

        count = 0

        for key in self.metadata.keys():

            count += len(self.metadata[key]['url'])

        return count

    def ___timeout_export__(self):

        if hasattr(self, 'timeout_export') and self.timeout_export:

            if hasattr(self, 'export_json') and self.export_json:

                self.export_data_json(filename='timeout_export_content.json', overwrite=True,
                                      indent_level=3,
                                      sort_keys=False)

            if hasattr(self, 'export_csv') and self.export_csv:

                self.export_data_csv(filename='timeout_export_content.csv', overwrite=True)

    def __init_web_driver__(self):

        self.__init_driver_options__()

        if self.browser == 'chrome':

            self.driver_path = self.__os_process__.locate_file(pattern='/chromedriver$', params='-i --regexp',
                                                               updatedb=self.__updatedb__)[0]

            if self.driver_path is None:

                Logger.error(initialization_error_msg + 'Can\'t Find Chrome Driver Executable File')

            self.driver = webdriver.Chrome(options=self.options, executable_path=self.driver_path)

        elif self.browser == 'firefox':

            self.driver_path = self.__os_process__.locate_file(pattern='/geckodriver$', params='-i --regexp',
                                                               updatedb=self.__updatedb__)[0]

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

        elements = self.find_elements_by_xpath(xpath=topic_xpath)

        self.topics_urls = list()
        self.metadata = dict()

        for element in elements:

            href = element.get_attribute('href')
            self.topics_urls.append(href)

    def __get_posts_metadata__(self):

        if len(self.topics_urls) > 0:

            def get_urls(topic_url):

                name = topic_url.split('/')[-1]

                if (isinstance(self.topics, list) and name in self.topics) \
                        or self.topics == 'all':

                    self.metadata[name] = self.__get_metadata__(url=topic_url)

            for url in self.topics_urls:

                get_urls(url)

        else:

            pass

    def __get_metadata__(self, url):

        self.get(url)

        article_xpath = '//section/div/section/div/div/div/h3/a'
        subtitle_xpath = '//section/div/section' + '/div' * 4 + '/h3'
        pub_xpath = '//section/div/section' + '/div' * 5 + '[@class="n"]'
        datetime_xpath = '//section/div/section' + '/div' * 7

        def get_pub(elements_pub: List[WebElement]):

            author, publication = [], []

            for pub in elements_pub:

                children = pub.find_elements_by_xpath('child::*')

                if len(children) == 2:

                    author.append(children[0].text)
                    publication.append(children[1].text)

                else:

                    author.append(children[0].text)
                    publication.append(None)

            return author, publication

        def get_metadata():

            elements_url = self.find_elements_by_xpath(xpath=article_xpath)
            elements_subtitle = self.find_elements_by_xpath(xpath=subtitle_xpath)
            elements_pub = self.find_elements_by_xpath(xpath=pub_xpath)
            elements_date = self.find_elements_by_xpath(xpath=datetime_xpath)

            title = list(map(lambda node: node.text, elements_url))
            subtitle = list(map(lambda node: node.text, elements_subtitle))
            _urls = list(map(lambda node: node.get_attribute('href'), elements_url))

            author, publication = get_pub(elements_pub)

            date = list(map(lambda node: node.text.split('\n')[0], elements_date))
            read_time = list(map(lambda node: node.text.split('\n')[-1], elements_date))

            _metadata = {'title': title,
                         'subtitle': subtitle,
                         'publication': publication,
                         'url': _urls,
                         'author': author,
                         'date': date,
                         'read_time': read_time}

            return _metadata

        metadata = self.scroll_down(callback=get_metadata,
                                    delay=0.5,
                                    limit=self.scroll_step)

        return metadata

    def __get_data__(self):

        if self.metadata is None:

            error_log = {'error_type': 'ValueError', 'message': 'Not urls to iterate through'}
            Logger.write_messages_json(error_log)

            # Log Error
            Logger.error(initialization_error_msg)

            return None

        self.posts_content = dict()

        for topic, metadata in self.metadata.items():

            n_post = len(metadata['url'])

            Logger.info(f'Begin Scraping : {topic}')

            for i in range(n_post):

                Logger.info_r(f'scraped content : {i + 1}/{n_post}')

                self.__get_post_content__(url=metadata['url'][i])

            Logger.info(f'End Scraping : {topic}')
            Logger.set_line(length=50)

    def __get_post_content__(self, url):

        self.get(url)

        text_xpath = '//article/div/section/div/div/p'
        figure_xpath = '//article/div/section/div/div/figure'

        def section_reformat(text):
            return '[' + text + ']'

        def child_reformat(text):

            return '<' + text + '>'

        def get_figure(elements_figure: List[WebElement]):

            img_src, img_caption = [], []

            for element in elements_figure:

                children = element.find_elements_by_xpath('child::*')
                img_node = self.node_find_element_by_xpath(node=children[0], xpath='.//img', raise_error=False)

                if img_node is None or\
                        img_node.get_attribute('alt') != post_image_indicator:

                    continue

                elif len(children) == 2:

                    src = img_node.get_attribute('src')
                    caption = get_caption(children[1])

                    img_src.append(src)
                    img_caption.append(caption)

                else:

                    src = img_node.get_attribute('src')

                    img_src.append(src)
                    img_caption.append(None)

            return img_src, img_caption

        def get_caption(node: WebElement):

            caption = ''

            children = node.find_elements_by_xpath('child::*')

            for child in children:

                txt = MediumScraper.safe_get_attribute(child, 'text', '')
                caption += child_reformat(txt)

            return caption

        def get_text(p_nodes: List[WebElement]):

            text = ''

            for node in p_nodes:

                txt = MediumScraper.safe_get_attribute(node, 'text', '')
                text += section_reformat(txt)

                children = node.find_elements_by_xpath('child::*')

                for child in children:

                    txt = MediumScraper.safe_get_attribute(child, 'text', '')

                    if len(txt) > 3:

                        text += child_reformat(txt)

                    else:

                        text += txt

            return text

        def check_limited_access():

            ok = self.find_element_by_xpath(f"//*[contains(text(), '{limited_access_indicator[0]}')]",
                                            raise_error=False)

            if ok is None:

                ok = self.find_element_by_xpath(f"//*[contains(text(), '{limited_access_indicator[1]}')]",
                                                raise_error=False)

            if ok is None:

                return False

            return True

        def get_post_content():

            ok = check_limited_access()

            if ok is True and \
                    self.ignore_limited_access is False:

                Logger.warning('You have a limited access :' + url)

                invalid = input('\tDo you want to continue - [y/n]: ')

                if invalid.lower() == 'n':

                    return

                elif invalid.lower() != 'y':

                    Logger.fail('Abort')

                    return

            elif ok is True and self.ignore_limited_access:

                Logger.warning('You have a limited access :' + url)

            elements_text = self.find_elements_by_xpath(xpath=text_xpath, raise_error=False)
            elements_figure = self.find_elements_by_xpath(xpath=figure_xpath, raise_error=False)

            text = get_text(elements_text)

            img_src, img_caption = get_figure(elements_figure)

            keys = list(self.posts_content.keys())

            if len(keys) == 0:

                self.posts_content = {'url': [],
                                      'text':  [],
                                      'img_src': [],
                                      'caption': []}

            self.posts_content['url'].append(url)
            self.posts_content['text'].append(text)
            self.posts_content['img_src'].append(img_src)
            self.posts_content['caption'].append(img_caption)

        get_post_content()

    def __get_taps_urls__(self):
        pass
