#include "task.h"
#include "utilities.h"
#include "connection.h"

#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <glib.h>
#include <math.h>

#include "debug.h"


Colony *init_colony(char *colonyid, GHashTable *tasks,int n_ant,int cpus, int mems, int ratio_terms, int stop_terms){
  Colony* colony = (Colony*)malloc(sizeof(Colony));
  colony->id = colonyid;
  if(tasks!=NULL){
    colony->tasks =tasks;
  }else{
    colony->tasks = g_hash_table_new_full(g_str_hash, g_str_equal,free_key,free_value);
  }
  colony->n_ant = n_ant;
  colony->cpus = cpus;
  colony->mems = mems;
  colony->ratio_terms = ratio_terms;
  colony->stop_terms = stop_terms;
  colony->stop_index = 0;

  colony->ratio = (double)colony->mems / colony->cpus;

  colony->ants = (Ant**)malloc(sizeof(Ant*)*n_ant);
  for(int i=0;i<n_ant;i++){
    colony->ants[i] = (Ant*)malloc(sizeof(Ant));
    colony->ants[i]->cpus =0;
    colony->ants[i]->mems =0;
    colony->ants[i]->result =0;
    colony->ants[i]->solution = NULL;
  }
  colony->current_result = 0;
  colony->current_cpus = 0;
  colony->current_mems = 0;
  colony->current_solution = NULL;

  colony->default_result = 0;
  colony->default_pheromone =1;
  colony->biggest_pheromone =1;

  //if is full
  colony->cpus_wanted =0;
  colony->mems_wanted =0;
  colony->tasks_changed =0;
  colony->is_full = 0;

  //默认参数
  colony->alpha = 1;
  colony->beta =2;
  colony->rho = 0.1;
  colony->xi = 0.1;
  colony->q0 = 0.5;
  return colony;
}
void * destroy_colony(Colony *colony){
  free(colony->ants);
  g_list_free(colony->current_solution);
  g_hash_table_destroy(colony->tasks);
  return NULL;
}

void *init_choice(Colony *colony){
  double ratio = colony->ratio;

  GList *sorted = NULL;
  GHashTableIter iter;
  gpointer key, value;
  g_hash_table_iter_init (&iter, colony->tasks);
  while (g_hash_table_iter_next (&iter, &key, &value))
    {

      Task * task = (Task*)value;
       task->heuristic = (double)task->value/(task->cpus * ratio + task->mems);

      sorted = g_list_insert_sorted(sorted,task,cmp_heuristic);
      //      printf("task %d %d %d %d %f \n",task->id,task->cpus,task->mems,task->value, task->heuristic);
    }
  int tmp_cpus = 0;
  int tmp_mems = 0;
  GList *iter_s = NULL;
  for( iter_s = sorted;iter_s;iter_s = iter_s->next)
    {
      Task * task = (Task *)iter_s->data;
      //      printf("task %d %d %d %d \n",task->id,task->cpus,task->mems,task->value);
      if( (task->cpus +tmp_cpus <= colony->cpus) && (task->mems + tmp_mems <= colony->mems) )
        {
          tmp_cpus += task->cpus;
          tmp_mems += task->mems;
          colony->default_result += task->value;
        }
      else break;
    }

  colony->current_cpus = tmp_cpus;
  colony->current_mems = tmp_mems;
  colony->current_result = colony->default_result;
  colony->default_pheromone = (double)colony->default_result;
  printf("default sum / pheromone : %ld  %f \n",colony->default_result, colony->default_pheromone);



  for(iter_s = sorted;iter_s;iter_s = iter_s->next){
    Task *task = (Task*)iter_s->data;
    task->pheromone = colony->default_pheromone;
    task->choice = pow(task->heuristic, colony->alpha) * pow(task->pheromone, colony->beta);
    printf("task info  heu choice: %s %d %d %d %e %e \n",task->id, task->cpus, task->mems, task->value, task->heuristic, task->choice);
  }
  g_list_free(sorted);

  update_ratio(colony);
  return NULL;
}

void * choose(Colony *colony, int i_ant){
  Ant * ant = colony->ants[i_ant];
  ant->cpus =0;
  ant->mems =0;
  ant->result=0;
  ant->solution=NULL;
  DEBUGA("ant %dth: %d %d \n", i_ant,ant->cpus, ant->mems);

  double sum_choice = 0;

  //重新计算choice并排序，由于局部信息素更新

  GList *sorted = NULL;
  GHashTableIter iter;
  gpointer key, value;
  g_hash_table_iter_init (&iter, colony->tasks);
  while (g_hash_table_iter_next (&iter, &key, &value))
    {
      Task * task = (Task*)value;
      task->choice = pow(task->heuristic, colony->alpha) * pow(task->pheromone, colony->beta);

      sorted = g_list_insert_sorted(sorted,task,cmp_choice);
      //      DEBUGA("task %d %d %d %d %f \n",task->id,task->cpus,task->mems,task->value, task->heuristic);

      sum_choice += task->choice;
    }

  //  srand( (unsigned)time(NULL) );
  while( g_list_length(sorted) > 0)
    {
      double q1 = rand() / (double)RAND_MAX;
      //      DEBUGA("q1: %f \n",q1);
      // 伪随机方式，q1>q0时，选择最大的
      if( q1 < colony->q0)
        {
          Task * task = (Task *)sorted->data;

          if( (task->cpus +ant->cpus <= colony->cpus) && (task->mems + ant->mems <= colony->mems) )
            {
              //          DEBUGA("best choice: %d %d %d %d %e \n", task->id, task->cpus, task->mems, task->value, task->choice);
              ant->cpus += task->cpus;
              ant->mems += task->mems;
              ant->result += task->value;
              ant->solution = g_list_append(ant->solution, task->id);

              //local_update pheromone
              task->pheromone = (1-colony->xi) * task->pheromone + colony->xi * colony->default_pheromone;

              //从sorted中删除这个task
              sorted = g_list_remove(sorted,task);
              // 从sum_choice中减去这个的
              sum_choice -= task->choice;
            }
          else break;
        }
      // q1<=q0时，轮盘赌
      else
        {
          Task * chosen =NULL;
          double tmp_sum = 0;

          double q2 = rand() / (double)RAND_MAX * sum_choice;
          //       DEBUGA("rouletten random %e \n", q2);
          GList *iter_sor = NULL;
          for(iter_sor = sorted; iter_sor; iter_sor = iter_sor->next)
            {
              Task * task = (Task *) iter_sor->data;
              tmp_sum += task->choice;
              if(tmp_sum >= q2 )
                {

                  chosen = task;
                  break;
                }
            }
          if( (ant->cpus +chosen->cpus <= colony->cpus) && (ant->mems + chosen->mems <= colony->mems))
            {
              //              DEBUGA("rouletten choose  %s \n",chosen->id);
              ant->cpus += chosen->cpus;
              ant->mems += chosen->mems;
              ant->result += chosen->value;
              ant->solution = g_list_append(ant->solution, chosen->id);

              //local_update pheromone
              chosen->pheromone = (1-colony->xi) * chosen->pheromone + colony->xi * colony->default_pheromone;

              //从sorted中删除这个task
              sorted = g_list_remove(sorted,chosen);
              // 从sum_choice中减去这个的
              sum_choice -= chosen->choice;
            }
          else break;

        }

    }
  DEBUGA("ant %dth reslut: %ld \n",i_ant, ant->result);
  GList * iter_slt = NULL;

  for(iter_slt = ant->solution; iter_slt; iter_slt = iter_slt->next ){
    char * data = (char *)iter_slt->data;
    //    DEBUGA("solution : %s \n", data);
  }

  return NULL;
}

void * roanoke(Colony *colony){

  if( colony->stop_terms - colony->stop_index )
    {
      DEBUGA("\nterm %dth: \n", colony->stop_index);
      int result_changed=0;
      int biggest_ant_index =0;
      long biggest_result = colony->current_result;
      for(int i=0; i< colony->n_ant;i++)
        {
          choose(colony, i);
          //          printf("after ant %dth choose, result: %ld \n", i, (colony->ants)[i]->result);
          if( colony->ants[i]->result > biggest_result)
            {
              result_changed = 1;
              biggest_ant_index = i;
              biggest_result = colony->ants[i]->result;

            }
          colony->current_result = biggest_result;
        }
      if(result_changed)
        {
          DEBUGA("\n\n\nresult changed!\n");
          colony->current_result = biggest_result;
          colony->current_solution = colony->ants[biggest_ant_index]->solution;
          colony->current_cpus = colony->ants[biggest_ant_index]->cpus;
          colony->current_mems = colony->ants[biggest_ant_index]->mems;

          colony->stop_index =0;

          update_ratio(colony);
        }
      else
        {
          colony->stop_index ++;
        }
      update_pheromone(colony);


    }
  else
    {
      // do nothing
    }
  return NULL;

}

void *update_pheromone(Colony *colony){
  GList *iter = NULL;
  for(iter = colony->current_solution; iter; iter = iter->next)
    {
      char *id = (char *)(iter->data);
      DEBUGA("update pheromone id: %s \n",id);
      Task *task = g_hash_table_lookup(colony->tasks, id);
      task->pheromone = (1-colony->rho) * task->pheromone + colony->rho * colony->current_result;

      colony->biggest_pheromone = colony->biggest_pheromone > task->pheromone? colony->biggest_pheromone : task->pheromone;
    }

  return NULL;
}

void *update_ratio(Colony *colony){

  // 修改ratio
  double left_ratio = colony->ratio;
  if(colony->cpus - colony->current_cpus)
    {
      left_ratio = (double)(colony->mems - colony->current_mems) / (colony->cpus - colony->current_cpus);
    }
  else
    {
      left_ratio = 256;
    }
  if(colony->ratio != left_ratio)
    {
      DEBUGA("\n\nupdate ratio: %e --> %e \n", colony->ratio, left_ratio);
      colony->ratio = left_ratio;
    }

  GHashTableIter iter;
  gpointer key, value;
  g_hash_table_iter_init (&iter, colony->tasks);
  while (g_hash_table_iter_next (&iter, &key, &value))
    {

      Task * task = (Task*)value;
      task->heuristic = (double)task->value/(task->cpus * colony->ratio + task->mems);

      //      printf("task %d %d %d %d %f \n",task->id,task->cpus,task->mems,task->value, task->heuristic);
    }
  return NULL;
}

void *run(Colony *colony){
  zsys_handler_set(NULL);
  s_catch_signals();
  init_sockets(colony);

  while(!s_interrupted){
    recv_tasks(colony);

    if(colony->is_full){
      if(colony->tasks_changed) {
        colony->stop_index -= 1;
        colony->tasks_changed = 0;
        sleep(6);
      }
      if(colony->stop_terms > colony->stop_index){
        roanoke(colony);
        colony->result_ready =1;
      }else{
        if(colony->result_ready){
          INFO("\n colony %s current_result %ld\n", colony->id, colony->current_result);

          send_result(colony);
          colony->result_ready = 0;
        }
        //        DEBUGA("sleep\n");
        sleep(6);
      }
    }else{
        //        DEBUGA("sleep\n");
        sleep(6);
    }
  }

  return NULL;
}

void *test_init_colony(){
  GHashTable *tasks =generate_test_tasks(64,256);
  Colony *colony =init_colony("0",tasks,10,64,256,1,8);
  printf("num of ant: %d \n",colony->n_ant);
  init_choice(colony);
  Task *task = g_hash_table_lookup(colony->tasks,"2");
  printf("heu of id 2: %f \n" ,task->heuristic);
  destroy_colony(colony);
}

void *test_choose(){
  GHashTable *tasks =generate_test_tasks(64,256);
  Colony *colony =init_colony("0",tasks,10,64,256,1,8);
  printf("num of ant: %d \n",colony->n_ant);
  init_choice(colony);
  choose(colony,0);
  Task *task = g_hash_table_lookup(colony->tasks,"2");
  printf("heu of id 2: %f \n" ,task->heuristic);
  destroy_colony(colony);
}

void *test_roanoke(){

  GHashTable *tasks =generate_test_tasks(64,256);
  Colony *colony =init_colony("0",tasks,4,64,256,1,8);
  init_choice(colony);
  while(colony->stop_terms - colony->stop_index){
    roanoke(colony);
  }

  destroy_colony(colony);
  return NULL;
}

void *test_run(){

  Colony *colony =init_colony("0",NULL,4,64,256,1,8);
  run(colony);


  destroy_colony(colony);
  destroy_sockets(colony);
  return NULL;
}
