# Makefile for Net Services 3.1 under Linux

# 1993 Oct   	T. Trinh	original version
# 2001 Mar 15	kuiper		streamlined and modified to support different
#				OS versions

SRCDIR = .
INSTALLDIR = .

BINDIR = $(INSTALLDIR)
LIBDIR = $(INSTALLDIR)
MANDIR = $(INSTALLDIR)

.INIT: depend.make

CPPFLAGS =	-I../include -I../../include
		
CC = gcc
CFLAGS =	-fPIC -g -DLINUX

INSTALLLIBS =	/usr/bin/install -m 644 $(LIBDIR)

LDFLAGS =	-L$(LIBDIR)

LDLIBS =	-lnetsrv -lsocket -lnsl

LINTFLAGS = -u 

LIB_SRCS = net_endpt.c net_io.c net_tcp.c report_errno.c

LIB_OBJS =	$(LIB_SRCS:.c=.o)
SHLIB_SUFFIX =	.so

SHLIB_LD =	/usr/bin/ld -G -z text
SHLIB_LD_LIBS =	${PKG_LIBS} -lnetsrv


libnet_srv.so:: ${LIB_OBJS}
	$(CC) -c $(CFLAGS) ${LIB_SRCS}
	${SHLIB_LD} -G -z text -o libnet_srv.so ${LIB_OBJS}

$(LIBDIR)/$(LIB): $(LIB)
	$(INSTALLLIBS)

clean::
	@rm -f *~
	@rm -f core
	rm -f *.o

install:: libnet_srv.so
	cp libnet_srv.so /usr/local/lib/libnet_srv.so

depend.make:
	@touch depend.make
