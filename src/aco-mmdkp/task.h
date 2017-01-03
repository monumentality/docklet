#include <glib.h>

typedef struct Task{
  char *id;
  int cpus;
  int mems;
  int value;
  double pheromone;
  double heuristic;
  double choice;
} Task;

GHashTable *generate_test_tasks(int cpus,int mems);

int test_generate();

int cmp_heuristic(gconstpointer p1, gconstpointer p2);

int cmp_choice(gconstpointer p1, gconstpointer p2);
