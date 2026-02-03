/*************************************************************************
 *
 * $Id: unistd.h,v 1.2 2005/05/22 11:50:58 breese Exp $
 *
 * Copyright (C) 2003 Bjorn Reese <breese@users.sourceforge.net>
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTIES OF
 * MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE AUTHORS AND
 * CONTRIBUTORS ACCEPT NO RESPONSIBILITY IN ANY CONCEIVABLE MANNER.
 *
 ************************************************************************/

#ifndef PREDEF_UNISTD_H
#define PREDEF_UNISTD_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#if defined(PREDEF_STANDARD_XOPEN_1989) || defined(PREDEF_STANDARD_POSIX_1990)
# define PREDEF_HEADER_UNISTD
# include <unistd.h>

# define PREDEF_FUNC_ACCESS
# define PREDEF_FUNC_ALARM
# define PREDEF_FUNC_CHDIR
# define PREDEF_FUNC_CHMOD
# define PREDEF_FUNC_CHOWN
# define PREDEF_FUNC_CLOSE
# define PREDEF_FUNC_CTERMID
# define PREDEF_FUNC_DUP
# define PREDEF_FUNC_DUP2
# define PREDEF_FUNC_EXECL
# define PREDEF_FUNC_EXECLE
# define PREDEF_FUNC_EXECLP
# define PREDEF_FUNC_EXECV
# define PREDEF_FUNC_EXECVE
# define PREDEF_FUNC_EXECVP
# define PREDEF_FUNC_FORK
# define PREDEF_FUNC_FPATHCONF
# define PREDEF_FUNC_GETCWD
# define PREDEF_FUNC_GETEGID
# define PREDEF_FUNC_GETEUID
# define PREDEF_FUNC_GETGID
# define PREDEF_FUNC_GETGROUPS
# define PREDEF_FUNC_GETLOGIN
# define PREDEF_FUNC_GETPGRP
# define PREDEF_FUNC_GETPID
# define PREDEF_FUNC_GETPPID
# define PREDEF_FUNC_GETUID
# define PREDEF_FUNC_LINK
# define PREDEF_FUNC_LSEEK
# define PREDEF_FUNC_PATHCONF
# define PREDEF_FUNC_PAUSE
# define PREDEF_FUNC_PIPE
# define PREDEF_FUNC_READ
# define PREDEF_FUNC_RMDIR
# define PREDEF_FUNC_SETGID
# define PREDEF_FUNC_SETPGID
# define PREDEF_FUNC_SETSID
# define PREDEF_FUNC_SETUID
# define PREDEF_FUNC_SLEEP
# define PREDEF_FUNC_SYSCONF
# define PREDEF_FUNC_TCGETPGRP
# define PREDEF_FUNC_TCSETPGRP
# define PREDEF_FUNC_TTYNAME
# define PREDEF_FUNC_UNLINK
# define PREDEF_FUNC_WRITE

# if defined(PREDEF_STANDARD_XOPEN_1992)
#  define PREDEF_FUNC_NICE
#  define PREDEF_FUNC_SWAB
# endif

# if defined(PREDEF_STANDARD_XOPEN_1992) || defined(PREDEF_STANDARD_POSIX_1992)
#  define PREDEF_FUNC_CONFSTR
#  define PREDEF_FUNC_FSYNC
#  define PREDEF_FUNC_GETOPT
# endif

# if defined(PREDEF_STANDARD_XOPEN_1995)
#  define PREDEF_FUNC_FCHDIR
#  define PREDEF_FUNC_FCHMOD
#  define PREDEF_FUNC_GETHOSTID
#  define PREDEF_FUNC_GETHOSTNAME
#  define PREDEF_FUNC_GETPGID
#  define PREDEF_FUNC_GETSID
#  define PREDEF_FUNC_GETWD
#  define PREDEF_FUNC_LCHOWN
#  define PREDEF_FUNC_LOCKF
#  define PREDEF_FUNC_READLINK
#  define PREDEF_FUNC_SETPGRP
#  define PREDEF_FUNC_SETREGID
#  define PREDEF_FUNC_SETREUID
#  define PREDEF_FUNC_SYMLINK
#  define PREDEF_FUNC_SYNC
#  define PREDEF_FUNC_TRUNCATE
#  define PREDEF_FUNC_UALARM
#  define PREDEF_FUNC_USLEEP
#  define PREDEF_FUNC_VFORK
# endif

# if defined(PREDEF_STANDARD_XOPEN_1995) || defined(PREDEF_STANDARD_POSIX_1992)
#  define PREDEF_FUNC_FTRUNCATE
# endif

# if defined(PREDEF_STANDARD_XOPEN_1998) || defined(PREDEF_STANDARD_POSIX_1993)
#  define PREDEF_FUNC_FDATASYNC
# endif

# if defined(PREDEF_STANDARD_XOPEN_1998)
#  define PREDEF_FUNC_GETLOGIN_R
#  define PREDEF_FUNC_PREAD
#  define PREDEF_FUNC_PWRITE
#  define PREDEF_FUNC_TTYNAME_R
# endif
#endif

#endif /* PREDEF_UNISTD_H */
