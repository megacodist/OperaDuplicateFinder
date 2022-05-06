# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import base64
import hashlib
import hmac
import logging
from pathlib import Path
import pickle
import platform
from typing import Any

from dup_finder import DupFinder


# Definning global variables...
_MODULE_DIR = Path(__file__).resolve().parent


def _LoadAppSettings():
    # Reading settings from the file...
    try:
        settingsFileStream = open(
            _MODULE_DIR / 'bin.bin',
            mode='rb'
        )
        settings = settingsFileStream.read()
        #settings = base64.b64decode(settings)
    except Exception:
        settings = {}
    finally:
        settingsFileStream.close()
    
    # Checking the signature...
    signature_ = hmac.digest(
        key=b'a-secret-key',
        msg=settings[44:],
        digest=hashlib.sha256
    )
    isOk = hmac.compare_digest(
        settings[:44],
        signature_
    )
    if isOk:
        settings = base64.b64decode(settings)
        settings = pickle.loads(settings)
    else:
        settings = {}

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

    return settings

def _SaveAppSettings(settings: dict[str, Any]):
    # Turning 'settings' to bytes (pickling)...
    binSettings = pickle.dumps(settings)
    binSettings = base64.b64encode(binSettings)

    # Signing the settings...
    # signature_ will be 64 bytes long...
    signature_ = hmac.digest(
        key=b'a-secret-key',
        msg=binSettings,
        digest=hashlib.sha256
    )
    # signature_ will be 86 bytes long...
    signature_ = base64.b64encode(signature_)

    # Writing settings to the file...
    with open(_MODULE_DIR / 'bin.bin', mode='wb') as settingsFileStream:
        settingsFileStream.write(signature_)
        settingsFileStream.write(binSettings)


if (__name__ == '__main__'):
    # Configuring logging ============================================================================================================
    # Getting root logger...
    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)

    # Logging platform information...
    _loggerPath = (Path(__name__).resolve().parent) / 'log.log'
    _loggerFileStream = logging.FileHandler(_loggerPath, 'w')
    _loggerFormatter = logging.Formatter('%(message)s')
    _loggerFileStream.setFormatter(_loggerFormatter)
    _logger.addHandler(_loggerFileStream)

    _logNote = f'Operating system: {platform.system()} {platform.release()} (version: {platform.version()}) {platform.architecture()}'
    logging.info(_logNote)
    temp = '.'.join(platform.python_version_tuple())
    _logNote = f'Python interpreter: {platform.python_implementation()} {temp}'
    logging.info(_logNote + '\n\n')

    # Logging program events...
    _logger.removeHandler(_loggerFileStream)
    _loggerFileStream = logging.FileHandler(_loggerPath, 'a')
    _loggerFormatter = logging.Formatter(
        fmt='[%(asctime)s]  %(module)s\n%(levelname)8s: %(message)s\n\n',
        datefmt='%Y-%m-%d  %H:%M:%S'
    )
    _loggerFileStream.setFormatter(_loggerFormatter)
    _logger.addHandler(_loggerFileStream)
    logging.info('Started')

    # Running the application ================================================
    # Getting settings...
    settinngs = _LoadAppSettings()
    # Running app...
    dup_finder_win = DupFinder(
        cwd=_MODULE_DIR,
        settings=settinngs
    )
    dup_finder_win.mainloop()
    # Saving settings...
    _SaveAppSettings(dup_finder_win.GetSettings())