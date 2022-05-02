# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import namedtuple
import tkinter as tk
from tkinter import ttk
from typing import Iterable


TitlePathPair = namedtuple(
    'TitlePathPair',
    'title, path'
)


class LicenseDialog(tk.Toplevel):
    def __init__(self, files: Iterable[TitlePathPair]) -> None:
        super().__init__()
        self.geometry('300x400')

        self.ntbk_lcns = ttk.Notebook(
            self
        )
        self.ntbk_lcns.pack(
            fill='both',
            expand=1
        )

        for titlePath in files:
            frm = ttk.Frame(
                self.ntbk_lcns
            )
            frm.pack(
                fill='both',
                expand=1
            )

            hscrllbr_lcns = ttk.Scrollbar(
                frm,
                orient='horizontal'
            )
            vscrllbr_lcns = ttk.Scrollbar(
                frm,
                orient='vertical'
            )
            txt_lcns = tk.Text(
                frm,
                wrap='none',
            )
            hscrllbr_lcns.config(
                command=txt_lcns.xview
            )
            vscrllbr_lcns.config(
                command=txt_lcns.yview
            )
            txt_lcns.config(
                xscrollcommand=hscrllbr_lcns.set,
                yscrollcommand=vscrllbr_lcns.set
            )
            hscrllbr_lcns.pack(
                side='bottom',
                fill='x'
            )
            vscrllbr_lcns.pack(
                side='right',
                fill='y'
            )
            txt_lcns.pack(
                fill='both',
                side='top',
                expand=1
            )

            with open(titlePath.path, 'rt') as lcnsStream:
                txt_lcns.insert(
                    tk.END,
                    lcnsStream.readlines()
                )
            
            self.ntbk_lcns.add(
                frm,
                text=titlePath.title
            )
            txt_lcns.config(state='disabled')