#define _XOPEN_SOURCE

#include "utilities.h"
#include <stdio.h>
#include <glib.h>
#include <stdlib.h>
#include <czmq.h>
#include "debug.h"
#include <signal.h>



int s_interrupted =0;

void s_signal_handler(){
  s_interrupted =1;
  zsys_interrupted =1;
  printf("interupted! \n");
}

void s_catch_signals(void){
  struct sigaction action;
  action.sa_handler = s_signal_handler;
  action.sa_flags = 0;
  sigemptyset( &action.sa_mask);

  sigaction(SIGINT, &action, NULL);
  sigaction(SIGTERM, &action, NULL);
}

void free_key(gpointer data)
{
  //  DEBUGC("hashtable free key: %s \n", data);
  free(data);

}

void free_value(gpointer data)
{
  //  DEBUGC("hashtable free value\n");
  free(data);

}

int test_glist() {
  GList* list = NULL;
  list = g_list_append(list, "Hello world!");
  printf("The first item of the glist is '%s'\n", g_list_first(list)->data);
  return 0;


}

int test_gtable(){
  GHashTable *table = NULL;

  table = g_hash_table_new(g_str_hash, g_str_equal);

  g_hash_table_insert(table, "1", "one");
  g_hash_table_insert(table, "2", "two");
  g_hash_table_insert(table, "3", "three");
  g_hash_table_insert(table, "4", "four");
  g_hash_table_insert(table, "5", "five");

  printf("Size of hash table: %d \n", g_hash_table_size(table));

  printf("Before replace: 3 ---> %s \n", g_hash_table_lookup(table, "3"));
  g_hash_table_replace(table, "3", "third");
  printf("After replace: 3 ---> %s \n", g_hash_table_lookup(table, "3"));

  g_hash_table_remove(table, "2");
  //  display_hash_table(table);
  printf("Now size of hash table: %d \n", g_hash_table_size(table));

  g_hash_table_destroy(table);

  return 0;
}
