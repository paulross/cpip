/*************************************************************************
 *
 * $Id: wctype.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_WCTYPE_H
#define PREDEF_WCTYE_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#if defined(PREDEF_STANDARD_C94) || defined(PREDEF_STANDARD_XOPEN_1998)
# define PREDEF_HEADER_WCTYPE
# include <wctype.h>

# if !defined(PREDEF_FUNC_ISWALNUM)
/* These may already have been defined in <predef/wchar.h> */
#  define PREDEF_FUNC_ISWALNUM
#  define PREDEF_FUNC_ISWALPHA
#  define PREDEF_FUNC_ISWCNTRL
#  define PREDEF_FUNC_ISWCTYPE
#  define PREDEF_FUNC_ISWDIGIT
#  define PREDEF_FUNC_ISWGRAPH
#  define PREDEF_FUNC_ISWLOWER
#  define PREDEF_FUNC_ISWPRINT
#  define PREDEF_FUNC_ISWPUNCT
#  define PREDEF_FUNC_ISWSPACE
#  define PREDEF_FUNC_ISWUPPER
#  define PREDEF_FUNC_ISWXDIGIT
#  define PREDEF_FUNC_TOWLOWER
#  define PREDEF_FUNC_TOWUPPER
# endif
# define PREDEF_FUNC_TOWCTRANS
# define PREDEF_FUNC_WCTRANS
# define PREDEF_FUNC_WCTYPE

#endif

#endif /* PREDEF_WCTYPE_H */
