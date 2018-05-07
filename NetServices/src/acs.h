/* acs.h -- ACS Global Type Declarations */

/* %W%	%G% */

/*----------------------------------------------------------------------------
 * Copyright (c) 1993-1995, Jet Propulsion Laboratory
 * Permission is granted to make and distribute copies of this software
 * without fee, provided the above copyright notice and this permission notice
 * are preserved on all copies.  All other rights reserved.  The software is
 * provided "as is" without express or implied warranty, and no representation
 * is made about its suitability for any purpose.
 *
 * Revision History:
 * 
 *   Date            By               Description
 * 
 * 12-Oct-93     Thang Trinh        Initial release (v1.0).
 * 
 * Description:
 *	This header file defines global type definitions and symbolic
 *	constants that are common to all ACG common services.
 *
 *--------------------------------------------------------------------------*/

#ifndef ACS_H
#define ACS_H

#ifndef SUCCESS
#define SUCCESS 0
#endif

#ifndef ERROR 
#define ERROR (-1) 
#endif

#ifndef NULL
#define NULL 0
#endif

#define ALREADY_INITIALIZED	(-2)
#define NOT_INITIALIZED		(-3)

typedef enum {
	BLOCKING = 0,           /* return after I/O completes */
	NON_BLOCKING = 1        /* return immediately, I/O done or not */
} io_mode;
 
#endif /* #ifndef ACS_H */

#ifdef LINUX
/* needed for Linux  */
#ifndef FIONBIO
#include "linux/ioctl.h"
#define FIONBIO _IOW('f',126,int)
#endif 
#endif 
