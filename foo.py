from msvcrt import getwche
from PIL.ImageFont import FreeTypeFont
from tkinter import ttk
from tkinter.font import Font

from megacodist.text import GetCommonAffix


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
    
    import sys
    import time
    mmm = 'abcdefghijklmnopqrstuvwxyz'
    while True:
        slice_ = slice(None, 200, 2)
        print(slice_.start)
        print(slice_.stop)
        print(slice_.step)
        print(slice_.indices(len(mmm)))

        time.sleep(3)
        sys.exit(0)

    n = int(input('Enter number of strings: '))
    texts = []
    for i in range(1, n + 1):
        string = input(f'Enter {i}th string: ')
        texts.append(string)
    
    slice_ = commonAfix(*texts, is_posfix=True)
    print(slice_)
    print(texts[0][slice_], flush=True)
    getwche()