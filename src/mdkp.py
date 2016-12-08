import copy
import math
import random
import numpy as np
from numpy.linalg import cholesky
import matplotlib.pyplot as plt

class Colony:

    alpha = 1
    beta = 3
    rho = 0.5
    xi = 0.1
    q0 = 0.8
    
    def __init__(self,tasks,ant_count = 10 ,cpus = 64,mems= 256,ratio_terms=2, stop_terms=8):
        self.ant_count = ant_count
        self.cpus = cpus
        self.mems = mems
        self.tasks = tasks
        self.ratio_terms = ratio_terms
        self.stop_terms = stop_terms

        self.tasks_to_add = {}
        self.initiation()

    def initiation(self):
        self.price_ratio = self.mems / self.cpus
        self.ants = [dict() for x in range(self.ant_count)]

        self.current_sum = 0
        self.current_solution = []
        self.current_cpus = 0
        self.current_mems = 0

        self.default_sum = 0
        self.default_pheromone = 0
        self.biggest_pheromone = 0

    def change_tasks(self):
        # 添加新task
        for key, task in self.tasks_to_add.items():
            task['heuristic'] = task['price'] / (task['cpus'] * self.price_ratio + task['mems'])
            task['pheromone'] = self.biggest_pheromone
            task['choice'] = (task['heuristic']**Colony.alpha)*(task['pheromone']** Colony.beta)
        self.tasks.update(self.tasks_to_add)
        self.tasks_to_add = {}
        # TO-DO: 删除已完成的task
        

    def init_choice_fast(self):	

        for key,task in self.tasks.items():
#            print("all task: ",task)
            task['heuristic'] = task['price'] / (task['cpus'] * self.price_ratio + task['mems'])

        tmp_cpus = 0
        tmp_mems = 0

        sorted_tasks = sorted(self.tasks.values(), key = lambda k: k['heuristic'], reverse = True)

        while len(sorted_tasks)>0:
            if tmp_cpus+ sorted_tasks[0]['cpus'] <= self.cpus and tmp_mems + sorted_tasks[0]['mems'] <= self.mems:
                tmp_cpus += sorted_tasks[0]['cpus']
                tmp_mems += sorted_tasks[0]['mems']
                self.default_sum += sorted_tasks[0]['price']
#                print("default tasks: ",sorted_tasks[0])
                del sorted_tasks[0]
            else:
                break

        print("default sum: ", self.default_sum)
        self.current_sum = self.default_sum
        self.current_cpus = tmp_cpus
        self.current_mems = tmp_mems
        self.default_pheromone = 1 / self.default_sum
        
        for key,task in self.tasks.items():
            task['pheromone'] = self.default_pheromone
            task['choice'] = (task['heuristic']**Colony.alpha)*(task['pheromone']** Colony.beta)
            #print("task: ",task)
            
    def init_choice(self):
        global tasks
        global ants
        global default_sum
        global default_pheromone
        global current_sum
        global current_cpus
        global current_mems
    
        local_tasks = copy.deepcopy(tasks)
        global_tasks = tasks
        tmp_cpus = 0
        tmp_mems = 0
    
        default_sum = 0
        while  tmp_cpus< cpus and tmp_mems < mems:
    
            sum_choice =0
            tmp_price_ratio = (mems-tmp_mems) / (cpus-tmp_cpus)
            print('ratio: ',tmp_price_ratio)
            for key,task in local_tasks.items():
                task['heuristic'] = task['price'] / (task['cpus'] * tmp_price_ratio + task['mems'])
    #            task['pheromone'] = global_tasks[key]['pheromone']
    #            task['choice'] = (task['heuristic']**alpha)*(task['pheromone']**beta)
    #            sum_choice += task['choice']
            
            sorted_tasks = sorted(local_tasks.values(), key = lambda k: k['heuristic'], reverse = True)
    #        print(sorted_tasks[0])
    
            if tmp_cpus + sorted_tasks[0]['cpus'] <= cpus and tmp_mems + sorted_tasks[0]['mems'] <= mems:
                tmp_cpus += sorted_tasks[0]['cpus']
                tmp_mems += sorted_tasks[0]['mems']
                default_sum  += sorted_tasks[0]['price']
    
                del local_tasks[str(sorted_tasks[0]['id'])]
    
            else:
                break
    
        print("default: ", default_sum)
    
        current_sum = default_sum
        current_cpus = tmp_cpus
        current_mems = tmp_mems
        default_pheromone = 1 / default_sum
    
        for key,task in global_tasks.items():
            task['pheromone'] = default_pheromone
    
            #print("task: ",task)        
                
    def choose(ant_index):
        global ants
        global xi
        global cpus
        global mems
        global tasks
        
        ants[ant_index]['cpus']=0
        ants[ant_index]['mems']=0
        ants[ant_index]['solution'] = []
        ants[ant_index]['sum']=0
    
        local_tasks = copy.deepcopy(tasks)
        global_tasks = tasks
        # 每选择一个任务后，重新排序
        # 重新计算choice数组并排序, 因为局部信息素的更新
    
        while ants[ant_index]['cpus'] < cpus and ants[ant_index]['mems'] < mems:
    
            sum_choice =0
            tmp_price_ratio = (mems-ants[ant_index]['mems']) / (cpus-ants[ant_index]['cpus'])
            for key,task in local_tasks.items():
                task = local_tasks[key]
                task['heuristic'] = task['heuristic'] = task['price'] / (task['cpus'] * tmp_price_ratio + task['mems'])
                task['pheromone'] = global_tasks[key]['pheromone']
                task['choice'] = (task['heuristic']**alpha)*(task['pheromone']**beta)
                sum_choice += task['choice']
            
                sorted_tasks = sorted(local_tasks.values(), key = lambda k: k['choice'], reverse = True)
                #print(sorted_tasks)
    
        
            q1 = np.random.uniform(0,1)
    #        print("ran: ", q1)
            if q1 <= q0:
    #            print("best choose")
                if ants[ant_index]['cpus'] + sorted_tasks[0]['cpus'] <= cpus and ants[ant_index]['mems'] + sorted_tasks[0]['mems'] <= mems:
                    ants[ant_index]['cpus'] += sorted_tasks[0]['cpus']
                    ants[ant_index]['mems'] += sorted_tasks[0]['mems']
                    ants[ant_index]['solution'].append(sorted_tasks[0]['id'])
                    ants[ant_index]['sum'] += sorted_tasks[0]['price']
    
    
    
                    # local update pheromone
                    task_id = sorted_tasks[0]['id']
                    task_pheromone = sorted_tasks[0]['pheromone']
                    global_tasks[task_id]['pheromone'] = (1-xi)*task_pheromone + xi * default_pheromone
    
                    del local_tasks[sorted_tasks[0]['id']]
    
                else:
                    break
            else:
                chosen = 0
                ran = random.uniform(0,sum_choice)
                tmp_range = 0 
                for i in range(0,len(sorted_tasks)):
                    tmp_range += sorted_tasks[i]['choice']
                    if ran <= tmp_range:
    #                    print("roulette choose")
                        chosen = i
                        break
    
                if ants[ant_index]['cpus'] + sorted_tasks[chosen]['cpus'] <= cpus and ants[ant_index]['mems'] + sorted_tasks[chosen]['mems'] <= mems:
                    ants[ant_index]['cpus'] += sorted_tasks[chosen]['cpus']
                    ants[ant_index]['mems'] += sorted_tasks[chosen]['mems']
                    ants[ant_index]['solution'].append(sorted_tasks[chosen]['id'])
                    ants[ant_index]['sum'] += sorted_tasks[chosen]['price']
    
                    # local update pheromone
                    task_id = sorted_tasks[chosen]['id']
                    task_pheromone = sorted_tasks[chosen]['pheromone']
                    global_tasks[task_id]['pheromone'] = (1-xi)*task_pheromone + xi * default_pheromone
    
                    del local_tasks[sorted_tasks[chosen]['id']]
    
    
                else:
                    break
    
    #    print("ant ", ant_index, " sum: ", ants[ant_index]['sum'])
    
    def choose_fast(self,ant_index):
        
        ant = self.ants[ant_index]
        ant['cpus']=0
        ant['mems']=0
        ant['solution'] = []
        ant['sum']=0
    
        # 重新计算choice数组并排序, 因为局部信息素的更新
        sum_choice = 0
        for key,task in self.tasks.items():
            task['choice'] = (task['heuristic']**Colony.alpha)*(task['pheromone']**Colony.beta)
            sum_choice += task['choice']
            
        sorted_tasks = sorted(self.tasks.values(), key = lambda k: k['choice'], reverse = True)
        #print(sorted_tasks)
        
        while len(sorted_tasks)>0:
            q1 = np.random.uniform(0,1)
    #        print("ran: ", q1)
            if q1 <= Colony.q0:
    #            print("best choose")
                if ant['cpus'] + sorted_tasks[0]['cpus'] <= self.cpus and ant['mems'] + sorted_tasks[0]['mems'] <= self.mems:
                    ant['cpus'] += sorted_tasks[0]['cpus']
                    ant['mems'] += sorted_tasks[0]['mems']
                    ant['solution'].append(sorted_tasks[0]['id'])
                    ant['sum'] += sorted_tasks[0]['price']
    
    
    
                    # local update pheromone
                    task_id = sorted_tasks[0]['id']
                    task_pheromone = sorted_tasks[0]['pheromone']
                    self.tasks[task_id]['pheromone'] = (1-Colony.xi)*task_pheromone + Colony.xi * self.default_pheromone
    
                    del sorted_tasks[0]
    
                else:
                    break
            else:
                chosen = 0
                ran = random.uniform(0,sum_choice)
                tmp_range = 0 
                for i in range(0,len(sorted_tasks)):
                    tmp_range += sorted_tasks[i]['choice']
                    if ran <= tmp_range:
    #                    print("roulette choose")
                        chosen = i
                        break
    
                if ant['cpus'] + sorted_tasks[chosen]['cpus'] <= self.cpus and ant['mems'] + sorted_tasks[chosen]['mems'] <= self.mems:
                    ant['cpus'] += sorted_tasks[chosen]['cpus']
                    ant['mems'] += sorted_tasks[chosen]['mems']
                    ant['solution'].append(sorted_tasks[chosen]['id'])
                    ant['sum'] += sorted_tasks[chosen]['price']
    
                    # local update pheromone
                    task_id = sorted_tasks[chosen]['id']
                    task_pheromone = sorted_tasks[chosen]['pheromone']
                    self.tasks[task_id]['pheromone'] = (1-Colony.xi)*task_pheromone + Colony.xi * self.default_pheromone
    
                    del sorted_tasks[chosen]
    
#        print("ant ", ant_index, " sum: ", ant['sum'])
    
    
    def update_choice(self):
        
        for t_id in self.current_solution:
            old_pheromone = self.tasks[t_id]['pheromone']
            new_pheromone = (1-Colony.rho) * old_pheromone + Colony.rho * self.current_sum** 1/ (self.default_sum**2)
            self.tasks[t_id]['pheromone'] = new_pheromone
    
    def update_price_ratio(self):
        
        for key,task in self.tasks.items():
            task['heuristic'] = task['price'] / (task['cpus'] * self.price_ratio + task['mems'])
#            task['pheromone'] = 1 / self.current_sum
    
    def aco_fast(self):
    
        ratio_less_index = 0
        ratio_great_index = 0
        stop_index = 0
        while not self.tasks and not self.tasks_to_add:
            time.sleep(0.1)

        if self.tasks_to_add:
            self.change_tasks()

        self.init_choice_fast()
        
        while stop_index < self.stop_terms:
            if self.tasks_to_add:
                self.change_tasks()
            if not self.tasks:
                time.sleep(0.1)
                
            
#            print("term: ", stop_index)
            for index in range(0,self.ant_count):
                status = self.choose_fast(index)
    
            solution_changed = False
            for ant in self.ants:
                if ant['sum'] > self.current_sum:
                    solution_changed = True
#                    print("found a better solution: ", ant['sum'])
                    self.current_sum = ant['sum']
                    self.current_solution = ant['solution']
                    self.current_cpus = ant['cpus']
                    self.current_mems = ant['mems']
    
            if solution_changed:
                self.update_choice()
                stop_index = 0
            else:
                stop_index +=1
                
            # 修改价格比例
#            print("left cpus/mems : ",self.cpus-self.current_cpus,self.mems-self.current_mems, self.price_ratio, ratio_great_index, ratio_less_index)
            if self.cpus- self.current_cpus == 0:
                left_ratio = float('inf')
            else:
                left_ratio = (self.mems-self.current_mems)/(self.cpus-self.current_cpus)
            if ratio_great_index > 0:
                if left_ratio >= self.price_ratio:
                    if ratio_great_index >= self.ratio_terms:
                        # increase_price_ratio()
                        #price_ratio += 1
                        if left_ratio > 1000:
                            self.price_ratio = 1000
                        else:
                            self.price_ratio = left_ratio
    #                    print("price_ratio increase")
                        self.update_price_ratio()
                        ratio_great_index = 0
                    else:
                        ratio_great_index += 1
                else:
                    ratio_great_index = 0
                    ratio_less_index +=1
            elif ratio_less_index > 0:
                if left_ratio <= self.price_ratio:
                    if ratio_less_index >= self.ratio_terms:
                        # decrease_price_ratio()
                        #self.price_ratio -= 1
                        self.price_ratio = left_ratio
    #                    print("price_ratio decreased")
                        self.update_price_ratio()
                        ratio_great_index = 0
                    else:
                        ratio_less_index +=1
                else:
                    ratio_less_index = 0
                    ratio_great_index +=1
            else:
                if left_ratio < self.price_ratio:
                    ratio_less_index += 1
                else:
                    ratio_great_index +=1
    
#        print("current: ",self.current_sum)
    
    def aco():
        global stop_index
        global stop_terms
    
        global current_sum
        global current_solution
        global current_cpus
        global current_mems
        
        global ants
    
        global price_ratio
        global ratio_terms
        global ratio_less_index
        global ratio_great_index
    
        stop_index = 0 
        init_choice()
        while stop_index <= stop_terms:
            print("term: ", stop_index)
            for index in range(0,ant_count):
                status = choose(index)
    
            solution_changed = False
            for ant in ants:
                if ant['sum'] > current_sum:
                    solution_changed = True
                    print("found a better solution: ", ant['sum'])
                    current_sum = ant['sum']
                    current_solution = ant['solution']
                    print(ant['solution'])
                    current_cpus = ant['cpus']
                    current_mems = ant['mems']
    
            if solution_changed:
                update_choice()
                stop_index = 0
            else:
                stop_index +=1
    
        
    #    n, p = 100, 0.04  # number of trials, probability of each trial
    #    s = np.random.binomial(n, p, 10000)
    
    #    s = np.random.poisson(4, 200)
    #    plt.hist(s, bins=1000)
    #    plt.show()
    
    
    #    mean = [2, 4]
    #    cov = [[1, 0], [0, 1]]  # diagonal covariance
    #    x, y = np.random.multivariate_normal(mean, cov, 200).T
    #    plt.plot(x, y, 'x')
    #    plt.axis('equal')
    #    plt.show()
    
    
    def exact(self):
        opt = [ [0 for col in range(0,self.mems+1)] for row in range(0,self.cpus+1) ]
    #    print(opt)
        for key in list(self.tasks.keys()):
            task = self.tasks[key]
            i_cpu = int(task['cpus'])
            i_mem = int(task['mems'])
            price = int(task['price'])
            for j in range(self.cpus,i_cpu-1,-1):
                for k in range(self.mems,i_mem-1, -1):
    #                print(j,k)
                    opt[j][k] = max(opt[j][k],opt[j-i_cpu][k-i_mem]+price)
    
    #    print(opt)
#        print("exact opt: ",opt[self.cpus][self.mems])
        return opt[self.cpus][self.mems]
        
def generate_test_data(cpu,mem):
    cpu_arr = np.random.binomial(cpu, 1/16, cpu*2)
    mem_arr = np.random.binomial(mem, 1/32, mem*2)
#    cpu_arr = np.random.uniform(1,cpu,cpu*2)
#    mem_arr = np.random.uniform(1,mem,cpu*2)
    prices = np.random.uniform(1,100,cpu*2)
    tasks = {}
    for i in range(0,cpu*2):
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

def test1():
    import time
    
    tasks = generate_test_data(64,256)
    colony = Colony(tasks)
    colony.initiation()
    print("begin ")
    time1 = time.clock()
    colony.init_choice_fast()
    time2 = time.clock()
    colony.aco_fast()
    time3 = time.clock()
    colony.exact()
    time4 = time.clock()
    print("greedy/exact",(time2-time1)/(time4-time3))
    print("aco/exact: ", (time3-time2)/(time4-time3))

def test2():
    import time
    dp_opt = 0
    aco_fast_opt = 0
    dp_time = 0
    aco_time = 0
    for i in range(0,1000):
        tasks = generate_test_data(64,256)
        colony = Colony(tasks)
        colony.initiation()
        time1 = time.clock()
        colony.aco_fast()
        time2 = time.clock()
        dp_time += (time2-time1)
        aco_fast_opt += colony.current_sum
        dp_opt += colony.exact()
        time3 = time.clock()
        aco_time += (time3-time2)

    print("result: ", dp_opt, aco_fast_opt, aco_fast_opt/dp_opt)

    print("time used: ", dp_time, aco_time, dp_time/aco_time)

def test3():
    return

if __name__ == '__main__':
    test2()

    

#    init_choice_fast()
#    choose(0)
    #set_parameters()
#    from timeit import Timer
#    t1=Timer("aco_fast()","from __main__ import aco_fast")
#    print(t1.timeit(100))
#    aco_fast()
#    print("aco fast defalut ",default_sum)
#    print("aco fast current ", current_sum)
#    aco()
#    init_choice()
#    print("aco defalut ",default_sum)
#    print("aco current ", current_sum)
#    t2=Timer("exact()","from __main__ import exact")
#    print(t2.timeit(100))
#    exact()
