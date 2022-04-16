# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
import PIL.Image, PIL.ImageTk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from tkinter.font import nametofont
from typing import Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class DupFinder(tk.Tk):
    class DirectoryEventHandler(FileSystemEventHandler):
        def __init__(self, dupFinder: Any) -> None:
            super().__init__()
            self._trvw = dupFinder

        def on_created(self, event):
            itemLabel = Path(event.src_path).name
            self._trvw.trvw_files.insert(tk.END, itemLabel)

        def on_deleted(self, event):
            itemLabel = Path(event.src_path).name
            itemIndex = self._trvw.trvw_files.get(0, tk.END).index(itemLabel)
            self._trvw.trvw_files.delete(itemIndex)

        def on_moved(self, event):
            print('moved')
    
    def __init__(self) -> None:
        super().__init__()

        # Initializing the window...
        self.title('Duplicate remover')
        self.theme = ttk.Style()
        self.theme.theme_use('clam')

        # Defining of required variables...
        self._dirs : list[str] = []
        self._columnMinWidth : int = None
        self._fsHandler = None
        self._observers : list[Observer] = []

        # Defining of resources...
        self.img_browse = None
        self.img_folder = None
        self.img_file = None
        self.img_unknown = None

        # Defining of GUI widgets...
        self.frm_toolbar = None
        self.frm_files = None
        self.btn_browse = None
        self.btn_duplicate = None
        self.btn_license = None
        self.vscrlbr_files = None
        self.hscrlbr_files = None
        self.trvw_files = None

        self._LoadResources()
        self._InitializeGUI()

        # Initializing last item...
        self._fsHandler = DupFinder.DirectoryEventHandler(dupFinder=self)
    
    def _LoadResources(self) -> None:
        '''Loads resources using the the GUI.'''

        # Loading images...
        # Loading 'browse.png'...
        self.img_browse = Path(__file__).resolve().parent
        self.img_browse = self.img_browse / 'res/browse.png'
        self.img_browse = PIL.Image.open(self.img_browse)
        self.img_browse = self.img_browse.resize(size=(24, 24,))
        self.img_browse = PIL.ImageTk.PhotoImage(image=self.img_browse)
        # Loading 'folder.png'...
        self.img_folder = Path(__file__).resolve().parent
        self.img_folder = self.img_folder / 'res/folder.png'
        self.img_folder = PIL.Image.open(self.img_folder)
        self.img_folder = self.img_folder.resize(size=(24, 24,))
        self.img_folder = PIL.ImageTk.PhotoImage(image=self.img_folder)
        # Loading 'file.png'...
        self.img_file = Path(__file__).resolve().parent
        self.img_file = self.img_file / 'res/file.png'
        self.img_file = PIL.Image.open(self.img_file)
        self.img_file = self.img_file.resize(size=(24, 24,))
        self.img_file = PIL.ImageTk.PhotoImage(image=self.img_file)
        # Loading 'unknown.png'...
        self.img_unknown = Path(__file__).resolve().parent
        self.img_unknown = self.img_unknown / 'res/unknown.png'
        self.img_unknown = PIL.Image.open(self.img_unknown)
        self.img_unknown = self.img_unknown.resize(size=(24, 24,))
        self.img_unknown = PIL.ImageTk.PhotoImage(image=self.img_unknown)
        # Loading 'duplicate.png'...
        self.img_duplicate = Path(__file__).resolve().parent
        self.img_duplicate = self.img_duplicate / 'res/duplicate.png'
        self.img_duplicate = PIL.Image.open(self.img_duplicate)
        self.img_duplicate = self.img_duplicate.resize(size=(24, 24,))
        self.img_duplicate = PIL.ImageTk.PhotoImage(image=self.img_duplicate)
        # Loading 'license.png'...
        self.img_license = Path(__file__).resolve().parent
        self.img_license = self.img_license / 'res/license.png'
        self.img_license = PIL.Image.open(self.img_license)
        self.img_license = self.img_license.resize(size=(24, 24,))
        self.img_license = PIL.ImageTk.PhotoImage(image=self.img_license)
    
    def _InitializeGUI(self) -> None:
        '''Initializes the GUI of this window with Tcl/Tk widgets.'''

        # 
        self.frm_toolbar = ttk.Frame(
            self
        )
        self.frm_toolbar.pack(
            fill='x',
            padx=2,
            pady=(2, 1,)
        )

        #
        self.btn_browse = ttk.Button(
            self.frm_toolbar,
            image=self.img_browse,
            command=self._BrowseDir
        )
        self.btn_browse.pack(
            side='left'
        )

        #
        self.btn_duplicate = ttk.Button(
            master=self.frm_toolbar,
            image=self.img_duplicate,
            state=tk.DISABLED
        )
        self.btn_duplicate.pack(
            side=tk.LEFT
        )

        #
        self.btn_license = ttk.Button(
            master=self.frm_toolbar,
            image=self.img_license
        )
        self.btn_license.pack(
            side=tk.LEFT
        )

        #
        self.frm_files = ttk.Frame(
            self
        )
        self.frm_files.pack(
            fill='both',
            expand=1,
            padx=2,
            pady=(1, 2,)
        )

        #
        self.vscrlbr_files = ttk.Scrollbar(
            self.frm_files,
            orient='vertical'
        )
        self.hscrlbr_files = ttk.Scrollbar(
            self.frm_files,
            orient='horizontal'
        )
        self.trvw_files = ttk.Treeview(
            self.frm_files,
            show='tree headings',
            selectmode='browse',
            xscrollcommand=self.hscrlbr_files.set,
            yscrollcommand=self.vscrlbr_files.set
        )
        self.vscrlbr_files.config(
            command=self.trvw_files.yview
        )
        self.hscrlbr_files.config(
            command=self.trvw_files.xview
        )
        # Configuring the default heading...
        self.trvw_files.heading(
            '#0',
            text='Name',
            anchor=tk.W
        )
        # Configuring the default column...
        self.trvw_files.column(
            '#0',
            width=200,
            stretch=False,
            anchor=tk.W
        )
        self.hscrlbr_files.pack(
            side='bottom',
            fill='x'
        )
        self.vscrlbr_files.pack(
            side='right',
            fill='y'
        )
        self.trvw_files.pack(
            fill='both',
            expand=1,
            padx=3,
            pady=3
        )

        # Binding events...
        self.wait_visibility()
        self.trvw_files.bind('<<TreeviewSelect>>', self._OnNodeChanged)
        
    def _BrowseDir(self):
        folder = filedialog.askdirectory(initialdir=Path.cwd())
        if folder:
            self._EnumFiles(folder)
    
    def _OnNodeChanged(self, event:tk.Event):
        # Getting childern of selected node
        selectedItemID = self.trvw_files.selection()
        if not selectedItemID:
            # All items have been deselected, so disabling the duplicate button...
            self.btn_duplicate['state'] = tk.DISABLED
            return

        selectedItemID = selectedItemID[0]
        childern = self.trvw_files.get_children(selectedItemID)

        if len(childern):
            self.btn_duplicate['state'] = tk.NORMAL
        else:
            self.btn_duplicate['state'] = tk.DISABLED
        
        '''# Printing the text of selected item in Treeview & all its parent...
        while selectedItemID:
            print(self.trvw_files.item(selectedItemID, option='text'))
            selectedItemID = self.trvw_files.parent(selectedItemID)'''

    def _EnumFiles(self, folder: str):
        # First of all emptying the list...
        self.trvw_files.delete(*self.trvw_files.get_children())
        self._observers.clear()

        # Second of all populating the list with files...
        currentDir = Path(folder).resolve()
        try:
            # Retreiving all files in the folder...
            items = []
            for item in currentDir.iterdir():
                if item.is_file():
                    items.append(item)
            
            # Sorting items:
            #   folders at the top
            #   files in a way that XXXX.X comes before XXXX (1).X, XXXX (2).X
            items.sort(key=lambda file : file.stem)

            # Adding parent to to the treeview...
            parentNode = self.trvw_files.insert(
                '',
                index=tk.END,
                text=str(currentDir),
                image=self.img_folder,
                open=True
            )
            
            # Getting minimum width of the column (step 1 of 3)...
            self.update()
            minColWidth = self.trvw_files.winfo_width()

            # Getting minimum width of the column (step 2 of 3)...
            appFont = nametofont('TkDefaultFont')
            itemWidth = appFont.measure(item.parent) + 40
            if itemWidth > minColWidth:
                minColWidth = itemWidth
            
            # Adding the files to their folder in the treeview...
            for item in items:                
                # Getting minimum width of the column (step 3 of 3)...
                itemWidth = appFont.measure(item.name) + 58
                if itemWidth > minColWidth:
                    minColWidth = itemWidth
                
                self.trvw_files.insert(
                    parent=parentNode,
                    index=tk.END,
                    text=item.name,
                    image=self.img_file
                )
            
            # Saving computed minimum width of the column...
            self._columnMinWidth = minColWidth
            
            # Sizing the column to minimum width...
            self.trvw_files.column(
                '#0',
                width=minColWidth
            )
        except PermissionError as e:
            messagebox.showerror(
                'Access is denied',
                str(e)
            )
        except Exception as e:
            messagebox.showerror(
                str(e.__class__.__name__),
                str(e)
            )
        
        # Setting a file system observer for this folder...
        observer = Observer()
        observer.schedule(
            self._fsHandler,
            folder,
            recursive=False
        )
        self._observers.append(observer)
        observer.start()


if (__name__ == '__main__'):
    dup_finder_win = DupFinder()
    dup_finder_win.mainloop()