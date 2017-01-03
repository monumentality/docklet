#include <glib.h>
#include "czmq.h"
typedef struct Ant{
  int cpus;
  int mems;
  long result;
  GList *solution;
} Ant;

typedef struct Colony{
  int alpha;
  int beta;
  double rho;
  double xi;
  double q0;

  char *id;
  int cpus;
  int mems;
  double ratio;
  int ratio_terms;
  int stop_terms;
  int stop_index;

  GHashTable *tasks;

  Ant* *ants;
  int n_ant;

  long default_result;
  double default_pheromone;

  long current_result;
  GList *current_solution;
  int current_cpus;
  int current_mems;

  int initial_result;
  int *initial_solution;
  int *initial_pheromone;

  GHashTable *tasks_to_add;
  int biggest_pheromone;

  int cpus_wanted;
  int mems_wanted;
  int is_full;
  int tasks_changed;
  int result_ready;

  //socket
  zsock_t *task_socket;
  zpoller_t *task_poller;
  zsock_t *result_socket;
} Colony;

Colony *init_colony(char *colonyid, GHashTable *tasks,int n_ant,int cpus, int mems, int ratio_terms, int stop_terms);

void *init_choice(Colony *colony);

void *choose(Colony *colony, int i_ant);

void *update_pheromone(Colony *colony);

void *update_ratio(Colony *colony);

void *roanoke();

void *run();

void *test_init_colony();

void *test_choose();

void *test_roanoke();

void *test_run();
