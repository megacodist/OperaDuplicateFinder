from datetime import datetime
from msvcrt import getwche
from queue import Queue
from requests import Session
import signal
from threading import Thread, Lock
from typing import Iterable


def Show(sig, frame) -> None:
    print('Foo')


def main() -> None:
    # Getting a piece of code snippet from user...
    # Terminated with two empty line...
    print('Enter some code:')
    text_ = []
    while True:
        input_ = input()
        if ((not input_) and text_ and (not text_[-1])):
            break
        text_.append(input_)
    text_ = '\n'.join(text_)

    print(text_)
    result_ = eval(compile(text_, text_, 'exec'))
    print(result_)

    print('Press nay key to exit: ', sep='', end='', flush=True)
    getwche()


def LoadSite(site: str, session: Session) -> str | None:
    try:
        resp = session.get(url=site)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass


def LoadSite_thrd(
        site: str,
        session: Session,
        q: Queue,
        ) -> str | None:

    try:
        resp = session.get(url=site)
        if resp.status_code == 200:
            resp = resp.text
    except Exception as err:
        resp = str(err)

    q.put(resp, block=True)


def DoNaively(sites: Iterable[str]):
    idx = 1
    with Session() as session:
        for site in sites:
            resp = LoadSite(site, session)
            print(f'{idx:2d}', '=' * 50)
            print(resp)
            idx += 1


def DoUsingThreads(sites: Iterable[str]):
    q = Queue(80)
    allThrds = []
    with Session() as session:
        for site in sites:
            thrd = Thread(
                target=LoadSite_thrd,
                kwargs={
                    'site': site,
                    'session': session,
                    'q': q})
            thrd.start()
            allThrds.append(thrd)

    for thrd in allThrds:
        thrd.join()

    while not q.empty():
        print(q.get())


if __name__ == '__main__':
    signal.signal(signal.SIGABRT, Show)

    sites = [
        'https://www.github.com/',
        'https://digikala.ir/'
    ] * 15

    startTime = datetime.now()
    print('Start at:', startTime.strftime('%A %B %d, %Y, %H:%M:%S'))
    #DoNaively(sites)
    DoUsingThreads(sites)
    finishedTime = datetime.now()
    print('Finished at:', finishedTime.strftime('%A %B %D, %Y, %H:%M:%S'))
    duration = finishedTime - startTime
    print('Duration:', str(duration))
    getwche()
