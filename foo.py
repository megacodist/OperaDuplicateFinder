from msvcrt import getwche
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
        CollisionPolicy.end,
        key=lambda item: item.root
    )
    print(
        ol.index
    )