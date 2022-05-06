# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import namedtuple
from enum import IntFlag
import json
import logging
from pathlib import Path
from PIL.ImageTk import PhotoImage
import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont

from duplicate_util import NameDirPair

from megacodist.exceptions import LoopBreakException
from megacodist.collections import OrderedList, CollisionPolicy


_IDRoot = namedtuple(
    '_IDRoot',
    'id, root'
)


class _Status(IntFlag):
    TO_DO_NOTHING = 0x00
    TO_BREAK_ITEM = 0x01
    TO_BREAK_DIR  = 0x02


class TreeviewFS(ttk.Treeview):
    '''Subclasses tkinter.ttk.Treeview to consolidate all file system visualization related functionalities into this class.'''

    def __init__(
        self,
        master: tk.Misc | None = None,
         *,
        img_folder: None | PhotoImage = None,
        img_file: None | PhotoImage = None,
        **kwargs
    ) -> None:
        # Initializing super class...
        super().__init__(
            master,
            **kwargs
        )
        # Setting images...
        self.img_folder = img_folder
        self.img_file = img_file

        # Getting the font of the tree view...
        self._font = None
        try:
            self._font = self['font']
        except tk.TclError:
            self._font = nametofont('TkDefaultFont')
        
        # Binding events ------------------------------
        # Binding the resize event...
        self.bind('<Configure>', self._OnWidthChanged)
        # Binding the DELETE key event...
        self.bind('<Delete>', self._OnDeleteKey)
        
        # Treeview column width management----------------
        # Getting the minimum width of the column...
        self.update()
        self._columnMinWidth = self.winfo_width() - 4
    
    def _OnWidthChanged(self, event: tk.Event) -> None:
        newWidth = event.width - 4
        if newWidth > self._columnMinWidth:
            self.column(
                '#0',
                width=newWidth
            )
    
    def _OnDeleteKey(self, event: tk.Event)-> None:
        # Getting selected item...
        selectedItemID = self.selection()
        if selectedItemID:
            parentID = self.parent(selectedItemID[0])
            self.delete(selectedItemID)

            # If there is one sibbling folder, merging the parent and the sibbling...
            pass
    
    def GetFullPath(
        self,
        id: str
    ) -> str:
        parts = []
        while id:
            text_ = self.item(
                id,
                'text'
            )
            parts.append(text_)

            id = self.parent(id)
        
        parts.reverse()
        return str(Path(*parts))

    def GetFoldersFiles(self, iid: str) -> tuple[tuple[str], tuple[str]]:
        '''Returns a pair (2-tuple) which first element is a tuple of all folder children and second element is
        a tuple of all file children of 'iid' item in the tree view.'''

        folders = []
        files = []
        for child in self.get_children(iid):
            grandChildrenNum = self.get_children(child)
            if len(grandChildrenNum) > 0:
                folders.append(child)
            else:
                files.append(child)
        
        return tuple([
            tuple(folders),
            tuple(files)
        ])

    def AddFolder(
        self,
        dir: str | Path,
        subfolders: bool = False
    ) -> None:
        '''Adds a older to the tree view. If the the folder does not exist of has no files inside, it raises
        a ValueError.'''

        # Checking dir parameter & getting dirParts
        if isinstance(dir, str):
            dir = Path(dir)
        elif not isinstance(dir, Path):
            raise TypeError("'dir' must be either a Path object or a string")
        
        # Checking existence of such folder in file system...
        if not (dir.exists() and dir.is_dir()):
            raise ValueError(f"'{str(dir)}'.\nSuch folder does not exist")
        
        # Checking whether dir contains at least one file...
        for item in dir.iterdir():
            if item.is_file():
                break
        else:
            raise ValueError(f"'{str(dir)}' does not contain any file.")
        
        # Starting algorithm...
        dirParts = Path(dir).parts
        dirPartsIndex = 0
        status = _Status.TO_DO_NOTHING
        # The root item id...
        currItem = ''
        try:
            while True:
                # Getting an ordered list of all folder children of currItem...
                foldersList = OrderedList(
                    collision=CollisionPolicy.end,
                    key=lambda item: item.root.lower()
                )
                for folderID in self.GetFoldersFiles(currItem)[0]:
                    foldersList.Put(
                        _IDRoot(
                            folderID,
                            Path(
                                self.item(
                                    folderID,
                                    'text'
                                )
                            ).parts[0]
                        )
                    )
                
                # Getting index in the current item folder children...
                index_ = foldersList.index(
                    _IDRoot(None, dirParts[dirPartsIndex])
                )
                if index_ is None:
                    index_ = 0
                    status = _Status.TO_BREAK_DIR
                    break
                elif isinstance(index_, int):
                    if index_ < 0:
                        index_ = -index_
                        status = _Status.TO_BREAK_DIR
                        break
                    else:
                        currItem = foldersList[index_].id
                        dirPartsIndex += 1
                else:
                    # Oops, something went wrong, logging a warning...
                    logging.warning(f"The return value of '{foldersList.__class__.__name__}.index' method must be either 'None' or 'int'.")
                    return
                
                # Checking text of currItem...
                currItemParts = Path(self.item(
                    currItem,
                    'text'
                )).parts
                currItemPartsIndex = 1

                while True:
                    # Checking current item...
                    try:
                        if dirParts[dirPartsIndex] == currItemParts[currItemPartsIndex]:
                            dirPartsIndex += 1
                            currItemPartsIndex += 1
                        else:
                            status = _Status.TO_BREAK_ITEM | _Status.TO_BREAK_DIR
                            index = 0
                            raise LoopBreakException()
                    except IndexError:
                        # Checking dirParts exhausted...
                        if dirPartsIndex >= len(dirParts):
                            # Checking if currItemParts exhausted as well...
                            if currItemPartsIndex >= len(currItemParts):
                                # Both parts exhausted
                                # Not changing the initial value of TO_DO_NOTHING of status to indicate updating currItem...
                                pass
                            else:
                                # Only dirParts exhausted
                                status = _Status.TO_BREAK_ITEM
                            raise LoopBreakException()
                        # Checking currItemParts exhausted...
                        else:
                            break
        except LoopBreakException:
            pass


        # Checking the need to the current item...
        if status & _Status.TO_BREAK_ITEM:
            parentItem = self.parent(currItem)

            # Getting currItem position in parent item...
            currItemPos = 0
            for item in self.get_children(parentItem):
                if currItem == item:
                    break
                else:
                    currItemPos += 1
            
            # Inserting new item in place of currItem with clipped text...
            text_ = str(Path(*currItemParts[:currItemPartsIndex]))
            newItem = self.insert(
                parent=parentItem,
                index=currItemPos,
                text=text_,
                image=self.img_folder,
                open=True,
                values=(self._font.measure(text_),)
            )

            # Detaching currItem from tree view & adjusting its text...
            self.detach(currItem)
            text_ = str(Path(*currItemParts[currItemPartsIndex:]))
            self.item(
                currItem,
                text=text_,
                values=(self._font.measure(text_),)
            )

            #
            self.move(
                item=currItem,
                parent=newItem,
                index=0
            )
            currItem = newItem

        # Checking whether a portion of dir path...
        if status & _Status.TO_BREAK_DIR:
            text_ = str(Path(*dirParts[dirPartsIndex:]))
            currItem = self.insert(
                parent=currItem,
                index=index_,
                text=text_,
                open=True,
                image=self.img_folder,
                values=(self._font.measure(text_),)
            )
        
        # Checking to whether to retrieve  or update the folder content...
        if status:
            # The folder item created & its ID is currItem
            # Getting its content...
            filesList = OrderedList(key=lambda item: (item.stem.lower(), item.name.lower()))
            for item in dir.iterdir():
                if item.is_file():
                    filesList.Put(item)
            for file in filesList:
                self.insert(
                    parent=currItem,
                    index='end',
                    text=file.name,
                    image=self.img_file,
                    values=(self._font.measure(file.name),)
                )
        else:
            # There is neither TO_BREAK_DIR nor TO_BREAK_ITEM flags
            # Updating currItem...
            pass
    
    def GetFileDirList(self) -> list[NameDirPair]:
        list_ = []
        self._UpdateFileDirList(
            '',
            '',
            list_
        )
        return list_

    def _UpdateFileDirList(
        self,
        iid: str,
        path: str,
        filesList: list[NameDirPair]
    ) -> None:
        folders, files = self.GetFoldersFiles(iid)

        for itemID in files:
            filesList.append(
                NameDirPair(
                    name=self.item(itemID, 'text'),
                    dir=path
                )
            )
        
        for itemID in folders:
            self._UpdateFileDirList(
                itemID,
                str(Path(path, self.item(itemID, 'text'))),
                filesList
            )
    
    '''# Treeview column width management (1 of 5)
    def _GetMaxTextWidth(self, level: int) -> int:
        return self._GetMaxTextWidth_Recursively(
            '',
            0,
            level
        )

    # Treeview column width management (2 of 5)
    def _GetMaxTextWidth_Recursively(
        self,
        id: str,
        thisLevel: int,
        requestedLevel: int
    ) -> int:
        # Checking stop recursion condition...
        if thisLevel == requestedLevel:
            return self._font.measure(self.item(id, 'text'))
        # Checking to continue recursion...
        elif thisLevel < requestedLevel:
            maxWidth = 0
            for childID in self.GetFoldersFiles(childID)[0]:
                width = self._GetMaxTextWidth_Recursively(
                    id=childID,
                    thisLevel=thisLevel + 1,
                    requestedLevel=requestedLevel
                )
                if width > maxWidth:
                    maxWidth = width
            
            return maxWidth
        else:
            # Oops something went wrong...
            logging.warning("In '_GetMaxTextWidth_Recursively' it is impossible 'thisLevel' to be greater than 'requestedLevel'")
    
    # Treeview column width management (3 of 5)
    def _UpdateLevel(
        self,
        level: int,
        levelInfo: _LevelInfo
    ) -> None:
        try:
            self._levelsInfo[level].count += levelInfo.count
            if levelInfo.maxWidth > self._levelsInfo[level].maxWidth:
                self._levelsInfo[level].maxWidth = levelInfo.maxWidth
                self._SetColMinWidth()
        except IndexError:
            if level == len(self._levelsInfo):
                self._levelsInfo.append(levelInfo)
            else:
                # Oops something went wrong...
                logging.warning("In '_UpdateLevel', 'level' parameter is more than 1 beyond self._levelsInfo")
    
    # Treeview column width management (4 of 5)
    def _SetColMinWidth(self) -> None:
        FIRST_LEVEL_INDENT = 24
        NEXT_LEVEL_INDENT = 16

        indent = FIRST_LEVEL_INDENT
        maxWidth = 0
        for index in range(1, len(self._levelsInfo)):
            indent += NEXT_LEVEL_INDENT
            width = indent + self._levelsInfo[index].maxWidth
            if width > maxWidth:
                maxWidth = width
        
        if maxWidth > self._columnMinWidth:
            self._columnMinWidth = maxWidth
            self.column('#0', width=self._columnMinWidth)
    
    # Treeview column width management (5 of 5)
    def _RemoveFromLevel(
        self,
        level: int,
        levelInfo: _LevelInfo
    ) -> None:
        try:
            self._levelsInfo[level].count -= levelInfo.count
            if self._levelsInfo[level].count == 0:
                if level + 1 == len(self._levelsInfo):
                    self._levelsInfo.pop()
                else:
                    logging.warning("Items at level {level} deleted before some upper levels")
            elif 
        except IndexError:
            pass'''