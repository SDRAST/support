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

int main()
{
    int             Ret;
    sigset_t        sigset;
    struct sigevent sig;
    timer_t         timerone;
    
    sigemptyset(&sigset);
    sigaddset(&sigset,SIGUSR1);
    
    sigprocmask(SIG_BLOCK,&sigset,NULL);

    /* This timer uses a set-table system-wide realtime clock.
       The second argument points to a sigevent structure that specifies  how
       the caller should be notified when the timer expires (see sigevent(7)).
       Upon timer expiration, the timer generates  the  signal SIGUSR1 for the
       process.
       The third argument is a pointer to a buffer with the timer ID.
    */
    sig.sigev_notify = SIGEV_SIGNAL;    /* timer emits a signal when expired */
    sig.sigev_signo = SIGUSR1;          /* timer uses SIGUSR1 */
    sig.sigev_value.sival_int =20;      /* timer ID */
    sig.sigev_notify_attributes = NULL; /* see pthread_attr_init(3) */
    Ret = timer_create(CLOCK_REALTIME, &sig, &timerone);

    if (Ret == 0)
    {
        struct itimerspec in, out;
        /* relative time to the start of the timer */
        in.it_value.tv_sec     = 0;
        in.it_value.tv_nsec    = (0.5 * powl(10,9));
        /* timer interval */
        in.it_interval.tv_sec  = 0;
        in.it_interval.tv_nsec = (50 * powl(10,6));// fire every 50 ms
        Ret = timer_settime(timerone, 0, &in, &out);
    }
    else
    {
        printf("timer_create() failed with %d\n", errno);
        exit(1);
    }
    Ret = 0;
    
    while(1)
    {
      siginfo_t info;
      sigemptyset(&sigset);
      sigaddset(&sigset,SIGUSR1);

      while(sigwaitinfo(&sigset,&info)>0)
      {
        printf("[%d] Caught signal %d\n",(int)time(0),info.si_value.sival_int);
      }
    }
    return 0;
}