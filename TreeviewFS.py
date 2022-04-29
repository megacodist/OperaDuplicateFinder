from collections import namedtuple
from enum import IntFlag, auto
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont
from typing import Literal

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
        master: tk.Misc | None = ...,
        *,
        class_: str = ...,
        columns: str | list[str] | tuple[str, ...] = ...,
        cursor: tk._Cursor = ...,
        displaycolumns: str | list[str] | tuple[str, ...] | list[int] | tuple[int, ...] | Literal["#all"] = ...,
        height: int = ...,
        name: str = ...,
        padding: tk._Padding = ...,
        selectmode: Literal["extended", "browse", "none"] = ...,
        show: Literal["tree", "headings", "tree headings", ""] | list[str] | tuple[str, ...] = ...,
        style: str = ...,
        takefocus: tk._TakeFocusValue = ...,
        xscrollcommand: tk._XYScrollCommand = ...,
        yscrollcommand: tk._XYScrollCommand = ...
    ) -> None:
        # Initializing super class...
        super().__init__(
            master,
            class_=class_,
            columns=columns,
            cursor=cursor,
            displaycolumns=displaycolumns,
            height=height,
            name=name,
            padding=padding,
            selectmode=selectmode,
            show=show,
            style=style,
            takefocus=takefocus,
            xscrollcommand=xscrollcommand,
            yscrollcommand=yscrollcommand
        )

        # Getting the font of the tree view...
        self._font = None
        try:
            self._font = self['font']
        except tk.TclError:
            self._font = nametofont('TkDefaultFont')
        
        #
        self.wait_visibility()
        self.bind()
        
        # Getting the minimum width of the column...
        self.update()
        self._columnMinWidth = self.winfo_width('<Configure>', self._OnWidthChanged)
    
    def _OnWidthChanged(self, event: tk.Event) -> None:
        if event.width > self._columnMinWidth:
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
        
        return tuple(
            tuple(folders),
            tuple(files)
        )

    def AddFolder(self, dir: str | Path) -> None:
        # Checking dir parameter & getting dirParts
        if isinstance(dir, Path):
            dirParts = dir.parts
        elif isinstance(dir, str):
            dirParts = Path(dir).parts
        else:
            raise TypeError("'dir' must be either a Path object or a string")
        
        dirPartsIndex = 0
        status = _Status.TO_DO_NOTHING
        currItem = self.item('')
        try:
            while dirPartsIndex < len(dirParts):
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
                
                # Getting an ordered list of all folder children of currItem...
                foldersList = OrderedList(
                    collision=CollisionPolicy.end,
                    key=lambda item: item[1]
                )
                for folder in self.GetFoldersFiles(currItem)[0]:
                    foldersList.Put(
                        _IDRoot(
                            folder,
                            Path(
                                self.item(
                                    folder,
                                    'text'
                                )
                            ).parts[0]
                        )
                    )
                
                # Getting index in the current item folder children...
                index_ = foldersList.index(dirParts[dirPartsIndex])
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
                    pass
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
            
            #
            newItem = self.insert(
                parent=parentItem,
                index=currItemPos,
                text=currItemParts[:currItemPartsIndex],
                open=True,
                values=(
                    {
                        'textWidth': self._font.measure(currItemParts[:currItemPartsIndex])
                    }
                )
            )

        # Checking the need to the current item...
        if status & _Status.TO_BREAK_DIR:
            pass