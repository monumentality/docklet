#include "task.h"
#include "utilities.h"
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <glib.h>
#include <assert.h>
#include <string.h>
#include "debug.h"

#define PRECISE 1e-10

GHashTable *generate_test_tasks(int cpus,int mems){
  GHashTable *tasks = NULL;
  tasks = g_hash_table_new_full(g_str_hash, g_str_equal,free_key,free_value);
  //  if((tasks = malloc(sizeof(Task)* cpus)) == NULL){
  //    printf("out of memory! exit.");
  //  }
    srand( (unsigned)time(NULL) );
  for (int i =1; i<cpus*10; i++){

    char *key = malloc(sizeof(char)*10);
    sprintf(key, "%d",i);

    Task *task = malloc(sizeof(Task));
    task->id = key;
    double tcpus = (double)rand()/RAND_MAX * cpus +1;
    double tmems = (double)rand()/RAND_MAX * mems +1;
    double tvalue = (double)rand()/RAND_MAX *100 +1;
    task->cpus = tcpus;
    task->mems = tmems;
    task->value = tvalue;

    g_hash_table_insert(tasks,key,task);

    //    Task *lookup =  (Task *)g_hash_table_lookup(tasks, key);
    //    printf("%d %d %d \n", lookup->cpus, lookup->mems, lookup->value);

  }
  return tasks;
}

int test_generate(){
  GHashTable *tasks =generate_test_tasks(64,256);
  printf("size of hash table: %d \n\n\n\n", g_hash_table_size(tasks));

  for(int i=1;i<64;i++){
    char key[10];
    sprintf(key,"%d",i);
    Task *task =  (Task *)g_hash_table_lookup(tasks, key);
    assert(task != NULL);
    printf("%d %d\n", task->cpus, task->mems);
  }
  g_hash_table_destroy(tasks);
  return 0;
}

int cmp_heuristic(gconstpointer p1, gconstpointer p2){
    if(((Task*)p1)->heuristic - ((Task*)p2)->heuristic < PRECISE) return 1;
    if(((Task*)p1)->heuristic - ((Task*)p2)->heuristic > PRECISE) return -1;
    return 0;
    return( ((Task*)p1)->choice - ((Task*)p2)->choice);
}

int cmp_choice(gconstpointer p1, gconstpointer p2){
    if(((Task*)p1)->choice - ((Task*)p2)->choice < PRECISE) return 1;
    if(((Task*)p1)->choice - ((Task*)p2)->choice > PRECISE) return -1;
    return 0;
  //    return( ((Task*)p1)->choice  ((Task*)p2)->choice);
}
