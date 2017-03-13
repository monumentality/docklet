#include "connection.h"
#include "task.h"
#include "utilities.h"
#include "debug.h"

int init_sockets(Colony *colony){

  char * sub_key = malloc(strlen(colony->id)+8);
  strcpy(sub_key, colony->id);
  strcat(sub_key, " ");
  DEBUGC("subscribe: %s!\n",sub_key);
  colony->task_socket = zsock_new_sub("tcp://localhost:5000",sub_key);

  colony->task_poller = zpoller_new(colony->task_socket,NULL);

  assert(colony->task_poller);

  colony->result_socket = zsock_new_req("tcp://localhost:5003");

  sync_sockets(colony);
  return 0;

}

int sync_sockets(Colony *colony){
  //    sleep(5);
  zsock_t *req = zsock_new_req("tcp://localhost:5001");

  zstr_send(req,colony->id);

  char * go = zstr_recv(req);
  DEBUGC("sync reply: %s\n",go);
  free(go);
  zsock_destroy(&req);
  DEBUGC("sync done \n");
  return 0;
}

int recv_tasks(Colony *colony){
  while(!s_interrupted){
    zsock_t *which = zpoller_wait(colony->task_poller, 0);

    if (which != NULL){
      char *machineid = zstr_recv(which);

      char *id = zstr_recv(which);
      char *cpus = zstr_recv(which);
      char *mems = zstr_recv(which);
      char *value = zstr_recv(which);
      char *oper = zstr_recv(which);

      if(strcmp(oper,"add")==0){
        Task *task = malloc(sizeof(Task));
        task->id = strdup(id);
        task->cpus = strtol(cpus,NULL,10);
        task->mems = strtol(mems,NULL,10);
        task->value = strtol(value,NULL,10);

	DEBUGC("machine %s add one task: id:%s cpus:%d mems:%d value:%d \n", colony->id,task->id, task->cpus, task->mems, task->value);

        task->heuristic = (double)task->value/(task->cpus * colony->ratio + task->mems);
        task->pheromone = colony->biggest_pheromone;

        g_hash_table_insert(colony->tasks,task->id,task);

        colony->tasks_changed =1;

        // 修改所有任务的cpu，mem总和，计算是否已满
        colony->cpus_wanted += task->cpus;
        colony->mems_wanted += task->mems;
        if(colony->cpus_wanted > colony->cpus || colony->mems_wanted > colony->mems) colony->is_full =1;

      }else if(strcmp(oper,"delete")==0){

	DEBUGC("machine %s delete one task: id:%s\n", colony->id, id);
        //任务是否变化了
        colony->tasks_changed =1;
        // 修改所有任务的cpu，mem总和，计算是否已满
        colony->cpus_wanted -= strtol(cpus,NULL,10);
        colony->mems_wanted -= strtol(mems,NULL,10);
        if(colony->cpus_wanted <= colony->cpus && colony->mems_wanted <= colony->mems) colony->is_full =0;

	Task *task = g_hash_table_lookup(colony->tasks,id);
	if(g_list_find(colony->current_solution,task->id)!=NULL){
	  DEBUGC("task to delete is in solution!\n");
	  colony->current_result -= task->value;
	}
	colony->current_solution = g_list_remove(colony->current_solution, task->id);
	DEBUGC("delete %s, result change to %ld \n", task->id, colony->current_result);
	
        g_hash_table_remove(colony->tasks, id);

      }else{
        DEBUGC("oper wrong: $%s$\n",oper);
      }
      zstr_free(&machineid);
      zstr_free(&id);
      zstr_free(&cpus);
      zstr_free(&mems);
      zstr_free(&value);
      zstr_free(&oper);
      continue;
    }
    else{
      //      DEBUGC("no message\n");
      break;
    }
  }
  return 0;
}


int destroy_sockets(Colony *colony){
  zpoller_destroy(&colony->task_poller);
  zsock_destroy(&colony->task_socket);
  return 0;
}

int test_sub(){
  Colony *colony = init_colony(0,NULL,4,4,16,1,8);
  init_sockets(colony);
  for(int i=0;i<10;i++){
    recv_tasks(colony);
    DEBUGC("aco run 1s\n");
    sleep(1);
  }
  destroy_sockets(colony);
  return 0;
}

int send_result(Colony *colony){

  DEBUGC("send current_solution of machine %s...\n",colony->id);
  // convert current_solution to string
  int solution_length = g_list_length(colony->current_solution);
  char *solution = malloc(20 * solution_length);
  GList *iter = NULL;
  long index =0;
  for(iter = colony->current_solution; iter; iter = iter->next)
    {
      char *id = (char *)(iter->data);
      index += sprintf(&solution[index], "%s ", id);
    }
  solution[index-1]='\0';
  DEBUGC("send current_solution of machine %s: %s$\n", colony->id, solution);

  //convert current_mem_value to string
  char *mem_value = malloc(32);
  sprintf(mem_value,"%e", colony->current_mem_value);
  DEBUGC("send current_mem_value of machine %s: %s$\n", colony->id, mem_value);

  //convert ratio to string
  char *ratio = malloc(32);
  sprintf(ratio,"%e", colony->ratio);
  DEBUGC("send ratio of machine %s: %s$\n", colony->id, ratio);
  
  // send message
  zstr_sendm(colony->result_socket, colony->id);
  zstr_sendm(colony->result_socket, solution);
  zstr_sendm(colony->result_socket, mem_value);
  zstr_send(colony->result_socket, ratio);
  

  char *result_reply = zstr_recv(colony->result_socket);
  DEBUGC("result reply: %s\n",result_reply);

  free(result_reply);

  free(solution);
  free(mem_value);
  free(ratio);
  return 0;
}
