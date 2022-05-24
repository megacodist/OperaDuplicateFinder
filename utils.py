# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

__doc__ = """This module exposes the ollowing types:

NameDirPair(name=XXX, dir=XXX)
"""

import base64
from collections import namedtuple
import hashlib
import hmac
import logging
import re
from pathlib import Path
import pickle
import platform
from threading import Lock
from time import sleep
from typing import Any, Sequence

from megacodist.exceptions import LoopBreakException
from megacodist.singleton import SingletonMeta


class AppSettings(object, metaclass=SingletonMeta):
    """Encapsulates APIs for persistence settings between different sessions
    of the application. This class offers a singleton object which must
    typically be used as follow:

    Firstly, AppSettings().Load('path/to/the/file') to load settings from
    the specified file.

    Secondly, AppSettings().Read(defaults) with a dictionary-like object whcih
    contains default value for settings (fallback).

    Thirdly, AppSettings().Update(new_values) with a dictionary-like object
    whcih contains new values for settings.

    Finally, AppSettings().Save() to save settings to the file.
    """

    def __init__(self) -> None:
        self.settings: dict[str, Any] = {}
        self.lock = Lock()
        self.file = None

    def Load(self, file: str | Path) -> None:
        """Loads settings from the specified file into the
        singleton object.
        """
        # Getting hold of settings singleton object...
        count = 0
        while not self.lock.acquire(True, 0.25):
            sleep(0.25)
            count += 1
            if count > 16:
                logging.error(
                    'Could not getting hold of settings singleton object')
                return

        # Reading settings from the file...
        self.file = file
        try:
            settingsFileStream = open(
                file,
                mode='rb')
            raw_settings = settingsFileStream.read()

            # Checking the signature...
            try:
                signature_ = hmac.digest(
                    key=b'a-secret-key',
                    msg=raw_settings[44:],
                    digest=hashlib.sha256)
                signature_ = base64.b64encode(signature_)
                isOk = hmac.compare_digest(
                    raw_settings[:44],
                    signature_)
                if isOk:
                    raw_settings = base64.b64decode(raw_settings[44:])
                    self.settings = pickle.loads(raw_settings)
            except Exception:
                # An error occurred checking signature of the settings file
                # Leaving settings dictionary empty...
                pass
        except Exception as err:
            # An error occurred reading the settings file
            # Leaving settings dictionary empty...
            logging.error(f'Loading settings file failed\n{str(err)}')
        finally:
            settingsFileStream.close()
            self.lock.release()

    def Save(self) -> None:
        """Saves settings to the file."""
        # Getting hold of settings singleton object...
        count = 0
        while not self.lock.acquire(True, 0.25):
            sleep(0.25)
            count += 1
            if count > 16:
                logging.error(
                    'Could not getting hold of settings singleton object')
                return

        try:
            # Turning 'settings' to bytes (pickling)...
            binSettings = pickle.dumps(self.settings)
            binSettings = base64.b64encode(binSettings)

            # Signing the settings...
            # signature_ will be 64 bytes long...
            signature_ = hmac.digest(
                key=b'a-secret-key',
                msg=binSettings,
                digest=hashlib.sha256)
            # signature_ will be 86 bytes long...
            signature_ = base64.b64encode(signature_)

            # Writing settings to the file...
            with open(self.file, mode='wb') as settingsFileStream:
                settingsFileStream.write(signature_)
                settingsFileStream.write(binSettings)
        finally:
            self.lock.release()

    def Read(self, defaults: dict[str, Any]) -> dict[str, Any]:
        """Checks settings against defaults. If exists return settings
        otherwise merge defaults into the settings (fallback).
        """
        # Getting hold of settings singleton object...
        count = 0
        while not self.lock.acquire(True, 0.25):
            sleep(0.25)
            count += 1
            if count > 16:
                logging.error(
                    'Could not getting hold of settings singleton object')
                return defaults

        for key, value in defaults.items():
            if ((key not in self.settings) or
                    (not isinstance(self.settings[key], type(value)))):
                self.settings[key] = value

        settings_ = self.settings.copy()
        self.lock.release()
        return settings_

    def Update(self, new_values: dict[str, Any]) -> None:
        """Updates singleton object with new values."""
        # Getting hold of settings singleton object...
        count = 0
        while not self.lock.acquire(True, 0.25):
            sleep(0.25)
            count += 1
            if count > 16:
                logging.error(
                    'Could not getting hold of settings singleton object')
                return

        try:
            for key, value in new_values.items():
                self.settings[key] = value
        finally:
            self.lock.release()


NameDirPair = namedtuple(
    'NameDirPair',
    'name, dir')


def ConfigureLogging(filepath: str | Path) -> None:
    # Getting root logger...
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Logging platform information...
    loggerFileStream = logging.FileHandler(filepath, 'w')
    loggerFormatter = logging.Formatter('%(message)s')
    loggerFileStream.setFormatter(loggerFormatter)
    logger.addHandler(loggerFileStream)

    logNote = (
        f'Operating system: {platform.system()} {platform.release()}'
        + f'(version: {platform.version()}) {platform.architecture()}')
    logging.info(logNote)
    temp = '.'.join(platform.python_version_tuple())
    logNote = f'Python interpreter: {platform.python_implementation()} {temp}'
    logging.info(logNote + '\n\n')

    # Logging program events...
    logger.removeHandler(loggerFileStream)
    loggerFileStream = logging.FileHandler(filepath, 'a')
    loggerFormatter = logging.Formatter(
        fmt=(
            '[%(asctime)s]  %(module)s  %(threadName)s'
            + '\n%(levelname)8s: %(message)s\n\n'),
        datefmt='%Y-%m-%d  %H:%M:%S')
    loggerFileStream.setFormatter(loggerFormatter)
    logger.addHandler(loggerFileStream)


def GetCommonAffix(
        *texts: Sequence,
        is_suffix: bool = False
        ) -> slice:
    '''Returns the common affix, either prefix or suffix, of two or more
    sequences and returns a slice object specifying the intersection (at
    the start or end). It accepts two or more sequences, aggregated in
    'texts' parameter, if less is provided TypeError exception will be
    raised. The optional 'is_suffix' parameter specifies the affix, either
    prefix or suffix. So to find the common suffix set this parameter
    to true.
    '''

    # Checking parameters...
    if len(texts) < 2:
        raise TypeError('At least two sequences must be provided.')

    if is_suffix:
        startIndex = -1
        increment = -1
    else:
        startIndex = 0
        increment = 1

    index = startIndex
    while True:
        try:
            for seqIndex in range(len(texts) - 1):
                if texts[seqIndex][index] != texts[seqIndex + 1][index]:
                    # Stopping comparisons
                    # when the first inequality if found...
                    raise LoopBreakException
        except (IndexError, LoopBreakException):
            # Stopping comparisons when the first sequence is exhausted...
            break

        index += increment

    if is_suffix:
        return slice(index - startIndex, None)
    else:
        return slice(startIndex, index)


def ReportDuplicates(
        filesList: list[NameDirPair]
        ) -> tuple[list[list[NameDirPair], list[NameDirPair]]]:

    duplicates = []
    allDuplicates = []
    similars = []
    allSimilars = []

    i = 0
    while i < len(filesList):
        if duplicates:
            duplicates = []
        if similars:
            similars = []
        j = i + 1
        firstFileNoExt = Path(filesList[i].name).stem
        lenFirstFileNoExt = len(firstFileNoExt)
        try:
            while True:
                nextFileNoExt = Path(filesList[j].name).stem
                _, commonPrefixIndex, _ = GetCommonAffix(
                    firstFileNoExt,
                    nextFileNoExt
                ).indices(lenFirstFileNoExt)

                if commonPrefixIndex < lenFirstFileNoExt:
                    break

                isDupPosfix = IsDuplicatePostfix(
                    nextFileNoExt[commonPrefixIndex:])

                if isDupPosfix:
                    duplicates.append(filesList[j])
                else:
                    similars.append(filesList[j])

                j += 1
        except IndexError:
            pass
        finally:
            if duplicates:
                duplicates.insert(0, filesList[i])
                allDuplicates.append(duplicates)
            if similars:
                similars.insert(0, filesList[i])
                allSimilars.append(similars)
        i = j

    return allDuplicates, allSimilars


def IsDuplicatePostfix(text: str) -> bool:
    '''Determines if 'text' is a duplicate postfix like ' - (23)', '_23', and
    so on. The following categories will be identified:

    ⬤ XXXX - 23
    ⬤ XXXX - (23)
    ⬤ XXXX-23
    ⬤ XXXX-(23)
    ⬤ XXXX _ 23
    ⬤ XXXX _ (23)
    ⬤ XXXX_23
    ⬤ XXXX_(23)
    ⬤ XXXX(23)
    ⬤ XXXX (23)
    ⬤ XXXX_copy
    ⬤ XXXX-copy
    ⬤ XXXX copy
    ⬤ XXXX - copy
    ⬤ XXXX _ copy
    ⬤ XXXX_copy copy
    ⬤ XXXX - copy - copy
    ⬤ XXXX copy copy
    and so on.'''

    match = re.search(
        r'^\s*[-_]+\s*\(\?\d+\)?$',
        text)
    if match:
        return True

    match = re.search(
        r'^\s*\(\d+\)$',
        text)
    if match:
        return True

    match = re.search(
        r'(?:[-_ ]*copy)+',
        text)
    if match:
        return True

    return False
