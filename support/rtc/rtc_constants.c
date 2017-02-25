/* Compile with
 *   gcc rtc_constants.c -o rtc_constants
 */
 
#include <linux/rtc.h> /* for RTC...   */
#include <stdio.h>     /* for printf   */
#include <sys/ioctl.h> /* needed by linux/rtc.h */

int main(int argc, char **argv)
{
  printf("RTC_IRQP_SET = %x\n", RTC_IRQP_SET);
  printf("RTC_PIE_ON   = %x\n", RTC_PIE_ON);
  printf("RTC_PIE_OFF  = %x\n", RTC_PIE_OFF);
  printf("RTC_UIE_ON   = %x\n", RTC_UIE_ON);
  printf("RTC_UIE_OFF  = %x\n", RTC_UIE_OFF);
  printf("RTC_RD_TIME  = %x\n", RTC_RD_TIME);
  printf("RTC_ALM_SET  = %x\n", RTC_ALM_SET);
  printf("RTC_ALM_READ = %x\n", RTC_ALM_READ);
  printf("RTC_AIE_ON   = %x\n", RTC_AIE_ON);
  printf("RTC_AIE_OFF  = %x\n", RTC_AIE_OFF);
  printf("RTC_IRQP_READ= %x\n", RTC_IRQP_READ);
  printf("RTC_IRQP_SET = %x\n", RTC_IRQP_SET);
}