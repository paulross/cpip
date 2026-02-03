/*************************************************************************
 *
 * $Id: ctype.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_CTYPE_H
#define PREDEF_CTYPE_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#define PREDEF_HEADER_CTYPE
#include <ctype.h>

#if defined(PREDEF_STANDARD_XOPEN_1989)
# define PREDEF_FUNC__TOLOWER
# define PREDEF_FUNC__TOUPPER
# define PREDEF_FUNC_ISASCII
# define PREDEF_FUNC_TOASCII
#endif

#endif /* PREDEF_CTYPE_H */
