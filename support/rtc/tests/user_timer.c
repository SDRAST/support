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

int make_timer(float delay, int interval)
{
    int             Ret;
    int             status;
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
    status = timer_create(CLOCK_REALTIME, &sig, &timerone);
    if (status == 0)
    {
        struct itimerspec in, out;
        /* relative time to the start of the timer */
        in.it_value.tv_sec     = 0;
        in.it_value.tv_nsec    = (delay * powl(10,9));
        /* timer interval */
        in.it_interval.tv_sec  = 0;
        in.it_interval.tv_nsec = (interval * powl(10,6));// fire every 50 ms
        Ret = timer_settime(timerone, 0, &in, &out);
        if (Ret != 0)
        {
            fprintf(stderr, "timer_settime() failed with %d\n", errno);
            fflush(stderr);
        }
    }
    else
    {
        fprintf(stderr, "timer_create() failed with %d\n", errno);
        fflush(stderr);
        Ret = errno;
        exit(1);
    }
    return Ret;
}
