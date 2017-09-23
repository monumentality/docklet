#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>

#define CPUS 64
#define MEMS  256

#ifndef MACHINES
#define  MACHINES  1
#endif

#ifndef DIS
#define  DIS "uniform"
#endif

#ifndef CORR
#define  CORR "corr0"
#endif

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
long int compute_relax_opt(){
  long int row = MACHINES * CPUS;
  long int column = MACHINES * MEMS;
  //  printf("row,colum, %ld %ld %ld: \n",row,column,n_tasks);
  //  printf("here\n");
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
  return opt[row][column];
}

void writefile(long int result){
  FILE * fp;
  char filename[100];
  sprintf(filename, "../../test_result/quality_opt_%s_%s_%d.txt", DIS, CORR, 100); 
  if((fp=fopen(filename,"a"))==NULL){
    printf("Cannot open file strike any key exit!");
    exit(1);
  }
  fprintf(fp,"%d %ld\n",MACHINES, result);
  fclose(fp);
}
  
int main(int argc, char *argv[]){
  //init_tasks();
  printf("machines: %d \n",MACHINES);
  char buffer[100];
  sprintf(buffer,"../../test_data/%s%s_tasks%d.txt",DIS,CORR,MACHINES);
  printf("%s",buffer);
  tasks = parse(buffer);
  long int result = compute_relax_opt();
  writefile(result);

  return 0;
}
