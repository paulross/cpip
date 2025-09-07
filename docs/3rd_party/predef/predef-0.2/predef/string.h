/*************************************************************************
 *
 * $Id: string.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_STRING_H
#define PREDEF_STRING_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#define PREDEF_HEADER_STRING
#include <string.h>

#if defined(PREDEF_STARDARD_XOPEN_1989) \
 || defined(PREDEF_LIBC_WINDOWS)
# define PREDEF_FUNC_MEMCCPY
#endif
#if defined(PREDEF_STARDARD_XOPEN_1995) \
 || defined(PREDEF_LIBC_WINDOWS) \
 || (defined(PREDEF_LIBC_VMS) && (PREDEF_LIBC_VMS >= 70000000))
# define PREDEF_FUNC_STRDUP
#endif
#if defined(PREDEF_STARDARD_XOPEN_1998)
# define PREDEF_FUNC_STRTOK_R
#endif

#endif /* PREDEF_STRING_H */
