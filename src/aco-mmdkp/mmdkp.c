#include "connection.h"
#include "pthread.h"
#include "utilities.h"
#include "debug.h"

void *colony_thread(Colony *colony){
  DEBUGC("in thread, before run colony\n");
  run(colony);
  return NULL;
}
int create_and_run_colony_thread(char *colonyid, int cpus, int mems){
  DEBUGC("create thread %s\n",colonyid);
  Colony *colony = init_colony(colonyid, NULL, 10, cpus, mems, 1, 6);
  pthread_t *thread =malloc(sizeof(pthread_t));
  pthread_create(thread,NULL, colony_thread, colony);

  return 0;
}

int destroy_colony_thread(){

  return 0;
}

int main_thread(){
  setbuf(stdout, NULL);
  DEBUGC("old max sockets: %ld\n",zsys_socket_limit());
  zsys_set_max_sockets(100000);
  DEBUGC("old max sockets: %ld\n",zsys_socket_limit());
  zsys_handler_set(NULL);
  s_catch_signals();
  // 5001用来同步sub，5000用于sub，5002用于主进程接受创建销毁pthread
  zsock_t *rep = zsock_new_rep("tcp://*:5002");
  DEBUGC("waiting for mmdkp sync request... \n");
  char * sync_msg = zstr_recv(rep);
  DEBUGC("recv mmdkp sync request: %s\n",sync_msg);

  free(sync_msg);
  zstr_send(rep,"mmdkp sync success");
  DEBUGC("mmdkp sync done \n");

  //  zpoller_t * poller = zpoller_new(rep,NULL);
  //  assert(poller);

  while(1){
    char *oper = zstr_recv(rep);
    char *id = zstr_recv(rep);
    char *cpus = zstr_recv(rep);
    char *mems =zstr_recv(rep);
    DEBUGC("recevice new thread request: %s %s %s %s\n", oper,id, cpus,mems);
    zstr_send(rep,"new colony success");
    
    create_and_run_colony_thread(strdup(id), strtol(cpus,NULL,10),strtol(mems,NULL,10));
    
    DEBUGC("after create thread! \n");
    zstr_free(&oper);
    zstr_free(&id);
    zstr_free(&cpus);
    zstr_free(&mems);
    //  }
  }
      //  zpoller_destroy(&poller);
  zsock_destroy(&rep);

  return 0;
}

int test_main_thread(){
  main_thread();
  return 0;
}
