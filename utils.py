# 2022/5/5  20:14  liujiaqi
import platform
import os


def ClearCLI():
    system = platform.system()
    if system == u'Windows':
        os.system('cls')
    else:
        os.system('clear')


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


#
'''def check_before_run(required_files):
    """Checks if required files exist before going deeper.
    Args:
        required_files (str or list): string file name(s).
    """
    if isinstance(required_files, str):
        required_files = [required_files]

    for fpath in required_files:
        if not os.path.exists(fpath):
            raise RuntimeError('"{}" is not found'.format(fpath))'''


if __name__ == '__main__':
    a = ['aioieg', 'fasdweg', 'asdgasd', '892829josljl']
    iterprint(a, 90, 1, True)
