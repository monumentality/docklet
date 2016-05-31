#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>

#define MEM 1000000000


int main(){
  time_t begin, end;
  long i;
  char * c = calloc(MEM,sizeof(char));
  c[0]=0;

  while(1){
    /* Get the current time. */
    begin = time (NULL);

    for( i = 0;i<MEM;i++){
      c[i]=0;
    }
    end = time(NULL);

      //    sleep(difftime(end,begin));
  }
}
