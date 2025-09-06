Incremental Build
=================

Just support git for the moment.

Stored State
-------------


    * Git SHA this was built from.
    * Git timestamp, UTC, format YYYY-MM-DDTHH:MM:SS (RFC3339).

History



commit 153dddf037f6ac5eb48e48601698ee742e34fb0e
Author: Paul Ross <apaulross@gmail.com>
Date:   Sun Oct 8 12:16:06 2017 +0100

Date is in format (hopefully this works for all locales):

Output:
    '2017-10-08T11:16:06'




Or all files:
    git log -n 1 --name-status <SHA>

    commit 58e0e67392234b91b514d246fb23a0dc8c2a92d3
    Author: Paul Ross <apaulross@gmail.com>
    Date:   Wed Oct 4 11:01:41 2017 +0100


Dependencies
--------------

Bring source tree up to date (or to a specific branch or commit).


    all_files = [t.filePathIn for job in DirWalk.dirWalk(inDir, outDir, globMatch, recursive, bigFirst=False)]



Update history and dependencies.

rsync to remote target.

Set up a cron for all of this.

Report to a mailing list?
