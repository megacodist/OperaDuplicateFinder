from msvcrt import getwche
from pathlib import Path
from tkinter import ttk
from tkinter.font import Font

from megacodist.collections import OrderedList, CollisionPolicy


def _GetMemebers(typeObj: type, members: list[str]) -> None:
    for member in dir(typeObj):
        if member not in members:
            members.append(member)
    
    for type_ in typeObj.__bases__:
        _GetMemebers(type_, members)

if __name__ == '__main__':
    '''typeObj = ttk.Treeview
    members = []
    _GetMemebers(typeObj, members)
    members.sort()

    for member in members:
        print(member)
        print(help(getattr(typeObj, member)))'''
    
    

    ol = OrderedList(
        key=lambda item: (item.stem.lower(), item.name.lower())
    )
    _MODULE_DIR = Path(__file__).resolve().parent
    for item in _MODULE_DIR.iterdir():
        if item.is_file():
            ol.Put(item)
    
    for item in ol:
        print(item.name)