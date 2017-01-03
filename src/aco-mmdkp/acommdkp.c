#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>

#define CPUS 64
#define MEMS  256
#define  MACHINES  20
#define PRICES  100

typedef struct Task{
  int cpus;
  int mems;
  int price;
} Task;

Task *tasks;

long int n_tasks = CPUS * MACHINES;

long int opt[CPUS * MACHINES+1][MEMS * MACHINES +1];

void init_tasks(){
  if((tasks = malloc(sizeof(Task)* n_tasks)) == NULL){
    printf("out of memory! exit.");
  }
  srand( (unsigned)time(0) );
  for (int i =1; i<n_tasks; i++){
    tasks[i] = (Task){ rand()%64+1,rand()%256+1, rand()%100+1};
    //    printf("%d %d %d \n",tasks[i].cpus, tasks[i].mems, tasks[i].price);
  }

}

Task * parse(char *filename){
  if((tasks = malloc(sizeof(Task)* n_tasks)) == NULL){
    printf("out of memory! exit.");
  }
  FILE * fp;
  if((fp=fopen(filename,"r"))==NULL){
    printf("Cannot open file strike any key exit!");
    exit(1);
  }
  for( int i =0;i<n_tasks;i++){
    fscanf(fp,"%d %d %d\n",&tasks[i].cpus, &tasks[i].mems,&tasks[i].price);
    //    printf("%d %d %d\n",tasks[i].cpus,tasks[i].mems,tasks[i].price);
  }
  fclose(fp);
  return tasks;
}
void compute_relax_opt(){
  long int row = MACHINES * CPUS;
  long int column = MACHINES * MEMS;
  printf("row,colum, %ld %ld %ld: ",row,column,n_tasks);
  printf("here\n");
  int cpus,mems,price;
  for (long int i=0; i< n_tasks ;i++){

    cpus = tasks[i].cpus;
    mems = tasks[i].mems;
    price = tasks[i].price;
    // printf("i: %ld %d %d %d\n",i,cpus,mems,price);
    for (long int j=row;j>=cpus;j--){
      for(int long k =column; k >=mems;k--){
        opt[j][k] = (opt[j][k] > (opt[j-cpus][k-mems]+price) ? opt[j][k] : (opt[j-cpus][k-mems] + price));
      }
    }
  }
  printf("%ld\n", opt[row][column]);
}

int main(int argc, char *argv[]){
  //init_tasks();
  tasks = parse("uniform_tasks.txt");
  compute_relax_opt();


  return 0;
}
