# Makefile for ACOMMDKP
VERSION=0.01

CC=gcc
OPTIM_FLAGS=-O
WARN_FLAGS=-Wall -ansi -pedantic
C99_FLAGS=-std=c99
DEBUGMODE=-DINFOMODE
ZSOCK_NOCHECK=-DZSOCK_NOCHECK
GLIB_FLAGS=`pkg-config --cflags --libs glib-2.0 libzmq libczmq`
CFLAGS=$(WARN_FLAGS)  ${GLIB_FLAGS} ${C99_FLAGS} $(ZSOCK_NOCHECK) $(DEBUGMODE) $(OPTIM_FLAGS)
# To change the default timer implementation, uncomment the line below
# or call 'make TIMER=unix'
TIMER=unix
#TIMER=unix
LDLIBS=-lm $(shell pkg-config --libs glib-2.0 libzmq libczmq)

.PHONY: all run

all: clean acomdkp

clean:
	@$(RM) *.o acomdkp

test: utilities.o colony.o task.o knapsack.o connection.o mmdkp.o test.o
	${CC} -o $@ $^ ${CFLAGS}

test.o: test.c

acomdkp: acomdkp.o utilities.o colony.o task.o kanpsack.o

acomdkp.o: acomdkp.c
	${CC} -o $@ $^ ${CFLAGS}

utilities.o: utilities.c utilities.h

colony.o: colony.c colony.h

task.o: task.c task.h

knapsack.o: knapsack.c knapsack.h

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
