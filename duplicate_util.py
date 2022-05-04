# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import namedtuple
import re
from pathlib import Path

from megacodist.text import GetCommonAffix


NameDirPair = namedtuple(
    'NameDirPair',
    'name, dir'
)


def ReportDuplicates(filesList: list[NameDirPair]) -> tuple[list[list[NameDirPair], list[NameDirPair]]]:
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

                match = re.search(
                    r'^\s*\(\d+\)$',
                    nextFileNoExt[commonPrefixIndex:]
                )

                if match:
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