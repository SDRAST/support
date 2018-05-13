/* spec_if.h -- Spectrometer Interface Declarations */

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
 |	for spectrometer external interface.
 |
 |      The Net Services Tcl toolkit does not use these definitions but
 |      constructs and decodes them on the fly.
 |
 *--------------------------------------------------------------------------*/

#ifndef SPEC_IF_H
#define SPEC_IF_H

#include "rdc_if.h"

/* message ID
   ----------
   This is what is put into the 'msg_id' part of the 'msg_hdr'
   structure defined in rdc_if.h.

   See eac_if.h for an explanation of the message ID.		*/

#define SPEC_CMD         ((SPEC_ID   << 16) | CMD)
#define SPEC_RSP         ((SPEC_ID   << 16) | RSP)

/* message structure definitions */

typedef struct cmd_msg SPEC_CMD_MSG;
typedef struct rsp_msg SPEC_RSP_MSG;

#endif /* SPEC_IF_H */
