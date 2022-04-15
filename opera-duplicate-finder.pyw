from enum import IntEnum
from pathlib import Path
import PIL.Image, PIL.ImageTk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from typing import Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from megacodist.text import GetStringDimensions


class ItemType(IntEnum):
    unknown = 0
    folder = 1
    file = 2


class _DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, dupFinder: Any) -> None:
        super().__init__()
        self._dupFinder = dupFinder

    def on_created(self, event):
        itemLabel = Path(event.src_path).name
        self._dupFinder.trvw_items.insert(tk.END, itemLabel)

    def on_deleted(self, event):
        itemLabel = Path(event.src_path).name
        itemIndex = self._dupFinder.trvw_items.get(0, tk.END).index(itemLabel)
        self._dupFinder.trvw_items.delete(itemIndex)

    def on_moved(self, event):
        print('moved')


class DupFinder(tk.Tk):
    def __init__(self, dir=None) -> None:
        super().__init__()

        # Initializing the window...
        self.title('Duplicate remover')
        self.theme = ttk.Style()
        self.theme.theme_use('clam')

        # 
        self.frm_toolbar = ttk.Frame(
            self
        )
        self.frm_toolbar.pack(
            fill='x',
            padx=2,
            pady=(2, 1,)
        )

        # Loading images...
        # Loading 'browse.png'...
        self.img_browse = Path(__file__).resolve().parent
        self.img_browse = self.img_browse / 'res/browse.png'
        self.img_browse = PIL.Image.open(self.img_browse)
        self.img_browse = self.img_browse.resize(size=(20, 20,))
        self.img_browse = PIL.ImageTk.PhotoImage(image=self.img_browse)
        # Loading 'folder.png'...
        self.img_folder = Path(__file__).resolve().parent
        self.img_folder = self.img_folder / 'res/folder.png'
        self.img_folder = PIL.Image.open(self.img_folder)
        self.img_folder = self.img_folder.resize(size=(20, 20,))
        self.img_folder = PIL.ImageTk.PhotoImage(image=self.img_folder)
        # Loading 'file.png'...
        self.img_file = Path(__file__).resolve().parent
        self.img_file = self.img_file / 'res/file.png'
        self.img_file = PIL.Image.open(self.img_file)
        self.img_file = self.img_file.resize(size=(20, 20,))
        self.img_file = PIL.ImageTk.PhotoImage(image=self.img_file)
        # Loading 'unknown.png'...
        self.img_unknown = Path(__file__).resolve().parent
        self.img_unknown = self.img_unknown / 'res/unknown.png'
        self.img_unknown = PIL.Image.open(self.img_unknown)
        self.img_unknown = self.img_unknown.resize(size=(20, 20,))
        self.img_unknown = PIL.ImageTk.PhotoImage(image=self.img_unknown)

        #
        self.btn_path = ttk.Button(
            self.frm_toolbar,
            image=self.img_browse,
            command=self._BrowseDir
        )
        self.btn_path.pack(
            side='left'
        )

        #
        self.strvar_path = tk.StringVar(self.frm_toolbar)
        self.entry_path = ttk.Entry(
            self.frm_toolbar,
            textvariable=self.strvar_path
        )
        self.entry_path.pack(
            fill='both',
            pady=4,
            padx=4
        )

        #
        self.frm_items = ttk.Frame(
            self
        )
        self.frm_items.pack(
            fill='both',
            expand=1,
            padx=2,
            pady=(1, 2,)
        )

        #
        self.vscrlbr_items = ttk.Scrollbar(
            self.frm_items,
            orient='vertical'
        )
        self.hscrlbr_items = ttk.Scrollbar(
            self.frm_items,
            orient='horizontal'
        )
        self.trvw_items = ttk.Treeview(
            self.frm_items,
            show='tree headings',
            xscrollcommand=self.hscrlbr_items.set,
            yscrollcommand=self.vscrlbr_items.set
        )
        self.vscrlbr_items.config(
            command=self.trvw_items.yview
        )
        self.hscrlbr_items.config(
            command=self.trvw_items.xview
        )
        # Configuring the default heading & column...
        self.trvw_items.heading(
            '#0',
            text='Name',
            anchor=tk.W
        )
        self.trvw_items.column(
            '#0',
            width=200,
            stretch=False,
            anchor=tk.W
        )
        self.hscrlbr_items.pack(
            side='bottom',
            fill='x'
        )
        self.vscrlbr_items.pack(
            side='right',
            fill='y'
        )
        self.trvw_items.pack(
            fill='both',
            expand=1,
            padx=3,
            pady=3
        )

        # Binding events...
        self.wait_visibility()
        self.strvar_path.trace('w', self._OnDirChanged)

        # Initializing path...
        self._fsHandler = _DirectoryEventHandler(self)
        if dir and isinstance(dir, str):
            self.strvar_path.set(dir)
        else:
            self.strvar_path.set(Path().cwd())
        
    def _BrowseDir(self):
        folder = filedialog.askdirectory(initialdir=self.strvar_path.get())
        if folder:
            self.strvar_path.set(folder)
    
    def _OnDirChanged(self, *_):
        folder = Path(self.strvar_path.get())
        if folder.exists():
            # Folder exists, first chaning color to green...
            self.entry_path.config(foreground='green')
            # Then enumerating files...
            self._EnumFiles()
        else:
            # Folder DOES NOT exist, first chaning color to red...
            self.entry_path.config(foreground='red')
            # Then emptying the list...
            self.trvw_items.delete(*self.trvw_items.get_children())

    def _EnumFiles(self):
        # First of all emptying the list...
        self.trvw_items.delete(*self.trvw_items.get_children())

        # Second of all populating the list with files...
        currentDir = Path(self.strvar_path.get()).resolve()
        try:
            # Retreiving all items in the folder...
            items = []
            for item in currentDir.iterdir():
                items.append(item)
            # Sorting items:
            #   folders at the top
            #   files in a way that XXXX.X comes before XXXX (1).X, XXXX (2).X
            items.sort(
                key=lambda fsItem : (
                    0 if fsItem.is_dir() else 1,
                    fsItem.stem
                )
            )
            # Adding the items to the listbox...
            maxWidth = 100
            from tkinter.font import Font
            font_ = Font(
                name='Times New Roman',
                size=10
            )

            parentNode = self.trvw_items.insert(
                '',
                index=tk.END,
                text=item.parent,
                image=self.img_folder,
                open=True
            )
            for item in items:
                if item.is_dir():
                    itemType = ItemType.folder
                    itemImage = self.img_folder
                elif item.is_file():
                    itemType = ItemType.file
                    itemImage = self.img_file
                else:
                    itemType = ItemType.unknown
                    itemImage = self.img_unknown
                
                itemWidth = font_.measure(item.name)
                if itemWidth > maxWidth:
                    maxWidth = itemWidth
                
                self.trvw_items.insert(
                    parent=parentNode,
                    index=tk.END,
                    text=item.name,
                    image=itemImage,
                    values=(
                        itemType,
                    )
                )
            
            self.trvw_items.column(
                '#0',
                width=maxWidth+30
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
        
        self._observer = Observer()
        self._observer.schedule(
            self._fsHandler,
            self.strvar_path.get(),
            recursive=True
        )
        self._observer.start()


if (__name__ == '__main__'):
    dup_finder_win = DupFinder()
    dup_finder_win.mainloop()