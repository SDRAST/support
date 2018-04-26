/* rmc.h -- RMC Global Constant and Type Declarations */

/* %W%	%G% */

/*---------------------------------------------------------------------------*
 |
 | Project:
 |	Equipment Activity Controller (EAC)
 |	Jet Propulsion Laboratory, Pasadena, CA
 |
 |	A description of the EAC and its vision is provided at 
 |	http://dsnra.jpl.nasa.gov/eac.html
 |
 |---------------------------------------------------------------------------
 | Revision History:
 | 
 |   Date            By               Description
 | 
 | 01-May-95     Thang Trinh        Initial Delivery
 |
 | 16-Mar-01     Tom Kuiper         Modified declaration for sys_errlist
 |                                  to handle Linux 2.2
 | 08-Mar-07	 Tom Kuiper	    Removed code for defining sys_errlist
 |                                  It is done in /usr/include/bits/sys_errlist.h
 |---------------------------------------------------------------------------
 | 
 | Description:
 |	This header file defines global type definitions and symbolic
 |	constants that are common to all RMC applications.
 |
 *--------------------------------------------------------------------------*/

#ifndef RMC_H
#define RMC_H

/* standard definitions */

#ifndef YES
#define YES 1
#endif

#ifndef NO
#define NO 0
#endif

#ifndef FALSE
#define FALSE 0
#endif

#ifndef TRUE
#define TRUE 1
#endif

#ifndef OK
#define OK 1
#endif

#ifndef ERROR
#define ERROR (-1)
#endif

#ifndef NULL
#define NULL 0
#endif

#ifndef NULLP
#define NULLP (char *)0
#endif

#ifndef IN_RANGE
#define IN_RANGE(n,lo,hi) ((lo) <= (n) && (n) <= (hi))
#endif

#ifndef MAX
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#endif

#ifndef MIN
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#endif

#ifndef SWAP
#define SWAP(a,b) ({ long tmp; tmp = (a), (a) = (b), (b) = tmp})
#endif

extern int sys_nerr;
extern __const char *__const sys_errlist[];

#ifndef SYS_ERRSTR
#define SYS_ERRSTR(_errno) (((unsigned)_errno > sys_nerr) ? \
    "Illegal errno value" : sys_errlist[_errno])
#endif

/* character definitions */

#ifndef EOS
#define EOS '\000'
#endif

#ifndef BELL
#define BELL '\007'
#endif

#ifndef LF
#define LF '\012'
#endif

#ifndef CR
#define CR '\015'
#endif 

/* integer type definitions */

typedef short	i16, I16;		/* 16-bit integer */

typedef int	i32, I32;		/* 32-bit integer */

/* bit and boolean type definitions */
 
typedef unsigned char  u8, U8;		/*  8 bits, for bitwise operations */
 
typedef unsigned short u16, U16;	/* 16 bits, for bitwise operations */
 
typedef unsigned int   u32, U32;	/* 32 bits, for bitwise operations */
 
typedef enum {
    false = 0, true = 1
} bool, boolean;

#endif /* #ifndef RMC_H */
