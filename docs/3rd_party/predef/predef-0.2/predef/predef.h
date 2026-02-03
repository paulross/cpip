/*************************************************************************
 *
 * $Id: predef.h,v 1.2 2005/05/22 11:50:58 breese Exp $
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

#ifndef PREDEF_PREDEF_H
#define PREDEF_PREDEF_H

/*
 * References:
 *   http://predef.sourceforge.net/
 *   http://www.UNIX-systems.org/v3-apis.html
 *   http://petef.port5.com/c/portability.txt
 */

/*************************************************************************
 * Compilers
 */

/*
 * Borland C/C++
 *
 * Version: 0xVRR : V = Version, RR = Revision
 * Example: 0x551 = Borland C++ 5.51
 */
#if defined(__BORLANDC__)
# define PREDEF_COMPILER_BORLAND __BORLANDC__
#endif

/*
 * Comeau C++
 *
 * Version: VRR : V = Version, RR = Revision
 * Example: 230 = Comeau C++ 2.30
 */
#if defined(__COMO__)
# if defined(__COMO_VERSION__)
#  define PREDEF_COMPILER_COMEAU __COMO_VERSION__
# else
#  define PREDEF_COMPILER_COMEAU 0
# endif
#endif

/*
 * Cray C/C++
 *
 * Version: V : V = Version
 * Example: ?
 */
#if defined(_CRAYC)
# if defined(_REVISION)
#  define PREDEF_COMPILER_CRAY _REVISION
# else
#  define PREDEF_COMPILER_CRAY 0
# endif
#endif

/*
 * Cygwin
 */
#if defined(__CYGWIN__)
# define PREDEF_COMPILER_CYGWIN 0
#endif

/*
 * Compaq C++
 *
 * Version: VVRRTPPP : VV = Version, RR = Revision, T = Type, PPP = Patch
 * Example: 60090001 = DEC C/C++ 6.0-001
 */
#if defined(__DECC) || defined(__DECCXX)
# if defined(__DECC_VER)
#  define PREDEF_COMPILER_DECC __DECC_VER
# else
#  define PREDEF_COMPILER_DECC 0
# endif
#else
# if defined(VAXC) || defined(__VAXC)
#  define PREDEF_COMPILER_DECC 0
# else
#  if defined(__osf__) && defined(__LANGUAGE_C__) && !defined(__GNUC__)
/* Workaround for old DEC C compilers */
#   define PREDEF_COMPILER_DECC 0
#  endif
# endif
#endif

/*
 * Diab C/C++
 *
 * Version: VRPP : V = Version, R = Revision, PP = Patch
 * Example: 4426 = Diab C/C++ 4.4q
 */
#if defined(__DCC__) && defined(__VERSION_NUMBER__)
# define PREDEF_COMPILER_DIAB __VERSION_NUMBER__
#endif

/*
 * Digital Mars (Symatec C++, Zortech C++)
 *
 * Version: 0xVRP : V = Version, R = Revision, P = Patch
 * Example: 0x720 = Digital Mars 7.2
 */
#if defined(__DMC__)
# define PREDEF_COMPILER_DMC __DMC__
#else
# if defined(__SC__) || defined(__ZTC__)
#  define PREDEF_COMPILER_DMC 0
# endif
#endif

/*
 * GNU C/C++
 *
 * Version: VVRRPP : VV = Version, RR = Revision, PP = Patch
 * Example: 030200 = GCC 3.0.2
 */
#if defined(__GNUC__)
# if defined(__GNUC_PATCHLEVEL__)
#  define PREDEF_COMPILER_GCC ((__GNUC__ * 10000) + \
                               (__GNUC_MINOR__ * 100) + \
                               (__GNUC_PATCHLEVEL__))
# else
#  define PREDEF_COMPILER_GCC ((__GNUC__ * 10000) + \
                               (__GNUC_MINOR__ * 100))
# endif
#endif

/*
 * HP ANSI C / aC++
 *
 * Version: VVRRPP : VV = Version, RR = Revision, PP = Patch
 * Example: 12100 = A.01.21
 *
 * The __HP_aCC was introduced in version A.01.15 (and A.03.13), where
 * it is set to 1. Beginning with version A.01.21 (and A.03.25) __HP_aCC
 * is set as above.
 *
 * The C compiler defines the __HP_cc macro, and the C++ compiler the
 * __HP_aCC macro.
 */
#if defined(__HP_aCC)
# if (__HP_aCC == 1)
#  define PREDEF_COMPILER_HPCC 11500
# else
#  define PREDEF_COMPILER_HPCC __HP_aCC
# endif
#else
# if defined(__HP_cc)
#  define PREDEF_COMPILER_HPCC __HP_cc
# else
#  if (__cplusplus - 0 >= 199707L) && defined(__hpux)
#   define PREDEF_COMPILER_HPCC 0
#  endif
# endif
#endif

/*
 * Intel C++
 *
 * Version: VRP : V = Version, R = Revision, P = Patch
 * Example: 500 = ICC 5.0
 */
#if defined(__INTEL_COMPILER)
# define PREDEF_COMPILER_INTEL __INTEL_COMPILER
#else
# if defined(__ICC)
#  define PREDEF_COMPILER_INTEL 0
# endif
#endif

/*
 * KAI C++
 *
 * Version: 0xVRPP : V = Version, R = Revision, PP = Patch
 * Example: 0x4004 = KAI C++ 4.0d
 *
 * Please note that Intel has discontinued development of the KAI C++
 * compiler in spring 2002:
 *
 *   http://developer.intel.com/software/products/kcc/announcement.htm
 */
#if defined(__KCC)
# if defined(__KCC_VERSION)
#  define PREDEF_COMPILER_KAI __KCC_VERSION
# else
#  define PREDEF_COMPILER_KAI 0
# endif
#endif

/*
 * MinGW32
 */
#if defined(__MINGW32__)
# define PREDEF_COMPILER_MINGW32 0
#endif

/*
 * SGI MIPSpro
 *
 * Version: VRP : V = Version, R = Revision, P = Patch
 * Example: 721 = MIPSpro 7.2.1
 */
#if (defined(sgi) || defined(__sgi)) && defined(_COMPILER_VERSION)
# define PREDEF_COMPILER_MIPSPRO _COMPILER_VERSION
#endif

/*
 * Apple MPW C++
 *
 * Version: 0xVVRR : VV = Version, RR = Revision
 * Example: 0x0500 = MPW C++ 5.0
 */
#if defined(__MRC__)
# define PREDEF_COMPILER_MPW __MRC__
#else
# if defined(MPW_C) || defined(MPW_CPLUS)
#  define PREDEF_COMPILER_MPW 0
# endif
#endif

/*
 * Metrowerks CodeWarrior
 *
 * Version: 0xVRPP : V = Version, R = Revision, PP = Patch
 * Example: 0x2200 = Metrowerks C/C++ 2.2
 *
 * Versions prior to CodeWarrior 7 sets __MWERKS__ to 1.
 */
#if defined(__MWERKS__)
# define PREDEF_COMPILER_MWERKS __MWERKS__
#endif

/*
 * Norcroft C
 *
 * The __ARMCC_VERSION macro is assigned a floating-point number,
 * so it cannot be used by the preprocessor to compare versions.
 */
#if defined(__CC_NORCROFT)
# define PREDEF_COMPILER_NORCROFT 0
#endif

/*
 * SCO OpenServer
 */
#if defined(_SCO_DS)
# define PREDEF_COMPILER_SCO 0
#endif

/*
 * Sun Forte C/C++ (Workshop Pro)
 *
 * Version: 0xVRP : V = Version, R = Revision, P = Patch
 * Example: 0x500 = Workshop Pro 5.0
 */
#if defined(__SUNPRO_C)
# define PREDEF_COMPILER_SUNPRO __SUNPRO_C
#else
# if defined(__SUNPRO_CC)
#  define PREDEF_COMPILER_SUNPRO __SUNPRO_CC
# endif
#endif

/*
 * TenDRA
 */
#if defined(__TenDRA__)
# define PREDEF_COMPILER_TENDRA 0
#endif

/*
 * USL C
 *
 * Version: 0xVRRYYYYMM : V = Version, RR = Revision, YYYY = Year, MM = Month
 * Example: 0x302199801 = USL C 3.2
 */
#if defined(__USLC__)
# if defined(__SCO_VERSION__)
#  define PREDEF_COMPILER_USLC __SCO_VERSION__
# else
#  define PREDEF_COMPILER_USLC 0
# endif
#endif

/*
 * Microsoft Visual C++
 *
 * Version: VVRR : VV = Version, RR = Revision
 * Example: 1200 = Visual C++ 6.0 (compiler 12.0)
 */
#if defined(_MSC_VER)
# define PREDEF_COMPILER_VISUALC _MSC_VER
# define PREDEF_VERSION_VISUALC_6_0 1200
# define PREDEF_VERSION_VISUALC_7_0 1300
#endif

/*
 * Watcom C++
 *
 * Version: VVRR : VV = Version, RR = Revision
 * Example: 1050 = Watcom C++ 10.5
 */
#if defined(__WATCOMC__)
# define PREDEF_COMPILER_WATCOM __WATCOMC__
#endif

/*
 * IBM xlC
 *
 * Version: 0xVVRR : VV = Version, RR = Revision
 * Example: 0x0500 = IBM xlC 5.0
 */
#if defined(__xlC__)
# define PREDEF_COMPILER_XLC __xlC__
#else
# if defined(__IBMC__) || defined(__IBMCPP__)
#  define PREDEF_COMPILER_XLC 0 /* Version is decimal */
# else
#  if defined(_AIX) && !defined(__GNUC__)
/* Workaround for old xlc */
#   define PREDEF_COMPILER_XLC 0
#  endif
# endif
#endif


/*************************************************************************
 * Operating Systems
 */

#if defined(__amigaos__) \
 || defined(AMIGA)
# define PREDEF_OS_AMIGA
#endif

#if defined(_AIX) \
 || defined(__TOS_AIX__) \
 || defined(PREDEF_COMPILER_XLC)
# define PREDEF_OS_AIX
#endif

#if defined(__BEOS__)
# define PREDEF_OS_BEOS
#endif

#if defined(bsdi) \
 || defined(__bsdi__)
# define PREDEF_OS_BSDI
#endif

#if defined(_UNICOS) \
 || defined(_CRAY)
# define PREDEF_OS_CRAY
#endif

#if defined(DGUX) \
 || defined(__DGUX__) \
 || defined(__dgux__)
# define PREDEF_OS_DGUX
#endif

#if defined(__DragonFly__)
# define PREDEF_OS_DRAGONFLY
#endif

#if defined(__FreeBSD__)
# define PREDEF_OS_FREEBSD
#endif

#if defined(hpux) \
 || defined(__hpux) \
 || defined(_HPUX_SOURCE)
# define PREDEF_OS_HPUX
#endif

#if defined(__GNU__)
# define PREDEF_OS_HURD
#endif

#if defined(sgi) \
 || defined(__sgi) \
 || defined(mips) \
 || defined(_SGI_SOURCE)
# define PREDEF_OS_IRIX
#endif

#if defined(linux) \
 || defined(__linux) \
 || defined(__linux__)
# define PREDEF_OS_LINUX
#endif

#if defined(macintosh) \
 || defined(Macintosh) \
 || defined(__MACOS__)
# define PREDEF_OS_MACINTOSH
#endif

#if defined(__MACOSX__) \
 || (defined(__APPLE__) && defined(__MACH__))
# define PREDEF_OS_MACOSX
#endif

#if defined(mpeix) \
 || defined(__mpexl)
# define PREDEF_OS_MPEIX
#endif

#if defined(MSDOS) \
 || defined(__MSDOS__) \
 || defined(_MSDOS) \
 || defined(__DOS__)
# define PREDEF_OS_MSDOS
#endif

#if defined(__NetBSD__)
# define PREDEF_OS_NETBSD
#endif

#if defined(__OpenBSD__)
# define PREDEF_OS_OPENBSD
#endif

#if defined(OS2) \
 || defined(_OS2) \
 || defined(__OS2__) \
 || defined(__TOS_OS2__)
# define PREDEF_OS_OS2
#endif

#if defined(__osf__) \
 || defined(__osf) \
 || defined(PREDEF_COMPILER_DECC)
/* See VMS below */
# define PREDEF_OS_OSF
#endif

#if defined(pyr)
# define PREDEF_OS_PYRAMID
#endif

#if defined(__QNX__) \
 || defined(__QNXNTO__)
# define PREDEF_OS_QNX
#endif

#if defined(M_I386) \
 || defined(M_XENIX) \
 || defined(_SCO_C_DIALECT) \
 || defined(PREDEF_COMPILER_SCO)
# define PREDEF_OS_SCO
#endif

#if defined(_SEQUENT_) \
 || defined(sequent)
# define PREDEF_OS_SEQUENT
#endif

#if defined(sinix)
# define PREDEF_OS_SINIX
#endif

#if defined(sun) \
 || defined(__sun__) \
 || defined(PREDEF_COMPILER_SUNPRO)
# if defined(__SVR4) || defined(__svr4__)
#  define PREDEF_OS_SOLARIS
# else
#  define PREDEF_OS_SUNOS
# endif
#endif

#if defined(ultrix) \
 || defined(__ultrix) \
 || defined(__ultrix__)
# define PREDEF_OS_ULTRIX
#endif


/*************************************************************************
 * Platforms
 */

#if defined(VMS) \
 || defined(__VMS)
# undef PREDEF_OS_OSF
# define PREDEF_PLATFORM_VMS
# if defined(__VMS_VER)
#  define PREDEF_OS_VMS __VMS_VER
# else
#  define PREDEF_OS_VMS 0
# endif
#endif

#if defined(unix) \
 || defined(__unix) \
 || defined(__unix__)
# define PREDEF_PLATFORM_UNIX
#endif
#if defined(PREDEF_OS_AIX) \
 || defined(PREDEF_OS_OSF) \
 || defined(PREDEF_OS_NETBSD) \
 || defined(PREDEF_OS_QNX)
/*
 * The Unix macros are not always defined on these platforms.
 */
# if !defined(PREDEF_PLATFORM_UNIX)
#  define PREDEF_PLATFORM_UNIX
# endif
#endif
#if defined(PREDEF_COMPILER_CYGWIN)
# define PREDEF_PLATFORM_UNIX
#endif
#if defined(AMIGA) && defined(PREDEF_COMPILER_GCC)
# define PREDEF_PLATFORM_UNIX
#endif

#if defined(WIN32) \
 || defined(_WIN32) \
 || defined(__TOS_WIN__) \
 || defined(PREDEF_COMPILER_VISUALC)
# define PREDEF_PLATFORM_WIN32
# define PREDEF_OS_WINDOWS
#endif

#if defined(PREDEF_OS_FREEBSD) \
 || defined(PREDEF_OS_NETBSD) \
 || defined(PREDEF_OS_OPENBSD) \
 || defined(PREDEF_OS_BSDI) \
 || defined(PREDEF_OS_DRAGONFLY) \
 || defined(_BSD_SOURCE) \
 || defined(_SYSTYPE_BSD)
# define PREDEF_PLATFORM_BSD
#endif

#if defined(__sysv__) \
 || defined(__SVR4) \
 || defined(__svr4__) \
 || defined(_SVR4_SOURCE) \
 || defined(_SYSTYPE_SVR4)
# define PREDEF_PLATFORM_SVR4
#endif

#if defined(UWIN)
# define PREDEF_PLATFORM_UWIN
#endif

#if defined(_WINDU_SOURCE)
# define PREDEF_PLATFORM_WINDU
#endif

/*************************************************************************
 * C Standards
 */

#define PREDEF_VERSION_C89 198900L
#define PREDEF_VERSION_C90 199000L
#define PREDEF_VERSION_C94 199409L
#define PREDEF_VERSION_C99 199901L

#if defined(__STDC_VERSION__)
# if (__STDC_VERSION__ - 0 > 1)
#  define PREDEF_STANDARD_C __STDC_VERSION__
# else
#  if (PREDEF_COMPILER_SUNPRO - 0 >= 0x420)
#   define PREDEF_STANDARD_C PREDEF_VERSION_C94
#  else
#   define PREDEF_STANDARD_C PREDEF_VERSION_C90
#  endif
# endif
#else
# if defined(__STDC__) \
  || defined(_MSC_EXTENSIONS) \
  || defined(PREDEF_COMPILER_BORLAND)
#  define PREDEF_STANDARD_C PREDEF_VERSION_C89
# endif
#endif

#if (PREDEF_STANDARD_C - 0 >= PREDEF_VERSION_C89)
# define PREDEF_STANDARD_C89
#endif
#if (PREDEF_STANDARD_C - 0 >= PREDEF_VERSION_C90)
# define PREDEF_STANDARD_C90
#endif
#if (PREDEF_STANDARD_C - 0 >= PREDEF_VERSION_C94)
# define PREDEF_STANDARD_C94
#endif
#if (PREDEF_STANDARD_C - 0 >= PREDEF_VERSION_C99)
# define PREDEF_STANDARD_C99
#endif

/*************************************************************************
 * C++ Standards
 */

#define PREDEF_VERSION_CXX98 199711L

#if defined(__cplusplus)
# if __cplusplus - 0 == 1
#  define PREDEF_STANDARD_CXX PREDEF_VERSION_CXX98
# else
#  define PREDEF_STANDARD_CXX __cplusplus
# endif
#endif

#if (PREDEF_STANDARD_CXX - 0 >= PREDEF_VERSION_CXX98)
# define PREDEF_STANDARD_CXX98
#endif

/*************************************************************************
 * Unix Standards
 */

#if defined(PREDEF_PLATFORM_UNIX)
/*
 * Get the version test macros.
 */
# include <unistd.h>
#endif

/* POSIX 1003.1  = ISO/IEC 9945-1:1990 */
#define PREDEF_VERSION_POSIX_1990 199009L
/* POSIX 1003.1b = IEEE 1003.1b-1993 */
#define PREDEF_VERSION_POSIX_1993 199309L
/* ISO/IEC 9945-1:1996 = IEEE 1003.1-1996 */
#define PREDEF_VERSION_POSIX_1996 199506L
#define PREDEF_VERSION_POSIX_2001 200112L

#if _POSIX_VERSION - 0 >= PREDEF_VERSION_POSIX_1990
# define PREDEF_STANDARD_POSIX_1990
#endif
#if _POSIX_VERSION - 0 >= PREDEF_VERSION_POSIX_1993
# define PREDEF_STANDARD_POSIX_1993
#endif
#if _POSIX_VERSION - 0 >= PREDEF_VERSION_POSIX_1996
# define PREDEF_STANDARD_POSIX_1996
#endif
#if _POSIX_VERSION - 0 >= PREDEF_VERSION_POSIX_2001
# define PREDEF_STANDARD_POSIX_2001
#endif
#if defined(_POSIX_VERSION)
# define PREDEF_STANDARD_POSIX _POSIX_VERSION
#endif

#if _POSIX2_C_VERSION - 0 >= 199209L
# define PREDEF_STANDARD_POSIX_1992
#endif

/* X/Open Portability Guide 3 (XPG3)*/
#define PREDEF_VERSION_XOPEN_1989 300
/* X/Open Portability Guide 4 (XPG4) */
#define PREDEF_VERSION_XOPEN_1992 400
/* X/Open Single Unix Specification (XPG4v2, UNIX95) */
#define PREDEF_VERSION_XOPEN_1995 450
/* X/Open Single Unix Specification version 2 (UNIX98) */
#define PREDEF_VERSION_XOPEN_1998 500
/* Open Group Single Unix Specification version 3 (UNIX03) */
#define PREDEF_VERSION_XOPEN_2003 600

#if (_XOPEN_VERSION - 0 >= 3) || defined(_XOPEN_XPG3)
# define PREDEF_STANDARD_XOPEN_1989
#endif
#if (_XOPEN_VERSION - 0 >= 4) || defined(_XOPEN_XPG4)
# define PREDEF_STANDARD_XOPEN_1992
#endif
#if (_XOPEN_VERSION - 0 > 4) \
 || (defined(_XOPEN_UNIX) && (_XOPEN_VERSION - 0 == 4))
# define PREDEF_STANDARD_XOPEN_1995
#endif
#if (_XOPEN_VERSION - 0 >= PREDEF_VERSION_XOPEN_1998)
# define PREDEF_STANDARD_XOPEN_1998
#endif
#if (_XOPEN_VERSION - 0 >= PREDEF_VERSION_XOPEN_2003)
# define PREDEF_STANDARD_XOPEN_2003
#endif

#if defined(PREDEF_STANDARD_XOPEN_1998)
# define PREDEF_STANDARD_XOPEN _XOPEN_VERSION
#else
# if defined(PREDEF_STANDARD_XOPEN_1995)
#  define PREDEF_STANDARD_XOPEN PREDEF_VERSION_XOPEN_1995
# else
#  if defined(PREDEF_STANDARD_XOPEN_1992)
#   define PREDEF_STANDARD_XOPEN PREDEF_VERSION_XOPEN_1992
#  else
#   if defined(PREDEF_STANDARD_XOPEN_1989)
#    define PREDEF_STANDARD_XOPEN PREDEF_VERSION_XOPEN_1989
#   endif
#  endif
# endif
#endif

/*************************************************************************
 * C Libraries
 */

#if defined(PREDEF_COMPILER_MWERKS) && defined(TARGET_API_MAC_CARBON)
# define PREDEF_LIBC_CARBON 0
/*
 * Although the Metrowerks compiler supports C99, the Carbon library
 * does not contain all C99 functions.
 */
# if defined(PREDEF_STANDARD_C99)
#  undef PREDEF_STANDARD_C99
# endif
#endif

#if defined(__GLIBC__)
# if defined(__GLIBC_MINOR__)
#  define PREDEF_LIBC_GNU ((__GLIBC__ * 10000) + \
                           (__GLIBC_MINOR__ * 100))
# else
#  define PREDEF_LIBC_GNU ((__GLIBC__ * 10000))
# endif
#else
# if defined(__GNU_LIBRARY__)
/*
 * If __GNU_LIBRARY__ is defined, but __GLIBC__ is not we are using the
 * older GNU libc rather than glibc. Libc version 6 was succeeded by glibc
 * version 2. To enable easy chronological comparison, the PREDEF_LIBC_GNU
 * macro defines the libc version number to be 100 times smaller than the
 * version number of glibc. For example, libc version 6.0 becomes 600 and
 * glibc version 2.1 becomes 20100.
 */
#  if defined(__GNU_LIBRARY_MINOR__)
#   define PREDEF_LIBC_GNU ((__GNU_LIBRARY__ * 100) + \
                            (__GNU_LIBRARY_MINOR__))
#  else
#   define PREDEF_LIBC_GNU ((__GNU_LIBRARY__ * 100))
#  endif
# endif
#endif

#if defined(__CRTL_VER)
# define PREDEF_LIBC_VMS __CRTL_VER
# if (__CRTL_VER < 80000000)
/*
 * Although the compiler supports C99 language constructs, the C
 * run-time library does not contain all C99 functions.
 *
 * This was the case for 70300022. Update the 80000000 value when
 * it has been accurately determined what version of the library
 * supports C99.
 */
#  if defined(PREDEF_STANDARD_C99)
#   undef PREDEF_STANDARD_C99
#  endif
# endif
#endif

/*************************************************************************
 * C++ Libraries
 */

#if defined(__CPPLIB_VER)
# define PREDEF_LIBCXX_DINKUM __CPPLIB_VER
#endif

#if defined(__GLIBCXX__)
# define PREDEF_LIBCXX_GNU __GLIBCXX__
#else
# if defined(__GLIBCPP__)
#  define PREDEF_LIBCXX_GNU __GLIBCPP__
# endif
#endif

#if defined(PREDEF_COMPILER_VISUALC)
# if defined(PREDEF_LIBCXX_DINKUM)
#  define PREDEF_LIBCXX_VISUALC PREDEF_LIBCXX_DINKUM
# else
#  define PREDEF_LIBCXX_VISUALC 0
# endif
#endif

#endif
