import os
import subprocess
import sys
import time
import typing


def capture_cpp_stdin_output(stdin: typing.ByteString, filter_output: bool) -> typing.List[str]:
    """Send stdin to ``cpp -E`` and return the result as a list of strings.
    If ``filter_output`` is True than empty lines and lines starting with ``'#'`` are omitted."""
    try:
        cmds = [os.environ['CPP']]
    except KeyError:
        cmds = ['cpp']
    cmds.append('-E')
    sub_process = subprocess.run(cmds, capture_output=True, input=stdin)
    if sub_process.returncode:
        raise IOError(f'cpp returned error code {sp.returncode}. stderr: {sp.stderr}')
    lines = sub_process.stdout.decode().splitlines()
    if filter_output:
        ret = []
        for line in lines:
            if len(line) == 0 or line.startswith('#'):
                continue
            ret.append(line)
        return ret
    return lines


def main():
    stdin = b"""#define SPAM EGGS
#define EGGS SPAM
#define CHIPS SPAM
SPAM
EGGS
CHIPS
"""
    t_start = time.perf_counter()
    result = capture_cpp_stdin_output(stdin, True)
    print(' Output '.center(75, '-'))
    print('\n'.join(result))
    print(' Output DONE '.center(75, '-'))
    print(f'Time: {(time.perf_counter() - t_start) * 1000:0.3f} (ms)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
