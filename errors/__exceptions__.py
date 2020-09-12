from socket import error
from selenium.common.exceptions import WebDriverException, TimeoutException


__all__ = ['ScraperException', 'WebDriverException', 'TimeoutException',
           'SocketError', 'InvalidConfigurations']


class ScraperException(Exception):

    def __init__(self, message):

        super().__init__(message)


class InvalidConfigurations(ScraperException):

    def __init__(self, message):

        super().__init__(message)


class SocketError(error):

    def __init__(self, *args, **kwargs):
        pass
