SHLIB_LD =      /usr/bin/ld -G -z text
SHLIB_SUFFIX =  .so
CC_SWITCHES =   -g -c -fPIC

timer : timer.o user_timer.o
	gcc -lrt -o timer timer.o user_timer.o

user_timer.so : user_timer.o
	gcc user_timer.c ${CC_SWITCHES}
	${SHLIB_LD} user_timer.o -lrt -o user_timer.so

*.o : *.c