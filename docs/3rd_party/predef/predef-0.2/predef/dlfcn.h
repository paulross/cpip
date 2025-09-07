/*************************************************************************
 *
 * $Id: dlfcn.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_DLFCN_H
#define PREDEF_DLFCN_H

#ifndef PREDEF_PREDEF_H
# include <predef/predef.h>
#endif

#if defined(PREDEF_STANDARD_POSIX_1998) \
  || (defined(PREDEF_LIBC_GNU) && (PREDEF_LIBC_GNU >= 20000))
# define PREDEF_HEADER_DLFCN
# include <dlfcn.h>

# define PREDEF_FUNC_DLCLOSE
# define PREDEF_FUNC_DLERROR
# define PREDEF_FUNC_DLOPEN
# define PREDEF_FUNC_DLSYM
#endif

#endif /* PREDEF_DLFCN_H */
