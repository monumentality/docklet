# Makefile for ACOMMDKP
VERSION=0.01

CC=gcc
OPTIM_FLAGS=-O
WARN_FLAGS=-Wall -ansi -pedantic
C99_FLAGS=-std=c99
#DEBUGMODE=-DINFOMODE -DDEBUG_CONNECTION -DDEBUG_ACO
ZSOCK_NOCHECK=-DZSOCK_NOCHECK
GLIB_FLAGS=`pkg-config --cflags --libs glib-2.0 libzmq libczmq`
CFLAGS=$(WARN_FLAGS)  ${GLIB_FLAGS} ${C99_FLAGS} $(ZSOCK_NOCHECK) $(DEBUGMODE) $(OPTIM_FLAGS) -L /lib64
# To change the default timer implementation, uncomment the line below
# or call 'make TIMER=unix'
TIMER=unix
#TIMER=unix
LDLIBS=-lm $(shell pkg-config --libs glib-2.0 libzmq libczmq) -lpthread

.PHONY: all run

all: clean acommdkp

clean:
	@$(RM) *.o acommdkp

test: utilities.o colony.o task.o connection.o mmdkp.o test.o
	${CC} -o $@ $^ ${CFLAGS} ${LDLIBS}

test.o: test.c

acommdkp: utilities.o colony.o task.o connection.o mmdkp.o test.o
	${CC} -o $@ $^ ${CFLAGS} ${LDLIBS}

utilities.o: utilities.c utilities.h

colony.o: colony.c colony.h

task.o: task.c task.h

connection.o: connection.c connection.h

mmdkp.o: mmdkp.c mmdkp.h debug.h


dist : DIST_SRC_FILES=*.c *.h README *.txt Makefile
dist : all
	@(mkdir -p ../ACOMDKP-$(VERSION)			\
	&& rsync -rlpC --exclude=.svn $(DIST_SRC_FILES) ../ACOMDKP-$(VERSION)/ \
	&& cd ..	\
	&& tar cf - ACOMDKP-$(VERSION) | gzip -f9 > ACOMDKP-$(VERSION).tar.gz \
	&& rm -rf ./ACOMDKP-$(VERSION)					\
	&& echo "ACOMDKP-$(VERSION).tar.gz created." && cd $(CWD) )
