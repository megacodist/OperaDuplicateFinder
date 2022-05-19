# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""This module exposes the ollowing types:

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

from megacodist.text import GetCommonAffix


# Golbal variables of the module
APP_DIR = None
settings = {}


NameDirPair = namedtuple(
    'NameDirPair',
    'name, dir')


def SetAppDir(appDir: Path) -> None:
    global APP_DIR
    APP_DIR = appDir


def ConfigureLogging(app_dir: Path) -> None:
    # Getting root logger...
    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)

    # Logging platform information...
    _loggerPath = app_dir / 'log.log'
    _loggerFileStream = logging.FileHandler(_loggerPath, 'w')
    _loggerFormatter = logging.Formatter('%(message)s')
    _loggerFileStream.setFormatter(_loggerFormatter)
    _logger.addHandler(_loggerFileStream)

    _logNote = (f'Operating system: {platform.system()} {platform.release()}'
                + f'(version: {platform.version()}) {platform.architecture()}')
    logging.info(_logNote)
    temp = '.'.join(platform.python_version_tuple())
    _logNote = f'Python interpreter: {platform.python_implementation()} {temp}'
    logging.info(_logNote + '\n\n')

    # Logging program events...
    _logger.removeHandler(_loggerFileStream)
    _loggerFileStream = logging.FileHandler(_loggerPath, 'a')
    _loggerFormatter = logging.Formatter(
        fmt='[%(asctime)s]  %(module)s\n%(levelname)8s: %(message)s\n\n',
        datefmt='%Y-%m-%d  %H:%M:%S')
    _loggerFileStream.setFormatter(_loggerFormatter)
    _logger.addHandler(_loggerFileStream)


def SaveAppSettings() -> None:
    global settings

    # Turning 'settings' to bytes (pickling)...
    binSettings = pickle.dumps(settings)
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
    with open(APP_DIR / 'bin.bin', mode='wb') as settingsFileStream:
        settingsFileStream.write(signature_)
        settingsFileStream.write(binSettings)


def LoadAppSettings():
    global settings

    # Reading settings from the file...
    try:
        settingsFileStream = open(
            APP_DIR / 'bin.bin',
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
                settings = pickle.loads(raw_settings)
            else:
                settings = {}
        except Exception:
            # An error occurred checking signature of the settings file
            # Leaving settings dictionary empty...
            pass
    except Exception:
        # An error occurred reading the settings file
        # Leaving settings dictionary empty...
        pass
    finally:
        settingsFileStream.close()

    # Checking 'width'...
    try:
        if not isinstance(settings['width'], int):
            raise TypeError()
    except Exception:
        settings['width'] = 600

    # Checking 'height'...
    try:
        if not isinstance(settings['height'], int):
            raise TypeError()
    except Exception:
        settings['height'] = 800

    # Checking 'x'...
    try:
        if not isinstance(settings['x'], int):
            raise TypeError()
    except Exception:
        settings['x'] = 250

    # Checking 'y'...
    try:
        if not isinstance(settings['y'], int):
            raise TypeError()
    except Exception:
        settings['y'] = 250

    # Checking 'lastDir'...
    try:
        if not isinstance(settings['lastDir'], str):
            raise TypeError()
    except Exception:
        settings['lastDir'] = None


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
