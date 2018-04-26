/* rdc_if.h -- RDC External Interface Top Level Definitions */

/* %W%	%G% */

/*---------------------------------------------------------------------------*
 |
 | PROJECT:
 |	R&D Control System
 |	Jet Propulsion Laboratory, Pasadena, CA
 |
 |	A description of the RDC is available
 |	from http://dsnra.jpl.nasa.gov/devel/rdc/
 |
 | REVISION HISTORY:
 |
 |   Date            By               Description
 |
 | 09-Feb-96      T. Trinh	    Initial Delivery of EAC of 'eac_if.h'
 | 30-Jun-96      T. Kuiper         Added interfaces for RAC to 'eac_if.h'
 | 15-Nov-96      T. Kuiper         added new definitions to 'eac_if.h'
 | 03-Feb-97      T. Kuiper         replaced with 'rdc_if.h'
 | 02-Feb-98      T. Kuiper         added SPEC_ID
 | 24-Nov-98      T. Kuiper         moved subsystem specific definitions
 |                                  to separate files
 |
 | DESCRIPTION:
 |	This header file contains general definitions for the RDC external
 |	interfaces, excluding the 890-131 interface.  It currently contains
 |	definitions for the
 |            EAC      Equipment Activity Controller
 |            PCFS     PC Field System
 |            RAC      Radio Astronomy Controller
 |            RCTL     Remote Controller
 |            RMON     Remote Monitor
 |            SPEC     Spectrometer Controller
 |
 |      General message structures are defined in this file. Message
 |      structure definitions for specific subsystems are in separate
 |      include files for each interface, e.g., rac_if.h
 |
 *--------------------------------------------------------------------------*/

#ifndef RDC_IF_H
#define RDC_IF_H

#include "rmc.h"


/* subsystem ID
   -------------
   Used in the subsystem header files to construct the 'msg_id'.
   These are the most significant 16 bits of msg_id
   used to create unique message IDs along with message type.
   
   The reason for having them together here is so that it is easier
   to assign new subsystem IDs, without having to check all the
   subsystem header files.					*/

#define EAC_ID		1	/* EAC subsystem		*/
#define PCFS_ID		2	/* PCFS subsystem		*/
#define RAC_ID		3	/* RAC subsystem		*/
#define RMON_ID		4	/* Remote monitor subsystem	*/
#define RCTL_ID		5	/* Remote control subsystem	*/
#define SPEC_ID		6	/* Spectrometer subsystem	*/
#define SRVR_ID		7	/* Unspecified server		*/


/* message ID 
   ----------
   Most significant 16 bits are subsystem ID (defined above).
   The l.s. 8 bits are message type (1 - command, 2 - response).
   Here are some message types that every subsystem uses.	*/

#define CMD	1
#define RSP	2

/* Here's an example of how a message ID is constructed for a
   subsystem XX.

   #define XX_CMD		((XX_ID  << 16) | CMD)
   #define XX_RSP		((XX_ID  << 16) | RSP)

   Part of the message ID field is used for the message size.
   Bits 8-15 contain a message size code which specifies the
   length of the message as 128 * (size_code+1); thus, the
   default message size is 128 bytes, and the maximum size
   is 32768.  If other than the default of 0, the program must
   insert this into the message ID field.


   Definitions for commonly used message structures
   ------------------------------------------------

	(Message structures specific to a subsystem are in the
	subsystem's header file.)				*/

typedef struct msg_hdr {
	U32	msg_id;		/* defined above	*/
	U32	src_id;		/* sender application id (see net_eac.h) */
} MSG_HDR;


/* The following defines default structures for command and response
   messages. The message length must be < NET_MAX_MSG_LEN, which is
   currently 32768; see net.h	*/
   
#define MAX_CMD_LEN	128
#define MAX_RSP_LEN	128

typedef struct cmd_msg {
	MSG_HDR hdr;
	char	cmd[MAX_CMD_LEN];
} CMD_MSG;

typedef struct rsp_msg {
	MSG_HDR hdr;
	char	rsp[MAX_RSP_LEN];
} RSP_MSG;

#endif /* RDC_IF_H */
