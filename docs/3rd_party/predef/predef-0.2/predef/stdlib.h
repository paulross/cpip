/*************************************************************************
 *
 * $Id: stdlib.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_STDLIB_H
#define PREDEF_STDLIB_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#define PREDEF_HEADER_STDLIB
#include <stdlib.h>

#if defined(PREDEF_STARDARD_XOPEN_1992)
# define PREDEF_FUNC_DRAND48
# define PREDEF_FUNC_ERAND48
# define PREDEF_FUNC_JRAND48
# define PREDEF_FUNC_LCONG48
# define PREDEF_FUNC_LRAND48
# define PREDEF_FUNC_MRAND48
# define PREDEF_FUNC_NRAND48
# define PREDEF_FUNC_PUTENV
# define PREDEF_FUNC_SEED48
# define PREDEF_FUNC_SRAND48
#endif
#if defined(PREDEF_STARDARD_XOPEN_1995)
# define PREDEF_FUNC_A64L
# define PREDEF_FUNC_ECVT
# define PREDEF_FUNC_FCVT
# define PREDEF_FUNC_GCVT
# define PREDEF_FUNC_GETSUBOPT
# define PREDEF_FUNC_GRANTPT
# define PREDEF_FUNC_INITSTATE
# define PREDEF_FUNC_L64A
# define PREDEF_FUNC_MKSTEMP
# define PREDEF_FUNC_MKTEMP
# define PREDEF_FUNC_PTSNAME
# define PREDEF_FUNC_RANDOM
# define PREDEF_FUNC_REALPATH
# define PREDEF_FUNC_SETSTATE
# define PREDEF_FUNC_SRANDOM
# define PREDEF_FUNC_UNLOCKPT
#endif
#if defined(PREDEF_STARDARD_XOPEN_1998)
# define PREDEF_FUNC_RAND_R
#endif
#if defined(PREDEF_STANDARD_C99) || defined(PREDEF_STANDARD_XOPEN_2003)
# define PREDEF_FUNC_C__EXIT /* _Exit() */
# define PREDEF_FUNC_ATOLL
# define PREDEF_FUNC_LLABS
# define PREDEF_FUNC_LLDIV
# define PREDEF_FUNC_STRTOF
# define PREDEF_FUNC_STRTOLD
# define PREDEF_FUNC_STRTOLL
# define PREDEF_FUNC_STRTOULL
#endif

#endif /* PREDEF_STDLIB_H */
