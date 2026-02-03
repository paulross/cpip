/*************************************************************************
 *
 * $Id: signal.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_SIGNAL_H
#define PREDEF_SIGNAL_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#define PREDEF_HEADER_SIGNAL
#include <signal.h>

#if defined(PREDEF_STANDARD_XOPEN_1989) || defined(PREDEF_STANDARD_POSIX_1990)
# define PREDEF_FUNC_KILL
# define PREDEF_FUNC_SIGACTION
# define PREDEF_FUNC_SIGADDSET
# define PREDEF_FUNC_SIGDELSET
# define PREDEF_FUNC_SIGEMPTYSET
# define PREDEF_FUNC_SIGFILLSET
# define PREDEF_FUNC_SIGISMEMBER
# define PREDEF_FUNC_SIGPENDING
# define PREDEF_FUNC_SIGPROCMASK
# define PREDEF_FUNC_SIGSUSPEND
#endif
#if defined(PREDEF_STANDARD_XOPEN_1995)
# define PREDEF_FUNC_KILLPG
# define PREDEF_FUNC_SIGALTSTACK
# define PREDEF_FUNC_SIGHOLD
# define PREDEF_FUNC_SIGIGNORE
# define PREDEF_FUNC_SIGINTERRUPT
# define PREDEF_FUNC_SIGPAUSE
#endif

#endif /* PREDEF_SIGNAL_H */
