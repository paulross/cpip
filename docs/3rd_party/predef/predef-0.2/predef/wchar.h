/*************************************************************************
 *
 * $Id: wchar.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_WCHAR_H
#define PREDEF_WCHAR_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#if defined(PREDEF_STANDARD_C94) || defined(PREDEF_STANDARD_XOPEN_1992)
# define PREDEF_HEADER_WCHAR
# include <wchar.h>

# define PREDEF_FUNC_FGETWC
# define PREDEF_FUNC_FGETWS
# define PREDEF_FUNC_FPUTWC
# define PREDEF_FUNC_FPUTWS
# define PREDEF_FUNC_GETWC
# define PREDEF_FUNC_GETWCHAR
# define PREDEF_FUNC_PUTWC
# define PREDEF_FUNC_PUTWCHAR
# define PREDEF_FUNC_UNGETWC
# define PREDEF_FUNC_WCSCAT
# define PREDEF_FUNC_WCSCHR
# define PREDEF_FUNC_WCSCMP
# define PREDEF_FUNC_WCSCOLL
# define PREDEF_FUNC_WCSCPY
# define PREDEF_FUNC_WCSCSPN
# define PREDEF_FUNC_WCSFTIME
# define PREDEF_FUNC_WCSLEN
# define PREDEF_FUNC_WCSNCAT
# define PREDEF_FUNC_WCSNCMP
# define PREDEF_FUNC_WCSNCPY
# define PREDEF_FUNC_WCSPBRK
# define PREDEF_FUNC_WCSRCHR
# define PREDEF_FUNC_WCSSPN
# define PREDEF_FUNC_WCSSTR
# define PREDEF_FUNC_WCSTOD
# define PREDEF_FUNC_WCSTOK
# define PREDEF_FUNC_WCSTOL
# define PREDEF_FUNC_WCSTOUL
# define PREDEF_FUNC_WCSXFRM

# if defined(PREDEF_STANDARD_XOPEN_1992)
#  if !defined(PREDEF_FUNC_ISWALPHA)
/* These may already have been defined in <predef/wctype.h> */
#   define PREDEF_FUNC_ISWALNUM
#   define PREDEF_FUNC_ISWALPHA
#   define PREDEF_FUNC_ISWCNTRL
#   define PREDEF_FUNC_ISWCTYPE
#   define PREDEF_FUNC_ISWDIGIT
#   define PREDEF_FUNC_ISWGRAPH
#   define PREDEF_FUNC_ISWLOWER
#   define PREDEF_FUNC_ISWPRINT
#   define PREDEF_FUNC_ISWPUNCT
#   define PREDEF_FUNC_ISWSPACE
#   define PREDEF_FUNC_ISWUPPER
#   define PREDEF_FUNC_ISWXDIGIT
#   define PREDEF_FUNC_TOWLOWER
#   define PREDEF_FUNC_TOWUPPER
#  endif
#  define PREDEF_FUNC_WCSWCS
#  define PREDEF_FUNC_WCSWIDTH
#  define PREDEF_FUNC_WCTYPE
#  define PREDEF_FUNC_WCWIDTH
# endif

# if defined(PREDEF_STANDARD_C94) || defined(PREDEF_STANDARD_XPEN_1998)
#  define PREDEF_FUNC_BTOWC
#  define PREDEF_FUNC_FWIDE
#  define PREDEF_FUNC_FWPRINTF
#  define PREDEF_FUNC_FWSCANF
#  define PREDEF_FUNC_MBRLEN
#  define PREDEF_FUNC_MBRTOWC
#  define PREDEF_FUNC_MBSINIT
#  define PREDEF_FUNC_SWPRINTF
#  define PREDEF_FUNC_SWSCANF
#  define PREDEF_FUNC_VFWPRINTF
#  define PREDEF_FUNC_VSWPRINTF
#  define PREDEF_FUNC_VWPRINTF
#  define PREDEF_FUNC_WCRTOMB
#  define PREDEF_FUNC_WCSRTOMBS
#  define PREDEF_FUNC_WCTOB
#  define PREDEF_FUNC_WMEMCHR
#  define PREDEF_FUNC_WMEMCMP
#  define PREDEF_FUNC_WMEMCPY
#  define PREDEF_FUNC_WMEMMOVE
#  define PREDEF_FUNC_WMEMSET
#  define PREDEF_FUNC_WPRINTF
#  define PREDEF_FUNC_WSCANF
# endif

# if defined(PREDEF_STANDARD_C99) || defined(PREDEF_STANDARD_XOPEN_2003)
#  define PREDEF_FUNC_VFWSCANF
#  define PREDEF_FUNC_VSWSCANF
#  define PREDEF_FUNC_VWSCANF
#  define PREDEF_FUNC_WCSTOF
#  define PREDEF_FUNC_WCSTOLL
#  define PREDEF_FUNC_WCSTOULL
# endif

#endif

#endif /* PREDEF_WCHAR_H */
