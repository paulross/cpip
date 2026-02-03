/*************************************************************************
 *
 * $Id: stdio.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_STDIO_H
#define PREDEF_STDIO_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#define PREDEF_HEADER_STDIO
#include <stdio.h>

#if defined(PREDEF_STANDARD_XOPEN_1989)
# define PREDEF_FUNC_TEMPNAM
#endif
#if defined(PREDEF_STANDARD_XOPEN_1989) || defined(PREDEF_STANDARD_POSIX_1990)
# define PREDEF_FUNC_PCLOSE
# define PREDEF_FUNC_POPEN
#endif
#if defined(PREDEF_STANDARD_XOPEN_1992) || defined(PREDEF_STANDARD_POSIX_1992)
# define PREDEF_FUNC_GETOPT
#endif
#if defined(PREDEF_STANDARD_XOPEN_1998)
# define PREDEF_FUNC_FLOCKFILE
# define PREDEF_FUNC_FSEEKO
# define PREDEF_FUNC_FTELLO
# define PREDEF_FUNC_FTRYLOCKFILE
# define PREDEF_FUNC_FUNLOCKFILE
# define PREDEF_FUNC_GETC_UNLOCKED
# define PREDEF_FUNC_GETCHAR_UNLOCKED
# define PREDEF_FUNC_PUTC_UNLOCKED
# define PREDEF_FUNC_PUTCHAR_UNLOCKED
#endif
#if defined(PREDEF_STANDARD_C99) || defined(PREDEF_STANDARD_XOPEN_1998)
# define PREDEF_FUNC_SNPRINTF
# define PREDEF_FUNC_VSNPRINTF
#endif
#if defined(PREDEF_STANDARD_C99) || defined(PREDEF_STANDARD_XOPEN_2003)
# define PREDEF_FUNC_VFSCANF
# define PREDEF_FUNC_VSCANF
# define PREDEF_FUNC_VSSCANF
#endif

#endif /* PREDEF_STDIO_H */
