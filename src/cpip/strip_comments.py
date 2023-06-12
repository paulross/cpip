import argparse
import io
import logging
import os
import subprocess
import sys
import time
import typing

from cpip.core import ItuToTokens
from cpip.core import PpTokeniser
from cpip.util import DirWalk

__version__ = '0.1.0'
__date__ = '2023-06-12'

logger = logging.getLogger(__file__)


def translate_phases_123_file(input_file: typing.TextIO, placeholder_comment: str) -> bytes:
    ith = ItuToTokens.ItuToTokens(input_file)
    ith.translatePhases123()
    words = []
    for text, pp_type in ith.multiPassString.genWords():
        if pp_type not in PpTokeniser.COMMENT_TYPES:
            words.append(bytes(text, 'ascii'))
        elif placeholder_comment:
            words.append(bytes(placeholder_comment, 'ascii'))
    return b''.join(words)


def translate_phases_123_path(input_str: str, placeholder_comment: str) -> bytes:
    logger.info('Reading %s', input_str)
    with open(input_str) as file:
        return translate_phases_123_file(file, placeholder_comment)


def write_bytes(out_path: str, out_bytes: bytes) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as output_file:
        output_file.write(out_bytes)


def process_dir_to_output(in_dir: str, out_dir: str, glob_match: str, recursive: bool, clang_format: bool,
                          prefix_bytes: bytes, placeholder_comment: str) -> int:
    """Process all the files in a directory. Returns a count of the files."""
    assert os.path.isdir(in_dir)
    logger.info('Processing %s to %s', in_dir, out_dir)
    time_start = time.process_time()
    count = 0
    path_out = os.path.abspath(out_dir) if out_dir else None
    for t in DirWalk.dirWalk(in_dir, path_out, glob_match, recursive, bigFirst=False):
        if out_dir:
            output_bytes = prefix_bytes + translate_phases_123_path(t.filePathIn, placeholder_comment)
            if clang_format:
                output_bytes = run_clang_format(output_bytes)
            logger.info('Writing %s', t.filePathOut)
            write_bytes(t.filePathOut, output_bytes)
        else:
            output_bytes = prefix_bytes + translate_phases_123_path(t, placeholder_comment)
            if clang_format:
                output_bytes = run_clang_format(output_bytes)
            print(output_bytes.decode('ascii'))
        count += 1
    logger.info('Done. Time %.3f', time.process_time() - time_start)
    return count


def run_clang_format(bytes_in: bytes, **kwargs) -> bytes:
    # bytes_in = pack_lines(bytes_in)
    args = ['clang-format', ]
    for k in kwargs:
        args.append(f'{k}={kwargs[k]}')
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    result = proc.communicate(input=bytes_in)[0]
    if proc.returncode != 0:
        raise IOError(f'clang-format failed with return code {proc.returncode}')
    # print(f'TRACE: {type(result)}')
    return result


def pack_lines(bytes_in: bytes) -> bytes:
    while bytes_in.find(b'\n\n') != -1:
        bytes_in = bytes_in.replace(b'\n\n', b'\n')
    return bytes_in


def main():
    program_version = "v%s" % __version__
    program_shortdesc = 'strip_comments.py - Strip comments from a file or the files in a directory.'
    program_license = """%s
      Created by Paul Ross on %s.
      Copyright 2008-2017. All rights reserved.
      Version: %s
      Licensed under GPL 2.0
    USAGE
    """ % (program_shortdesc, str(__date__), program_version)
    parser = argparse.ArgumentParser(description=program_license,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--clang-format", action="store_true", dest="clang_format", default=False,
                        help="Run clang-format on the result. [default: %(default)s]")
    parser.add_argument("--placeholder-comment", type=str, default='',
                        help="Replace a comment with a placeholder comment, for example --placeholder-comment='/* */'."
                             " [default: %(default)s]")
    parser.add_argument("-g", "--glob", action='append', default=[],
                        help="Pattern match to use when processing directories. [default: %(default)s] i.e. every file.")
    parser.add_argument(
        "-l", "--loglevel",
        type=int,
        dest="loglevel",
        default=20,
        help="Log Level (debug=10, info=20, warning=30, error=40, critical=50)" \
             " [default: %(default)s]"
    )
    parser.add_argument("-r", "--recursive", action="store_true", dest="recursive",
                        default=False,
                        help="Recursively process directories. [default: %(default)s]")
    parser.add_argument("-o", "--output",
                        type=str,
                        dest="output",
                        default="",
                        help="Output directory. [default: %(default)s]")
    parser.add_argument("--prefix",
                        type=str,
                        default="",
                        help="Insert this file at the beginning of each output file. [default: %(default)s]")
    parser.add_argument(dest="path", nargs=1, help="Path to source file or directory.")
    args = parser.parse_args()
    clk_start = time.perf_counter()
    in_path = args.path[0]
    # Initialise logging etc.
    logging.basicConfig(level=args.loglevel,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        # datefmt='%y-%m-%d % %H:%M:%S',
                        stream=sys.stdout)
    if args.prefix:
        with open(os.path.expanduser(args.prefix), 'rb') as prefix_file:
            prefix_bytes = prefix_file.read()
    else:
        prefix_bytes = b''
    count_file = 0
    if os.path.isfile(in_path):
        # Single file
        result = prefix_bytes + translate_phases_123_path(sys.argv[1], args.placeholder_comment)
        if args.clang_format:
            # result = pack_lines(result)
            result = run_clang_format(result)
        if args.output == '':
            print(result.decode('ascii'))
        else:
            file_path_out = os.path.abspath(os.path.join(args.output, os.path.basename(in_path)))
            write_bytes(file_path_out, result)
        count_file = 1
    elif os.path.isdir(in_path):
        count_file = process_dir_to_output(in_path, args.output, args.glob, args.recursive, args.clang_format,
                                           prefix_bytes, args.placeholder_comment)
    else:
        logger.error('Can not understand path %s', in_path)
    print(f'Processed {count_file} files in {time.perf_counter() - clk_start:.3} (s)')
    print('Bye, bye!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
