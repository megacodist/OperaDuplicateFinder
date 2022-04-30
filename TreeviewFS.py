from cmath import log
from collections import namedtuple
from enum import IntFlag
import logging
import os
from pathlib import Path
from PIL.ImageTk import PhotoImage
import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont

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
        **kwargs
    ) -> None:
        # Initializing super class...
        super().__init__(
            master,
            **kwargs
        )

        # Getting the font of the tree view...
        self._font = None
        try:
            self._font = self['font']
        except tk.TclError:
            self._font = nametofont('TkDefaultFont')
        
        #
        self.bind('<Configure>', self._OnWidthChanged)
        
        # Getting the minimum width of the column...
        self.update()
        self._columnMinWidth = self.winfo_width() - 4
    
    def _OnWidthChanged(self, event: tk.Event) -> None:
        if event.width - 4 > self._columnMinWidth:
            self.column(
                '#0',
                width=event.width
            )

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
        image: PhotoImage
    ) -> None:
        # Checking dir parameter & getting dirParts
        if isinstance(dir, Path):
            dirParts = dir.parts
        elif isinstance(dir, str):
            dirParts = Path(dir).parts
        else:
            raise TypeError("'dir' must be either a Path object or a string")
        
        dirPartsIndex = 0
        status = _Status.TO_DO_NOTHING
        # The root item id...
        currItem = ''

        try:
            while True:
                # Getting an ordered list of all folder children of currItem...
                foldersList = OrderedList(
                    collision=CollisionPolicy.end,
                    key=lambda item: item.root
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
                        currItem = foldersList[index_]
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
                            dirPartsIndex -= 1
                            currItemPartsIndex -= 1
                            if currItemPartsIndex == (len(currItemParts) - 1):
                                # Not changing the initial value of TO_DO_NOTHING of status to indicate updating currItem...
                                pass
                            else:
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
            newItem = self.insert(
                parent=parentItem,
                index=currItemPos,
                text=os.sep.join(currItemParts[:currItemPartsIndex]),
                open=True,
                values=(
                    {
                        'textWidth': self._font.measure(currItemParts[:currItemPartsIndex])
                    }
                )
            )

            # Detaching currItem from tree view & adjusting its text...
            self.detach(currItem)
            self.item(
                currItem,
                text=os.sep.join(currItemParts[currItemPartsIndex:]),
                values=(
                    {
                        'textWidth': self._font.measure(currItemParts[currItemPartsIndex:])
                    }
                )
            )

            #
            self.move(
                item=currItem,
                parent=newItem,
                index=0
            )
            currItem = newItem

        # Checking the need to the current item...
        if status & _Status.TO_BREAK_DIR:
            self.insert(
                parent=currItem,
                index=index_,
                text=os.sep.join(dirParts[dirPartsIndex:]),
                image=image,
                values=(
                    {
                        'textWidth': self._font.measure(dirParts[dirPartsIndex:])
                    }
                )
            )