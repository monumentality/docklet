import math
import random
import numpy as np
from mdkp import Colony
from bidscheduler4 import AllocationOfMachine
import heapq


task_queue = []

machines = []

tasks = {}

def generate_test_tasks(cpu,mem,machines):
    global tasks
    tasks = {}
#    cpus = np.random.binomial(test_cpus, test_cpus/16, test_cpus*2)
#    mems = np.random.binomial(test_mems, test_mems/16, test_mems*2)
    cpu_arr = np.random.uniform(1,cpu,cpu*machines)
    mem_arr = np.random.uniform(1,mem,cpu*machines)
    prices = np.random.uniform(1,100,cpu*machines)
    for i in range(0,cpu*machines):
        if cpu_arr[i]==0 or mem_arr[i] ==0:
            continue

        task = {
            'id': str(i),
            'cpus': math.floor(cpu_arr[i]),
            'mems': math.floor(mem_arr[i]),
            'price': int(prices[i])
        }
        key = str(i)
        
        tasks[key] = task    
    #    print(task)
    return tasks

def init_machines(cpus,mems,num):
    global machines
    machines = []
    for i in range(0,num):
        machine = AllocationOfMachine()
        machine.machineid = str(i)
        machine.cpus = cpus
        machine.mems = mems
        machine.colony = Colony({},cpus=cpus,mems=mems)
        machine.tasks = {}
        machine.total_value = 0
        # to-do:改成多线程，直接运行每个线程
        # machine.colony.run()

        heapq.heappush(machines,machine)

# 从task_queue中取出最大的，从machines中取出最小的，放置
def dispatch(tasks):
    for key,task in tasks.items():
        price = int(0 - task['price'])
        heapq.heappush(task_queue,(price,task['id'],task))

    # the following is only for test
    while task_queue:
        neg_price,id, task = heapq.heappop(task_queue)
        machine = heapq.heappop(machines)
        machine.add_task(task)

        heapq.heappush(machines,machine)


def mdp(tasks,cpus,mems):

#    print(max(1,2,3))
#    print("numpy array: ")
#    print(np.zeros((2,4,2,4)))
    opt = np.zeros((cpus+1,mems+1,cpus+1,mems+1))
    #    print(opt)
    for key,task in tasks.items():
        cpu = int(task['cpus'])
        mem = int(task['mems'])
        price = int(task['price'])
        for i in range(cpus,0,-1):
            for j in range(mems,0, -1):
                for k in range(cpus,0,-1):
                    for l in range(mems,0,-1):
                #                print(i,j,k,l)
                        if not (i< cpu or j< mem) and not (k < cpu or l<mem):
                            opt[i][j][k][l] = max(opt[i][j][k][l],opt[i][j][k-cpu][l-mem]+price,opt[i-cpu][j-mem][k][l]+price)
                        elif (i <cpu or j<mem) and not (k<cpu or l<mem):
                            opt[i][j][k][l] = max(opt[i][j][k][l],opt[i][j][k-cpu][l-mem]+price)
                        elif not (i<cpu or j<mem) and (k<cpu or l<mem):
                            opt[i][j][k][l] = max(opt[i][j][k][l],opt[i-cpu][j-mem][k][l]+price)

                        # 两台机器都不能放的时候什么都不用做
    #print(opt)
    print("exact opt: ",opt[cpus][mems][cpus][mems])
    return opt[cpus][mems][cpus][mems]

def relax_mdp(tasks,cpus,mems,machines):

    cpus = cpus*machines
    mems = mems * machines
    opt = np.zeros((cpus+1,mems+1))
    for key,task in tasks.items():
        i_cpu = int(task['cpus'])
        i_mem = int(task['mems'])
        price = int(task['price'])
        for j in range(cpus,i_cpu-1,-1):
            for k in range(mems,i_mem-1, -1):
                #                print(j,k)
                opt[j][k] = max(opt[j][k],opt[j-i_cpu][k-i_mem]+price)
    
    #    print(opt)
    print("relax opt: ",opt[cpus][mems])
    return opt[cpus][mems]
    
if __name__ == '__main__':

    relax = 0
    exact = 0
    aco  = 0 
    for i in range(0,1):
        
        tasks = generate_test_tasks(16,64,1000)
#        relax += relax_mdp(tasks,16,64,10)
#        exact += mdp(tasks,16,64)
        
        init_machines(16,64,1000)
        dispatch(tasks)
        
        aco_fast_result = 0
        for machine in machines:
            machine.colony.aco_fast()
            #machine.colony.exact()
            aco_fast_result += machine.colony.current_sum
            
            print("aco fast result: ",aco_fast_result)

        aco += aco_fast_result

#    print("exact/relax: ", exact/relax)
#    print("aco/exact: ", aco/exact)
#    print("aco/relax: ", aco/relax)
    print("aco: ",aco)
    
