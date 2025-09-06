Incremental Build
=================

Basic assumptions
------------------

Just support git for the moment.
Our interaction is pretty simple so subprocess and re are all we need rather than relying on a dependency such as GitPython. This preserves cpip's independence at the expense of being a bit fragile.

Stored State
-------------

In the output directory we need to store a couple of files:

* History of the builds of the output directory. This can be a simple text file with one line per record latest last. Format: CSV. Name: ``git_history.txt``. Fields:
	* Git SHA this was built from.
	* Git timestamp, UTC, format YYYY-MM-DDTHH:MM:SS (RFC3339).
	* CPIP start build time, UTC, format YYYY-MM-DDTHH:MM:SS (RFC3339).

* Dependencies. This will be a flattened dependency tree: {globbed_file : [set(included_files)], ...}. Format: JSON. Name: file_dependencies.json

History
^^^^^^^^^^^^^^^^^^^^^^^

[git show --format=oneline <SHA> does not work, it dumps complete diff]

git show HEAD gives the following first three lines:

commit 153dddf037f6ac5eb48e48601698ee742e34fb0e
Author: Paul Ross <apaulross@gmail.com>
Date:   Sun Oct 8 12:16:06 2017 +0100

Date is in format (hopefully this works for all locales):

d = datetime.datetime.strptime(s, '%c %z') # Gives a fixed offset, aware datetime.
d.utctimetuple() # Components of UTC
u = dt.datetime(*d.utctimetuple()[:6])
Output:
u.strftime('%Y-%m-%dT%H:%M:%S')
'2017-10-08T11:16:06'

git diff <SHA> <SHA or 'HEAD'> --name-only

Gives list of files. What about deleted files

git log --name-status --diff-filter=D

Or all files:
git log -n 1 --name-status <SHA>

commit 58e0e67392234b91b514d246fb23a0dc8c2a92d3
Author: Paul Ross <apaulross@gmail.com>
Date:   Wed Oct 4 11:01:41 2017 +0100

    Release candidate v0.9.8rc0

M       setup.cfg
M       setup.py
M       src/cpip/CPIPMain.py
M       src/cpip/__init__.py


Dependencies
^^^^^^^^^^^^^^^^^^^^^^^

From the file include graph. The top level module ``IncList`` has a ``retIncludedFileSet()`` function that seems to do the job. Actually ``cpip.core.FileIncludeGraph.FigVisitorFileSet`` does the job.

Proceedure
--------------

Bring source tree up to date (or to a specific branch or commit).

Base the code on ``cpip.CPIPMain.preprocessDirToOutput()`` but instead of processing one by one create a list of jobs to do then remove unnecessary jobs where the file and its dependencies have not changed.

all_files = [t.filePathIn for job in DirWalk.dirWalk(inDir, outDir, globMatch, recursive, bigFirst=False)]

Find list of files that have been added or modified from git (see history above). Read the dependencies from the previous build. Any file that has been modified or has modified dependencies must be rebuilt.

Rewrite the top level index from the update dependencies with a table showing the history. Remove sub-directories that are not referenced in the index (file was deleted).

Update history and dependencies.

rsync to remote target.

Set up a cron for all of this.

Report to a mailing list?
