/* rmon_if.h -- Remote Monitor Subsystem Interface Declarations */

/*---------------------------------------------------------------------------*
 |
 | PROJECT:
 |	R&D Control System (RDC)
 |	Jet Propulsion Laboratory, Pasadena, CA
 |
 | REVISION HISTORY:
 |
 |   Date            By               Description
 |
 | 23-Nov-98     Tom Kuiper           created
 |
 | DESCRIPTION:
 |	This header file contains type definitions and symbolic constants
 |	for the Remote Control Subsystem external interface.
 |
 |      The Net Services Tcl toolkit does not use these definitions but
 |      constructs and decodes them on the fly.
 |
 *--------------------------------------------------------------------------*/

#ifndef RMON_IF_H
#define RMON_IF_H

#include "rdc_if.h"

/* message ID
   ----------
   This is what is put into the 'msg_id' part of the 'msg_hdr'
   structure defined in rdc_if.h.

   See eac_if.h for an explanation of the message ID.		*/

#define RMON_CMD         ((RMON_ID   << 16) | CMD)
#define RMON_RSP         ((RMON_ID   << 16) | RSP)

/* message structure definitions */

typedef struct cmd_msg RMON_CMD_MSG;
typedef struct rsp_msg RMON_RSP_MSG;

#endif /* RMON_IF_H */
