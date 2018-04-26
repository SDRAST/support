/* fs_if.h --  Field System Interface Declarations */

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
 |	for the "PC Field System" Subsystem external interface.
 |
 |      The Net Services Tcl toolkit does not use these definitions but
 |      constructs and decodes them on the fly.
 |
 *--------------------------------------------------------------------------*/

#ifndef FS_IF_H
#define FS_IF_H

#include "rdc_if.h"

/* message ID
   ----------
   This is what is put into the 'msg_id' part of the 'msg_hdr'
   structure defined in rdc_if.h.

   See eac_if.h for an explanation of the message ID.		*/

#define FS_CMD         ((PCFS_ID   << 16) | CMD)
#define FS_RSP         ((PCFS_ID   << 16) | RSP)

/* message structure definitions */

typedef struct cmd_msg FS_CMD_MSG;
typedef struct rsp_msg FS_RSP_MSG;

#endif /* FS_IF_H */
