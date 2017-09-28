#!/usr/bin/env python
# CPIP is a C/C++ Preprocessor implemented in Python.
# Copyright (C) 2008-2017 Paul Ross
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Paul Ross: apaulross@gmail.com
"""
DupeRelink.py -- Searches for HTML files that are the same, writes a single
file into a common area and deletes all the others. Then re-links all the
remaining HTML files that linked to the original files to link to the file
in the common area. This is a space saving optimisation after CPIPMain.py
has processed a directory of source files.
"""
import argparse
import collections
import fnmatch
import hashlib
import logging
import os
import shutil
import sys
import time

from cpip import TokenCss

__author__ = 'Paul Ross'
__date__ = '2017-09-26'
__version__ = '0.9.5'
__rights__ = 'Copyright (c) 2017 Paul Ross'

SUB_DIR_FOR_COMMON_FILES = '_common_html'
FILE_GLOB = '*.html'
LINK_FORMAT_STR = '<a href="{:s}'


def _get_hash_result(dir_path, file_glob):
    """Returns a dict of {hash : [file_path, ...], ...} from a root
    directory."""
    hash_result = collections.defaultdict(list)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if fnmatch.fnmatch(file, file_glob):
                fpath = os.path.join(root, file)
                with open(fpath, 'rb') as fobj:
                    hsh = hashlib.md5(fobj.read()).hexdigest()
                    hash_result[hsh].append(fpath)
    return hash_result


def _prune_hash_result(hash_result):
    """Prunes a dict of {hash : [file_path, ...], ...} to just those entries
    that have >1 file_path."""
    keys = []
    for k in hash_result:
        if len(hash_result[k]) == 1:
            keys.append(k)
    for k in keys:
        del hash_result[k]


def _replace_in_file(fpath, text_find, text_repl, nervous_mode, len_root_dir):
    """Reads the contents of the file at fpath, replaces text_from with
    text_repl and writes it back out to the same fpath."""
    if nervous_mode:
        logging.info(
            'Would replace links in "{:s}" swap: "{:s}" for: "{:s}"'.format(
                fpath[len_root_dir:], text_find, text_repl
            )
        )
    else:
        logging.debug(
            'Replacing links in "{:s}" swap: "{:s}" for: "{:s}"'.format(
                fpath[len_root_dir:], text_find, text_repl
            )
        )
        with open(fpath, 'r') as fobj:
            content = fobj.read()
        with open(fpath, 'w') as fobj:
            fobj.write(content.replace(text_find, text_repl))


def _prepare_to_process(root_dir, file_glob):
    """Create a dict {hash : [file_paths, ...], ...} for duplicated files"""
    logging.info(' Searching '.center(75, "="))
    hash_result = _get_hash_result(root_dir, file_glob)
    logging.info(
        'Hash result: hashes={:d}, files={:d}'.format(
            len(hash_result),
            sum([len(v) for v in hash_result.values()])
        )
    )
    _prune_hash_result(hash_result)
    logging.info(
        'Hash result: hashes={:d}, duplicate files={:d}'.format(
            len(hash_result),
            sum([len(v) for v in hash_result.values()])
        )
    )
    logging.info(' DONE Searching '.center(75, "="))
    return hash_result


def _copy_delete_duplicates_fix_links(hash_result,
                                      common_dir,
                                      nervous_mode,
                                      len_root_dir):
    """Copy a single file that is duplicated to the common area, rewrite the
    links in that copy to the original location then delete all duplicates."""
    count_deleted = 0
    count_bytes_saved = 0
    # Copy one file and delete all others
    logging.info(' Copying and deleting '.center(75, "="))
    for k, v in hash_result.items():
        assert len(v) > 1, '_pruneHashResult(hash_result) not called or failed.'
        # Copy one file
        copy_from = v[0]
        copy_to = os.path.join(common_dir, os.path.basename(v[0]))
        if nervous_mode:
            logging.info(
                'Would copy "{:s}" to "{:s}"'.format(
                    copy_from[len_root_dir:], copy_to[len_root_dir:]
                )
            )
        else:
            logging.debug(
                'Copying "{:s}" to "{:s}"'.format(
                    copy_from[len_root_dir:], copy_to[len_root_dir:]
                )
            )
            shutil.copy(copy_from, copy_to)
        count_bytes_saved += os.stat(v[0]).st_size * (len(v) - 1)
        # Need to rewrite the links in the copied file back to the directory
        # that we copied from.
        # Change:
        # <a href="macros_noref.html#_UHlfUFlUSE9OX0hfMA__">
        # To:
        # <a href="../includes/noddy.c/macros_noref.html#_UHlfUFlUSE9OX0hfMA__">
        text_find = LINK_FORMAT_STR.format('')
        # Add 1 as _common/ gives false extra depth
        depth_diff = 1 + copy_from.count(os.sep) - copy_to.count(os.sep)
        args = [os.pardir]  # We go up one from the common directory
        args.extend(copy_from[len_root_dir:].split(os.sep)[:depth_diff])
        # Put a trailing '/' on the replacement string
        args.append('')
        text_repl = LINK_FORMAT_STR.format(os.path.join(*args))
        _replace_in_file(copy_to, text_find, text_repl,
                         nervous_mode, len_root_dir)
        # Delete all original files
        for dupe_file_path in v:
            if nervous_mode:
                logging.info(
                    'Would delete "{:s}"'.format(dupe_file_path[len_root_dir:])
                )
            else:
                logging.debug('Remove:', dupe_file_path[len_root_dir:])
                os.remove(dupe_file_path)
            count_deleted += 1
    logging.info(' DONE Copying and deleting '.center(75, "="))
    return count_deleted, count_bytes_saved


def _rewrite_links_where_files_deleted(root_dir,
                                       sub_dir_for_common_files,
                                       nervous_mode,
                                       hash_result,
                                       len_root_dir):
    """In the directories where we have deleted files rewrite the links to the
    common directory."""
    logging.info(' Rewriting links '.center(75, "="))
    root_depth = root_dir.count(os.sep)
    for k, v in hash_result.items():
        for dupe_file_path in v:
            # Look at all HTML files in this directory and relink them to the
            # common_dir/file
            for root, dirs, files in os.walk(os.path.dirname(dupe_file_path)):
                depth = root.count(os.sep)
                assert depth >= root_depth
                # Search for things like:
                # <a href="Python.h_53f762a407a98d46db1d8ca72f382b50.html">
                # Replace with something like:
                # <a href="../../../common/Python.h_53f762a407a98d46db1d8ca72f382b50.html">
                # We also want to change links with lin numbers like:
                # <a href="_types.h_5b73d29fecfc2614281b2623ca49929e.html#37
                text_find = LINK_FORMAT_STR.format(os.path.basename(dupe_file_path))
                args = [os.pardir, ] * (depth - root_depth)
                args.append(sub_dir_for_common_files)
                args.append(os.path.basename(dupe_file_path))
                text_repl = LINK_FORMAT_STR.format(os.path.join(*args))
                for file in files:
                    if fnmatch.fnmatch(file, FILE_GLOB):
                        _replace_in_file(os.path.join(root, file),
                                         text_find,
                                         text_repl,
                                         nervous_mode,
                                         len_root_dir)
    logging.info(' DONE: Rewriting links '.center(75, "="))


def process(root_dir, sub_dir_for_common_files=SUB_DIR_FOR_COMMON_FILES,
            file_glob=FILE_GLOB, nervous_mode=False):
    """Process a directory in-place by making a single copy of common files,
    deleting the rest and fixing the links."""
    if not (os.path.exists(root_dir) and os.path.isdir(root_dir)):
        raise ValueError(
            'Root directory "{!r:s}" does not exist.'.format(root_dir)
        )
    root_dir = os.path.normpath(root_dir)
    len_root_dir = len(root_dir) + 1  # To get rid of the '/'
    logging.info('Root directory "{:s}" '.format(root_dir))
    # Get the hash of duplicates
    hash_result = _prepare_to_process(root_dir, file_glob)
    common_dir = os.path.join(root_dir, sub_dir_for_common_files)
    if len(hash_result):
        if not os.path.exists(common_dir):
            if nervous_mode:
                logging.info('Would create "{:s}"'.format(common_dir))
            else:
                os.mkdir(common_dir)
                # Write CSS file
                TokenCss.writeCssToDir(common_dir)
    statistics = _copy_delete_duplicates_fix_links(hash_result,
                                                   common_dir,
                                                   nervous_mode,
                                                   len_root_dir)
    _rewrite_links_where_files_deleted(root_dir,
                                       sub_dir_for_common_files,
                                       nervous_mode,
                                       hash_result,
                                       len_root_dir)
    return statistics


def main():
    """Delete and relink common files."""
    program_version = "v%s" % __version__
    program_shortdesc = \
        'DupeRelink.py - Delete duplicate HTML files and relink them to save space.'\
        ' WARNING: This deletes in-place.'
    program_license = """%s
  Version: %s
  Created by Paul Ross on %s.
  Copyright 2017. All rights reserved.
  Licensed under GPL 2.0
USAGE
""" % (program_shortdesc, program_version, str(__date__))
    parser = argparse.ArgumentParser(
        description=program_license,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-s", "--subdir", type=str, dest="subdir",
                        default=SUB_DIR_FOR_COMMON_FILES,
        help="Sub-directory for writing the common files. [default: %(default)s]")
    parser.add_argument("-n", "--nervous", action="store_true", dest="nervous",
                        default=False,
        help="Nervous mode, don't do anything but report what would be done."
             " Sets logging to INFO. [default: %(default)s]")
    parser.add_argument(
        "-l", "--loglevel",
        type=int,
        dest="loglevel",
        default=30,
        help="Log Level (debug=10, info=20, warning=30, error=40, critical=50)"
        " [default: %(default)s]"
    )
    parser.add_argument(
        dest="path",
        nargs=1,
        help="Path to source directory. WARNING: This will be rewritten in-place."
    )
    args = parser.parse_args()
    clkStart = time.clock()
    # Initialise logging etc.
    inPath = args.path[0]
    if args.nervous:
        log_level = min([args.loglevel, 20])
    else:
        log_level = args.loglevel
    logFormat = '%(asctime)s %(levelname)-8s %(message)s'
    logging.basicConfig(level=log_level,
                    format=logFormat,
                    # datefmt='%y-%m-%d % %H:%M:%S',
                    stream=sys.stdout)
    if os.path.isfile(inPath):
        logging.fatal('Path "{:s}" must be a directory.'.format(inPath))
        return 1
    elif os.path.isdir(inPath):
        print('Procesing: "{:s}" '.format(inPath))
        count_deleted, count_bytes_saved = process(
           inPath,
           sub_dir_for_common_files=args.subdir,
           file_glob=FILE_GLOB,
           nervous_mode=args.nervous
        )
        print('Files deleted: {:12d}'.format(count_deleted))
        print('  Bytes saved: {:12d} {:8.3f} (MB)'.format(
            count_bytes_saved, count_bytes_saved / 1024**2)
        )
    else:
        logging.fatal('%s is neither a file or a directory!' % inPath)
        return 1
    clkExec = time.clock() - clkStart
    print('CPU time = %8.3f (S)' % clkExec)
    print('Bye, bye!')
    return 0

if __name__ == '__main__':
    exit(main())
