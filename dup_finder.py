# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
from pathlib import Path
import re
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from typing import Any

import PIL.Image, PIL.ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from dialogs import TitlePathPair, LicenseDialog, ResultDialog
from duplicate_util import NameDirPair, ReportDuplicates
from TreeviewFS import TreeviewFS


class DupFinder(tk.Tk):    
    def __init__(
        self,
        cwd: Path,
        settings: dict[str, Any]
    ) -> None:
        super().__init__()

        # Initializing the window...
        self.title('Duplicate remover')
        self.geometry(f'{settings["width"]}x{settings["height"]}+{settings["x"]}+{settings["y"]}')
        self.theme = ttk.Style()
        self.theme.theme_use('clam')

        # Defining of required variables...
        self._cwd = cwd
        self._settings = settings
        self._dirs : list[str] = []
        self._columnMinWidth : int = 300 - 25
        self._fsHandler = None
        self._observers : list[Observer] = []

        # Defining of resources...
        self.img_browse = None
        self.img_folder = None
        self.img_file = None
        self.img_unknown = None
        self.img_duplicate = None
        self.img_license = None

        # Defining of GUI widgets...
        self.frm_toolbar = None
        self.frm_files = None
        self.frm_fsPath = None
        self.btn_browse = None
        self.btn_duplicate = None
        self.btn_license = None
        self.vscrlbr_files = None
        self.hscrlbr_files = None
        self.trvw_files = None

        self._LoadResources()
        self._InitializeGUI()

        # Binding events...
        #self.wait_visibility()
        self.trvw_files.bind('<<TreeviewSelect>>', self._OnItemSelectionChanged)
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
    
    def _LoadResources(self) -> None:
        '''Loads resources using the the GUI.'''

        # Loading images...
        # Loading 'browse.png'...
        self.img_browse = self._cwd / 'res/browse.png'
        self.img_browse = PIL.Image.open(self.img_browse)
        self.img_browse = self.img_browse.resize(size=(24, 24,))
        self.img_browse = PIL.ImageTk.PhotoImage(image=self.img_browse)
        # Loading 'folder.png'...
        self.img_folder = self._cwd / 'res/folder.png'
        self.img_folder = PIL.Image.open(self.img_folder)
        self.img_folder = self.img_folder.resize(size=(24, 24,))
        self.img_folder = PIL.ImageTk.PhotoImage(image=self.img_folder)
        # Loading 'file.png'...
        self.img_file = self._cwd / 'res/file.png'
        self.img_file = PIL.Image.open(self.img_file)
        self.img_file = self.img_file.resize(size=(24, 24,))
        self.img_file = PIL.ImageTk.PhotoImage(image=self.img_file)
        # Loading 'unknown.png'...
        self.img_unknown = self._cwd / 'res/unknown.png'
        self.img_unknown = PIL.Image.open(self.img_unknown)
        self.img_unknown = self.img_unknown.resize(size=(24, 24,))
        self.img_unknown = PIL.ImageTk.PhotoImage(image=self.img_unknown)
        # Loading 'duplicate.png'...
        self.img_duplicate = self._cwd / 'res/duplicate.png'
        self.img_duplicate = PIL.Image.open(self.img_duplicate)
        self.img_duplicate = self.img_duplicate.resize(size=(24, 24,))
        self.img_duplicate = PIL.ImageTk.PhotoImage(image=self.img_duplicate)
        # Loading 'license.png'...
        self.img_license = self._cwd / 'res/license.png'
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
            command=self._FindDuplicates
        )
        self.btn_duplicate.pack(
            side=tk.LEFT
        )

        #
        self.btn_license = ttk.Button(
            master=self.frm_toolbar,
            image=self.img_license,
            command=self._ShowLicense
        )
        self.btn_license.pack(
            side=tk.LEFT
        )

        # File system path frame --------------------------------
        self.frm_fsPath = ttk.Frame(
            self
        )
        self.frm_fsPath.pack(
            side='bottom',
            fill='x'
        )

        #
        self.entry_fsPath = tk.Text(
            self.frm_fsPath,
            height=1,
            state='disabled'
        )
        self.entry_fsPath.pack(
            fill='x'
        )

        # Folders & files frame -----------------------------------
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
        self.trvw_files = TreeviewFS(
            self.frm_files,
            img_folder=self.img_folder,
            img_file=self.img_file,
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
            text='Added folders',
            anchor=tk.W
        )
        # Configuring the default column...
        self.trvw_files.column(
            '#0',
            width=self._columnMinWidth,
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
        
    def _BrowseDir(self):
        folder = filedialog.askdirectory(
            initialdir=self._settings['lastDir'],
            title='Browse for a folder that contains duplicate files'
        )
        if folder:
            self._settings['lastDir'] = folder
            # Asking for subfolders...
            answer = messagebox.askquestion(
                'Subfolders',
                'Do you want to include subfolders?'
            )
            subfolders = False
            if answer.lower() == 'yes':
                subfolders = True
            
            try:                
                self.trvw_files.AddFolder(
                    folder,
                    subfolders=subfolders
                )
            except Exception as err:
                if len(err.args):
                    msg = '\n'.join(err.args)
                messagebox.showerror(
                    title='Error',
                    message=msg
                )
    
    def _OnItemSelectionChanged(self, event:tk.Event):
        # Checking selected item...
        selectedItemID = self.trvw_files.selection()
        if not selectedItemID:
            # This event has been fired for deselection, so deleting the fsPath...
            self.entry_fsPath['state'] = tk.NORMAL
            self.entry_fsPath.delete('1.0', tk.END)
            self.entry_fsPath['state'] = tk.DISABLED
            return

        # Getting selected item...
        selectedItemID = selectedItemID[0]

        # 
        self.entry_fsPath['state'] = tk.NORMAL
        self.entry_fsPath.delete('1.0', tk.END)
        self.entry_fsPath.insert(
            '1.0',
            self.trvw_files.GetFullPath(selectedItemID)
        )
        self.entry_fsPath['state'] = tk.DISABLED
    
    def on_closing(self) -> dict[str, Any]:
        w_h_x_y = self.winfo_geometry()
        match = re.search(
            r"""
                (?P<width>\d+)    # The width of the window
                x(?P<height>\d+)  # The height of the window
                \+(?P<x>\d+)       # The x-coordinate of the window
                \+(?P<y>\d+)       # The y-coordinate of the window""",
            w_h_x_y,
            re.VERBOSE
        )
        if match:
            self._settings['width'] = int(match.group('width'))
            self._settings['height'] = int(match.group('height'))
            self._settings['x'] = int(match.group('x'))
            self._settings['y'] = int(match.group('y'))
        else:
            logging.error('Cannot get the geometry of the window.')
        self.destroy()
    
    def GetSettings(self) -> dict[str, Any]:
        return self._settings
    
    def _ShowLicense(self) -> None:
        titlePathPairs = []
        titlePathPairs.append(
            TitlePathPair(
                'Read me',
                self._cwd / 'README.md'
            )
        )
        titlePathPairs.append(
            TitlePathPair(
                'License',
                self._cwd / 'License'
            )
        )

        lcnsDlg = LicenseDialog(titlePathPairs)
        lcnsDlg.mainloop()
    
    def _FindDuplicates(self) -> None:
        filesList = self.trvw_files.GetFileDirList()
        allDuplicates, allSimilars = ReportDuplicates(filesList)
        context = {
            'allDuplicates': allDuplicates,
            'allSimilars': allSimilars
        }

        resultDlg = ResultDialog(
            template_dir=str(self._cwd / 'res'),
            template_name='report.html',
            context=context
        )
        resultDlg.mainloop()