/* net_rdc.h -- RDC-Specific Task and End-point Name Definitions */

/* %W%	%G% */

/*---------------------------------------------------------------------------*
 |
 | PROJECT:
 |	R&D Control (RDC)
 |	Jet Propulsion Laboratory, Pasadena, CA
 |
 |	A description of the RDC, its vision and characteristics is available
 |	from http://dsnra.jpl.nasa.gov/devel/rdc/index.html
 |
 | REVISION HISTORY:
 |
 |   Date            By               Description
 |
 | 27-Nov-95      T. Trinh	   Initial Delivery.
 | 03-Oct-96	  T. Kuiper	   Modified documentation for clarity;
 |				   added additional definitions.
 | 19-Nov-96      T. Trinh	   Added antenna control servers' endpoints
 |				   and generic EAC control client.
 | 30 Jan 97      T. Kuiper        Added DMON (data server monitor) task;
 |                                 added DAVOS_SRV (DAVOS server)
 | 08 Sep 99      T. Kuiper        Made DAVOS_SRV a generic SPEC_SRV;
 |                                 added SPEC_TASK.
 |
 | DESCRIPTION:
 |	This header file maps the RDC-specific and related task names
 |	(integers defined as *_TASK) and server endpoint names
 |	(strings defined as *_SRV) onto generic task and endpoint names
 |	defined in net_appl.h.
 |
 *--------------------------------------------------------------------------*/

#ifndef NET_RDC_H
#define NET_RDC_H

#include "net_appl.h"

/* The following (numeric) task IDs are defined in net_appl.h:
	ANY_TASK (anonymous monitor clients)
	SGW_TASK (SPC LAN gateway server)
	MON_TASK (EAC monitor data server) */

/* RDC application program (numeric) ID codes */

#define ANT_TASK1	APP1_TASK	/* antenna control tasks 1-8 */
#define ANT_TASK2	APP2_TASK
#define ANT_TASK3	APP3_TASK
#define ANT_TASK4	APP4_TASK
#define ANT_TASK5	APP5_TASK
#define ANT_TASK6	APP6_TASK
#define ANT_TASK7	APP7_TASK
#define ANT_TASK8	APP8_TASK
#define CMD_TASK	APP9_TASK	/* operator command input task */

#define PCFS_TASK	APP10_TASK	/* PCFS client (or its emulators) */

#define RCTL_TASK	APP11_TASK	/* remote control client */
#define DMON_TASK	APP12_TASK	/* data server monitor client */

#define RAC_TASK	SRV2_TASK	/* RAC server */
#define SPEC_TASK	SRV11_TASK	/* spectrometer server task */

/* The following server endpoint names (strings) are used as defined in
   net_appl.h:
	SGW_SRV (SPC LAN gateway server)
	MON_SRV (EAC monitor data server) */

/* RDC-related server task and endpoint names (strings) */

#define RAC_SRV		APP_SRV2

#define ANT_SRV1	APP_SRV3	/* ant control servers' endpoints */
#define ANT_SRV2	APP_SRV4
#define ANT_SRV3	APP_SRV5
#define ANT_SRV4	APP_SRV6
#define ANT_SRV5	APP_SRV7
#define ANT_SRV6	APP_SRV8
#define ANT_SRV7	APP_SRV9
#define ANT_SRV8	APP_SRV10

#define SPEC_SRV	APP_SRV11	/* DAVOS server endpoint */

#endif /* NET_RDC_H */
