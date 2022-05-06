# 2022/5/5  20:14  liujiaqi

def iterprint(iterable, width, n=2, idx=False):
    if n < 1:
        n = 1
    interval = (width - 3) // n
    s = '| '
    c = 0
    for i, v in enumerate(iterable):
        prefix = str(i + 1) + '.'
        if not idx:
            prefix = ''
        s += f'{prefix} {v}'.ljust(interval)
        if c != n - 1:
            c = (c + 1) % n
            continue
        c = 0
        print(s.ljust(width - 1) + '|')
        s = '| '
    if not c == 0:
        print(s.ljust(width - 1) + '|')


if __name__ == '__main__':
    a = ['aioieg', 'fasdweg', 'asdgasd', '892829josljl']
    iterprint(a, 90, 1, True)
