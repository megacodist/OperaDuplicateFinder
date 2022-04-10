from pathlib import Path
import PIL.Image, PIL.ImageTk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from typing import Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class _DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, dupFinder: Any) -> None:
        super().__init__()
        self._dupFinder = dupFinder

    def on_created(self, event):
        itemLabel = Path(event.src_path).name
        self._dupFinder.lstbx_items.insert(tk.END, itemLabel)

    def on_deleted(self, event):
        itemLabel = Path(event.src_path).name
        itemIndex = self._dupFinder.lstbx_items.get(0, tk.END).index(itemLabel)
        self._dupFinder.lstbx_items.delete(itemIndex)

    def on_moved(self, event):
        print('moved')


class DupFinder(tk.Tk):
    def __init__(self, dir=None) -> None:
        super().__init__()

        # Initializing the window...
        self.title('Duplicate remover')

        # 
        self.frm_toolbar = ttk.Frame(
            self
        )
        self.frm_toolbar.pack(
            fill='x',
            padx=2,
            pady=(2, 1,)
        )

        # Loading 'open.png'...
        self.img_path = Path(__file__).resolve().parent
        self.img_path = self.img_path / 'res/open.png'
        self.img_path = PIL.Image.open(self.img_path)
        self.img_path = self.img_path.resize(size=(20, 20,))
        self.img_path = PIL.ImageTk.PhotoImage(image=self.img_path)
        #
        self.btn_path = ttk.Button(
            self.frm_toolbar,
            image=self.img_path,
            command=self._BrowseDir
        )
        self.btn_path.pack(
            side='right'
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
        self.lstbx_items = tk.Listbox(
            self.frm_items,
            xscrollcommand=self.hscrlbr_items.set,
            yscrollcommand=self.vscrlbr_items.set
        )
        self.vscrlbr_items.config(
            command=self.lstbx_items.yview
        )
        self.hscrlbr_items.config(
            command=self.lstbx_items.xview
        )
        self.hscrlbr_items.pack(
            side='bottom',
            fill='x'
        )
        self.vscrlbr_items.pack(
            side='right',
            fill='y'
        )
        self.lstbx_items.pack(
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
            self.lstbx_items.delete(0, 'end')

    def _EnumFiles(self):
        # First of all emptying the list...
        self.lstbx_items.delete(0, 'end')

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
            for item in items:
                self.lstbx_items.insert(tk.END, item.name)
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