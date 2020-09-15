from typing import Union

import sys
import os
import subprocess as process
from pathlib import Path

import json
import csv

import pandas as pd

import time
from datetime import datetime

import traceback

from errors.exceptions import InvalidConfigurations

__all__ = ['Logger', 'OS', 'Reader', 'Requests', 'Writer']

OS_TYPE = ['linux', 'windows']

OS_ROOT_DIR = str(Path.home()) + '/../../'


class Logger:

    @staticmethod
    def write_messages_json(content, log_file='logs.json', indent_level=3, sort_keys=False, separators=(',', ':')):

        json_record = dict()

        json_record['update_time'] = datetime.now().strftime("%I.%M:%S %p")
        json_record[json_record['update_time']] = content

        if OS.file_exists(log_file):

            Writer.dict_to_json(json_filename=log_file, content=json_record, overwrite=True,
                                indent_level=indent_level, separators=separators, sort_keys=sort_keys)

        else:

            Writer.dict_to_json(json_filename=log_file, content=json_record, overwrite=False,
                                indent_level=indent_level, separators=separators, sort_keys=sort_keys)

    @staticmethod
    def info(message, *args, end='\n'):

        print(Formatter.GREEN + message + ' ' + ' '.join(args) + Formatter.END, end=end)

    @staticmethod
    def info_r(message, *args):

        sys.stdout.write('\r ' + Formatter.GREEN + message + ' ' + ' '.join(args) + Formatter.END)
        sys.stdout.flush()

    @staticmethod
    def fail(message, *args, end='\n'):

        print(Formatter.FAIL + message + ' ' + ' '.join(args) + Formatter.END, end=end)

    @staticmethod
    def error(err, end='\n'):

        err_traceback = traceback.format_exc()

        Logger.fail(str(err))
        Logger.fail(str(err_traceback), end=end)

    @staticmethod
    def warning(message, end='\n'):

        print(Formatter.WARNING + message + Formatter.END, end=end)

    @staticmethod
    def set_line(length: int = 100):

        Logger.info(Formatter.BLUE + '=' * length + Formatter.END)


class OS:

    def __init__(self, os_type='linux'):

        self.os_type = os_type

    @staticmethod
    def file_exists(path):

        return Path(path).is_file()

    def locate_file(self, pattern, params: str = '', updatedb=False):

        if updatedb:

            self.run_commands('nice -n 19 ionice -c 3 updatedb')

        file_dirs = self.run_commands(f'locate {params} {pattern}', multi_outputs=True, multi_output_sep='\n')

        if len(file_dirs) > 1:

            file_dirs.pop()

        return file_dirs

    def run_commands(self, command, multi_outputs=True, multi_output_sep='\n'):

        output: Union[bytes, str, list]

        try:

            if self.os_type == 'linux':

                output = process.check_output(command, shell=True)

            elif self.os_type == 'windows' or self.os_type == 'win':

                bash_dir = os.environ.get('bash')

                if bash_dir is None:

                    raise InvalidConfigurations('bash environmental variable doesn\'t exist')

                output = process.check_output([bash_dir, '-c', command], shell=True)

            else:

                raise InvalidConfigurations(f'Invalid OS Type : {self.os_type}')

        except process.CalledProcessError as error:

            content = {f'CalledProcessError': 'OS::run_commands(...), ' + str(error)}
            Logger.write_messages_json(content)

            return None

        else:

            output = output.decode()

        if multi_outputs:

            output = output.split(multi_output_sep)

        return output


class Reader:

    @staticmethod
    def json_to_dict(json_filename):

        if not OS.file_exists(json_filename):

            Logger.warning(f'File: {json_filename} Doesn\'t Exist')

            return None

        content: dict

        with open(json_filename, "r") as buffer:

            content = json.load(buffer)

        return content


class Writer:

    @staticmethod
    def dict_to_json(json_filename, content, overwrite=False, indent_level=3, sort_keys=False, separators=(',', ':')):

        is_file_exist = OS.file_exists(json_filename)

        if not is_file_exist and overwrite:

            Logger.warning(f'overwrite=True, File: {json_filename} is Not Exists')

        elif is_file_exist and not overwrite:

            Logger.warning(f'File: {json_filename} Already Exists')

            ok = input('Do you want to continue - [y/n]: ')

            if ok.lower() == 'n':

                return None

            elif ok.lower() != 'y':

                Logger.error(f'Abort')

                return None

        if not is_file_exist:

            with open(json_filename, 'w+') as buffer_writer:

                json.dump(content, buffer_writer, indent=indent_level, separators=separators, sort_keys=sort_keys)
        else:

            new_content: dict

            with open(json_filename, 'r+') as buffer:

                new_content = json.load(buffer)
                new_content.update(content)

                buffer.seek(0)
                json.dump(new_content, buffer, indent=indent_level, separators=separators, sort_keys=sort_keys)
                buffer.truncate()

    @staticmethod
    def dict_to_csv(csv_filename, content, overwrite=False, use_pandas=True):

        is_file_exist = OS.file_exists(csv_filename)

        if not is_file_exist and overwrite:

            Logger.warning(f'overwrite=True, File: {csv_filename} is Not Exists')

        elif is_file_exist and not overwrite:

            Logger.warning(f'File: {csv_filename} Already Exists')

            ok = input('Do you want to continue - [y/n]: ')

            if ok.lower() == 'n':

                return None

            elif ok.lower() != 'y':

                Logger.error(f'Abort')

                return None

        if not use_pandas:

            if not is_file_exist:

                with open(csv_filename, 'w+') as buffer_writer:

                    csv_writer = csv.writer(buffer_writer)
                    csv_writer.writerow(content.keys())
                    csv_writer.writerow(content.values())

            else:

                new_content: dict

                with open(csv_filename, 'a') as buffer_writer:

                    csv_writer = csv.writer(buffer_writer)
                    csv_writer.writerow(content.values())
        else:

            dataframe = pd.DataFrame(content)
            dataframe.to_csv(csv_filename, index=False, encoding='utf-8')


class Requests:

    @staticmethod
    def safe_request(response):

        status_code = response.status_code

        if status_code is not 200:

            content = {'error_type': None,
                       'headers': response.headers,
                       'status_code': response.status_code,
                       'reason': response.reason}

            Logger.error(content)

            return None

        return response

    @staticmethod
    def sleep(secs):

        time.sleep(secs)

        
class Formatter:

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
