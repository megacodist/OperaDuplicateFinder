# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from collections import namedtuple
from jinja2 import FileSystemLoader, Environment
import logging
import re
import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame
from typing import Any, Iterable

from utils import AppSettings


TitlePathPair = namedtuple(
    'TitlePathPair',
    'title, path')


class LicenseDialog(tk.Toplevel):
    def __init__(self, files: Iterable[TitlePathPair]) -> None:
        super().__init__()
        self.title(' & '.join(item.title for item in files))

        # Loading License Dialog (LD) settings...
        settings = self._ReadSettings()
        self.geometry(
            f'{settings["LD_WIDTH"]}x{settings["LD_HEIGHT"]}'
            + f'+{settings["LD_X"]}+{settings["LD_Y"]}')
        self.state(settings['LD_STATE'])

        # Making this dialog as modal...
        self.grab_set()
        self.transient()

        # Adding tabs...
        self.ntbk_lcns = ttk.Notebook(
            self)
        self.ntbk_lcns.pack(
            fill='both',
            expand=1)
        for titlePath in files:
            frm = ttk.Frame(
                self.ntbk_lcns)
            frm.pack(
                fill='both',
                expand=1)

            hscrllbr_lcns = ttk.Scrollbar(
                frm,
                orient='horizontal')
            vscrllbr_lcns = ttk.Scrollbar(
                frm,
                orient='vertical')
            txt_lcns = tk.Text(
                frm,
                wrap='none')
            hscrllbr_lcns.config(
                command=txt_lcns.xview)
            vscrllbr_lcns.config(
                command=txt_lcns.yview)
            txt_lcns.config(
                xscrollcommand=hscrllbr_lcns.set,
                yscrollcommand=vscrllbr_lcns.set)
            hscrllbr_lcns.pack(
                side='bottom',
                fill='x')
            vscrllbr_lcns.pack(
                side='right',
                fill='y')
            txt_lcns.pack(
                fill='both',
                side='top',
                expand=1)

            with open(titlePath.path, 'rt') as lcnsStream:
                txt_lcns.insert(
                    tk.END,
                    lcnsStream.readlines())

            self.ntbk_lcns.add(
                frm,
                text=titlePath.title)
            txt_lcns.config(state='disabled')

        # Binding events...
        self.protocol('WM_DELETE_WINDOW', self._OnClosing)

    def _ReadSettings(self) -> dict[str, Any]:
        # Considering License Dialog (LD) default settings...
        defaults = {
            'LD_WIDTH': 500,
            'LD_HEIGHT': 700,
            'LD_X': 200,
            'LD_Y': 200,
            'LD_STATE': 'normal',
        }
        return AppSettings().Read(defaults)

    def _OnClosing(self) -> None:
        settings = {}

        # Getting the geometry of the License Dialog (LD)...
        w_h_x_y = self.winfo_geometry()
        GEOMETRY_REGEX = r"""
            (?P<width>\d+)    # The width of the window
            x(?P<height>\d+)  # The height of the window
            \+(?P<x>\d+)      # The x-coordinate of the window
            \+(?P<y>\d+)      # The y-coordinate of the window"""
        match = re.search(
            GEOMETRY_REGEX,
            w_h_x_y,
            re.VERBOSE)
        if match:
            settings['LD_WIDTH'] = int(match.group('width'))
            settings['LD_HEIGHT'] = int(match.group('height'))
            settings['LD_X'] = int(match.group('x'))
            settings['LD_Y'] = int(match.group('y'))
        else:
            logging.error('Cannot get the geometry of License Dialog.')

        # Getting other License Dialog (LD) settings...
        settings['LD_STATE'] = self.state()

        AppSettings().Update(settings)
        self.destroy()


class ResultDialog(tk.Toplevel):
    def __init__(
            self,
            template_dir: list[str],
            template_name: str,
            context: dict[str, Any]
            ) -> None:

        super().__init__()
        self.title('Report')

        # Loading Result Dialog (RD) settings...
        settings = self._ReadSettings()
        self.geometry(
            f'{settings["RD_WIDTH"]}x{settings["RD_HEIGHT"]}'
            + f'+{settings["RD_X"]}+{settings["RD_Y"]}')
        self.state(settings['RD_STATE'])

        self._templateDir = template_dir
        self._templateName = template_name
        self._context = context

        #
        self.html_report = HtmlFrame(
            self,
            vertical_scrollbar=True,
            horizontal_scrollbar=True,
            messages_enabled=False)
        self.html_report.on_form_submit(self._OnChoiceSubmitted)
        self.html_report.pack(
            fill='both',
            expand=1)

        # Showing results...
        self._RenderResult()

    def _ReadSettings(self) -> dict[str, Any]:
        # Considering License Dialog (LD) default settings...
        defaults = {
            'RD_WIDTH': 500,
            'RD_HEIGHT': 700,
            'RD_X': 200,
            'RD_Y': 200,
            'RD_STATE': 'normal',
        }
        return AppSettings().Read(defaults)

    def _OnChoiceSubmitted(
            self,
            url: str,
            data: str,
            method: str
            ) -> None:
        # Processing user choice...
        print(url, data, method)

        # Updating application settings of Result Dialog (RD)...
        settings = {}
        # Getting the geometry of the Result Dialog (RD)...
        w_h_x_y = self.winfo_geometry()
        GEOMETRY_REGEX = r"""
            (?P<width>\d+)    # The width of the window
            x(?P<height>\d+)  # The height of the window
            \+(?P<x>\d+)      # The x-coordinate of the window
            \+(?P<y>\d+)      # The y-coordinate of the window"""
        match = re.search(
            GEOMETRY_REGEX,
            w_h_x_y,
            re.VERBOSE)
        if match:
            settings['RD_WIDTH'] = int(match.group('width'))
            settings['RD_HEIGHT'] = int(match.group('height'))
            settings['RD_X'] = int(match.group('x'))
            settings['RD_Y'] = int(match.group('y'))
        else:
            logging.error('Cannot get the geometry of Result Dialog.')
        # Getting other Result Dialog (RD) settings...
        settings['RD_STATE'] = self.state()
        # Updating settings...
        AppSettings().Update(settings)

        self.destroy()

    def _RenderResult(self) -> None:
        fsLoader = FileSystemLoader(searchpath=self._templateDir)
        env = Environment(loader=fsLoader)
        tmplt = env.get_template(name=self._templateName)
        result_ = tmplt.render(**self._context)

        self.html_report.load_html(
            html_source=result_,
            base_url=self._templateDir)
