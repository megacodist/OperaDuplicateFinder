from collections import namedtuple
import tkinter as tk
from tkinter import ttk


TitlePathPair = namedtuple(
    'TitlePathPair',
    'title, path'
)


class LicenseDialog(tk.Tk):
    def __init__(self, *files: TitlePathPair) -> None:
        super().__init__()

        self._InitializeGUI()
    
    def _InitializeGUI(self) -> None:
        pass