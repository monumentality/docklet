#include <stdio.h>
#include <time.h>
#include <unistd.h>

int main(){
  time_t begin, end;
  long i;
  char c[1000000000];

  while(1){
    /* Get the current time. */
    begin = time (NULL);

    for( i = 0;i<100000;i++);

    end = time(NULL);

    sleep(difftime(end,begin));
  }
}
