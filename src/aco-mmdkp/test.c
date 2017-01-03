#define ZSOCK_NOCHECK

#include "task.h"
#include "utilities.h"
#include "connection.h"
#include "mmdkp.h"
#include "debug.h"

int test_while(){
  for(;;){
    printf("sleep! \n");
    //    sleep(1);
  }
}
int main(){
  //    test_while();
  //  test_glist();
  //  test_gtable();
  //  test_g_task();
  //  test_init_colony();
  //  test_choose();
  //  test_roanoke();
  //  test_sub();
  //  test_roanoke();
  //    test_run();
  test_main_thread();
  return 0;
}
