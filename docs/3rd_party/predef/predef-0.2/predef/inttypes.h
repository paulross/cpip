/*************************************************************************
 *
 * $Id: inttypes.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_INTTYPES_H
#define PREDEF_INTTYPES_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#if defined(PREDEF_STANDARD_C99) \
 || defined(PREDEF_STANDARD_XOPEN_1998) \
 || (defined(PREDEF_LIBC_GNU) && PREDEF_LIBC_GNU >= 20100)
# define PREDEF_HEADER_INTTYPES
# include <inttypes.h>

# define PREDEF_FUNC_IMAXABS
# define PREDEF_FUNC_IMAXDIV
# define PREDEF_FUNC_STRTOIMAX
# define PREDEF_FUNC_STRTOUMAX
# define PREDEF_FUNC_WCSTOIMAX
# define PREDEF_FUNC_WCSTOUMAX
#endif

#endif /* PREDEF_INTTYPES_H */
