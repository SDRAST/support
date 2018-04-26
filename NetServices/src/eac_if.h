/* eac_if.h -- EAC Interface Declarations */

/*---------------------------------------------------------------------------*
 |
 | PROJECT:
 |	Equipment Activity Controller (EAC)
 |	Jet Propulsion Laboratory, Pasadena, CA
 |
 |	A description of the EAC, its vision and characteristics is available
 |	from http://dsnra.jpl.nasa.gov/eac.html
 |
 | REVISION HISTORY:
 |
 |   Date            By               Description
 |
 | 11-Aug-97	 Thang Trinh	      Initial Delivery
 | 23-Nov-98     Tom Kuiper           moved add'l EAC subsystem definitions
 |                                    (EAC_CMD, EAC_RSP, etc.) to subsystem
 |                                    header files
 |
 | DESCRIPTION:
 |	This header file contains type definitions and symbolic constants
 |	for the equipment activity controller external interface.
 |
 *--------------------------------------------------------------------------*/

#ifndef EAC_IF_H
#define EAC_IF_H

#include "rdc_if.h"

/* message ID
   ----------
   This is what is put into the 'msg_id' part of the 'msg_hdr'
   structure defined in rdc_if.h.

   Most significant 16 bits are subsystem ID (defined above)
   l.s. 8 bits are message type (1 - command, 2 - response)
   bits 8-15 contain a message size code which specifies the
     length of the message as 128 * (size_code+1); thus, the
     default message size is 128 bytes, and the maximum size
     is 32768                                                   */

#define EAC_CMD         ((EAC_ID   << 16) | CMD)
#define EAC_RSP         ((EAC_ID   << 16) | RSP)
#define EAC_ANT_ASG	((EAC_ID   << 16) | 3)
#define EAC_LINK_UNASG	((EAC_ID   << 16) | 4)
#define EAC_EVENT	((EAC_ID   << 16) | 5)
#define EAC_MON_DATA	((EAC_ID   << 16) | 6)

/* The reason for constructing the message ID in this way, instead of using
a structure definition, is that one can't be sure how a given machine
allocates storages to items that are less than a 4-byte word in size.
So, a structure consisting of a short (two bytes) and two char's (one byte
each), might actually occupy three four-byte words, or 12 bytes in memory
instead of four. So, we can't be sure that the byte pattern from one machine
maps into the correct structure on another. */


/* message structure definitions */

typedef struct cmd_msg EAC_CMD_MSG;
typedef struct rsp_msg EAC_RSP_MSG;

typedef struct ant_asg_msg {
	MSG_HDR	hdr;
	int	antno;
	int	linkno;
} ANT_ASG_MSG;

typedef struct link_unasg_msg {
	MSG_HDR	hdr;
	int	linkno;
} LINK_UNASG_MSG;

#endif /* EAC_IF_H */
