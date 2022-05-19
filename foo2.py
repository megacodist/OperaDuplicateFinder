from threading import Thread
from msvcrt import getwche


num: int


def Increment(inc: int, count: int):
    global num
    for i in range(count):
        num += inc


def Decrement(dec: int, count: int):
    global num
    for i in range(count):
        num -= dec


if __name__ == '__main__':
    count = 2_000
    iterations = 3_000
    results = set()
    for i in range(1, iterations + 1):
        num = 0
        thrd1 = Thread(
            target=Increment,
            args=(2, count))
        thrd2 = Thread(
            target=Decrement,
            args=(1, count))
        thrd1.start()
        thrd2.start()
        thrd1.join()
        thrd2.join()
        results.add(num)

        print(' ' * 79, end='\r', flush=True)
        print(
            f'Iteration {i:>4d} of {iterations}. '
            + f'Number of results: {len(results)}',
            end='\r',
            flush=True)

    print()
    print(results)
    getwche()
