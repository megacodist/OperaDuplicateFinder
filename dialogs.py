# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import namedtuple
from jinja2 import FileSystemLoader, Environment
import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame
from typing import Any, Iterable


TitlePathPair = namedtuple(
    'TitlePathPair',
    'title, path'
)


class LicenseDialog(tk.Toplevel):
    def __init__(self, files: Iterable[TitlePathPair]) -> None:
        super().__init__()
        self.geometry('300x400')
        self.title(
            ' & '.join(item.title for item in files)
        )

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


class ResultDialog(tk.Toplevel):
    def __init__(
        self,
        template_dir: list[str],
        template_name: str,
        context: dict[str, Any]
    ) -> None:
        super().__init__()
        self.title('Report')


        self._templateDir = template_dir
        self._templateName = template_name
        self._context=context

        #
        self.html_report = HtmlFrame(
            self,
            vertical_scrollbar=True,
            horizontal_scrollbar=True,
            messages_enabled=False
        )
        #self.html_report.on_link_click(self._OnChoiceSubmitted)
        self.html_report.on_form_submit(self._OnChoiceSubmitted)
        self.html_report.pack(
            fill='both',
            expand=1
        )

        self._RenderResult()
    
    def _OnChoiceSubmitted(
        self,
        url: str,
        data: str,
        method: str
    ):
        print(url, data, method)
        self.destroy()
    
    def _RenderResult(self) -> None:
        fsLoader = FileSystemLoader(searchpath=self._templateDir)
        env = Environment(loader=fsLoader)
        tmplt = env.get_template(name=self._templateName)
        result_ = tmplt.render(**self._context)

        self.html_report.load_html(
            html_source=result_,
            base_url=self._templateDir
        )