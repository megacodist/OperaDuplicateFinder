# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import namedtuple
from enum import IntFlag
import logging
from pathlib import Path
from PIL.ImageTk import PhotoImage
import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont

from megacodist.exceptions import LoopBreakException
from megacodist.collections import OrderedList, CollisionPolicy
from utils import NameDirPair


_IDRoot = namedtuple(
    '_IDRoot',
    'id, root')


class _Status(IntFlag):
    TO_DO_NOTHING = 0x00
    TO_BREAK_ITEM = 0x01
    TO_BREAK_DIR = 0x02


class TreeviewFS(ttk.Treeview):
    '''Subclasses tkinter.ttk.Treeview to consolidate all file system
    visualization related functionalities into this class.
    '''

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
                width=newWidth)

    def _OnDeleteKey(self, event: tk.Event) -> None:
        # Getting selected item...
        selectedItemID = self.selection()
        if not selectedItemID:
            # DELETE pressed, nothing selected
            return

        parentID = self.parent(selectedItemID[0])
        self.delete(selectedItemID)

        # If there is one sibbling folder,
        # merging the parent and the sibbling of deleted item...
        folders, files = self.GetFoldersFiles(parentID)
        if len(folders) == 1 and len(files) == 0:
            # Appending sibbling text to parent...
            newParentText = str(Path(
                self.item(parentID, 'text'),
                self.item(folders[0], 'text')))
            self.item(
                parentID,
                text=newParentText)

            # Detaching the only folder sibbling...
            self.detach(folders[0])

            # Moving its childern to its parent...
            for childID in self.get_children(folders[0]):
                self.move(
                    item=childID,
                    parent=parentID,
                    index='end')

            self.delete(folders[0])

    @classmethod
    def _CompareFolders(cls, folder: Path) -> str:
        """Defines the comparer for an OrderedList that contains folders."""
        return folder.root.lower()

    @classmethod
    def _CompareFiles(cls, file: Path) -> tuple[str, str]:
        """Defines the comparer for an OrderedList that contains files."""
        return (file.stem.lower(), file.name.lower())

    def GetFullPath(
        self,
        id: str
    ) -> str:
        parts = []
        while id:
            text_ = self.item(
                id,
                'text')
            parts.append(text_)

            id = self.parent(id)

        parts.reverse()
        return str(Path(*parts))

    def GetFoldersFiles(self, iid: str) -> tuple[tuple[str], tuple[str]]:
        '''Returns a pair (2-tuple) which first element is a tuple of all
        folder children and second element is a tuple of all file children
        of 'iid' item in the tree view.
        '''

        folders = []
        files = []
        for child in self.get_children(iid):
            grandChildren = self.get_children(child)
            if len(grandChildren) > 0:
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
        '''Adds a older to the tree view. If the the folder does not exist
        of has no files inside, it raises a ValueError.
        '''

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
                    key=TreeviewFS._CompareFolders
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
                    logging.warning(
                        f"The return value of "
                        f"'{foldersList.__class__.__name__}.index' method "
                        f"must be either 'None' or 'int'.")
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
                                # Not changing the initial value of TO_DO_NOTHING
                                # of status to indicate updating currItem...
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

        # Checking the need to break the current item...
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

        # Checking whether only a portion of dir path is needed...
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
            filesList = OrderedList(key=TreeviewFS._CompareFiles)
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
            self._UpdateItem(currItem)

    def _UpdateItem(self, iid: str) -> None:
        # Getting all current folders & files in the list...
        folders, files = self.GetFoldersFiles(iid)
        filesList = OrderedList(
            collision=CollisionPolicy.ignore,
            key=TreeviewFS._CompareFiles)
        for file in files:
            filesList.Put(file)
        # Getting all files of iid in the file system...
        # Adding them to the TreeViewFS
        parentFSPath = Path(self.GetFullPath(iid))
        for item in parentFSPath.iterdir():
            if item.is_file():
                idx = filesList.Put(item)
                if idx:
                    self.insert(
                        parent=iid,
                        index=idx + len(folders),
                        text=item.name,
                        image=self.img_file,
                        values=(self._font.measure(item.name),))

    '''def GetFileDirList(self) -> list[NameDirPair]:
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
            )'''
