/*************************************************************************
 *
 * $Id: timeb.h,v 1.2 2005/05/22 11:50:59 breese Exp $
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

#ifndef PREDEF_SYS_TIMEB_H
#define PREDEF_SYS_TIMEB_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#if defined(PREDEF_STANDARD_XOPEN_1995) \
  || (defined(PREDEF_LIBC_GNU) && (PREDEF_LIBC_GNU >= 20000))
# define PREDEF_HEADER_SYS_TIMEB
# include <sys/timeb.h>

# define PREDEF_FUNC_FTIME
#endif

#endif /* PREDEF_SYS_TIMEB_H */
