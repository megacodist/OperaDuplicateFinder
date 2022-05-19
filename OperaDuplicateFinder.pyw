# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from pathlib import Path

from dup_finder import DupFinder
from utils import ConfigureLogging, AppSettings


# Definning global variables...
_MODULE_DIR = Path(__file__).resolve().parent


if (__name__ == '__main__'):
    # Configuring logging...
    ConfigureLogging(_MODULE_DIR / 'log.log')
    logging.info('Started')

    # Loading settings...
    AppSettings().Load(_MODULE_DIR / 'bin.bin')

    # Running the application...
    dupFinderWin = DupFinder(appDir=_MODULE_DIR)
    dupFinderWin.mainloop()

    # Saving settings for next session...
    AppSettings().Save()
