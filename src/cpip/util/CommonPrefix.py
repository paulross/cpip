"""Created on 23 Feb 2014

@author: paulross
"""
import os

def lenCommonPrefix(iterable):
    """Returns the length of the common prefix of a list of file names.
    The prefix is limited to directory names."""
    pref = os.path.commonprefix([os.path.normpath(p) for p in iterable])
    # Find '/'
    idx = pref.rfind(os.sep)
    if idx > 0:
        return idx+1
    return len(pref)
