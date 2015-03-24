/*
This creates a timer using librt to create a POSIX, per-process timer.

Compile with:
    cc timer.c -l rt -o timer
*/
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <signal.h>
#include <errno.h>
#include <math.h>

int make_timer(float delay, int interval);

int main()
{
    int             Ret;
    sigset_t        sigset;
    
    Ret = make_timer(0.5, 500);
    
    while(1)
    {
      siginfo_t info;
      sigemptyset(&sigset);
      sigaddset(&sigset,SIGUSR1);

      while(sigwaitinfo(&sigset,&info) > 0)
      {
        printf("[%d] Caught signal %d\n",(int)time(0),info.si_value.sival_int);
      }
    }
    return 0;
}