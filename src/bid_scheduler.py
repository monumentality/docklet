

#  from monitor import summary_resources, summary_usage, curr_usage
#  from monitor import summary_usage_per_user, summary_usage_per_user
#  from monitor import curr_usage_per_machine
from log import logger
import nodemgr
import bisect, uuid,json
import random
import copy
from timeit import Timer
class AllocationOfTask(object):
    __slots__ = 'id','userid','jobid','taskid','resources','bidprice','type','machineid','lxc_name','cpus','mems','dominant_price','charge'
    def __key(self):
        return (self.userid, self.jobid, self.taskid)
    def __hash__(self):
        return hash(self.__key())
    def __lt__(self, other):
        if self.dominant_price < other.dominant_price:
            return True
        else:
            return False
    def __le__(self, other): 
        if self.dominant_price <= other.dominant_price:
            return True
        else:
            return False
    def __eq__(self, other):
        return self.__key()==other.__key()
    def __ne__(self, other):
        return self.dominant_price != other.dominant_price
    def __gt__(self, other):
        if self.dominant_price > other.dominant_price:
            return True
        else:
            return False
    def __ge__(self, other):
        if self.dominant_price >=  other.dominant_price:
            return True
        else:
            return False
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def __repr__(self):
        return str({
            'id': self.id,
            'userid': self.userid,
            'jobid': self.jobid,
            'taskid': self.taskid,
            'cpus': self.cpus,
            'mems': self.mems,
            'bidprice': self.bidprice,
            'charge':self.charge,
            'type': self.type,
            'machineid':self.machineid,
            'lxc-name':self.lxc_name
        })

    def __str__(self):
        return str({
            'id': self.id,
            'userid': self.userid,
            'jobid': self.jobid,
            'taskid': self.taskid,
            'cpus': self.cpus,
            'mems': self.mems,
            'bidprice': self.bidprice,
            'dominant_price':self.dominant_price,
            'type': self.type,
            'machineid':self.machineid,
            'lxc-name':self.lxc_name
        })
     
class AllocationOfMachine(object):
    __slots__ = ['machineid',"resources","reliable_available",
                 'reliable_allocations', 'restricted_allocations',
                 'cpus','mems','cpu_price','mem_price','cpus_available','mems_available',
                 'cpu_compact','mem_compact', 'dominant_queue',
                 'opt','opt_complementary','tasks','reliable_arrays','restricted_arrays']
    def __lt__(self, other):
        if self.reliable_available < other.reliable_available:
            return True
        else:
            return False
    def __le__(self, other):
        if self.reliable_available <= other.reliable_available:
            return True
        else:
            return False
    def __eq__(self, other):
        if self.reliable_available == other.reliable_available:
            return True
        else:
            return False
    def __ne__(self, other):
        if self.reliable_available != other.reliable_available:
            return True
        else:
            return False
    def __gt__(self, other):
        if self.reliable_available > other.reliable_available:
            return True
        else:
            return False
    def __ge__(self, other):
        if self.reliable_available >=  other.reliable_available:
            return True
        else:
            return False

# 集群状态
active_machines = 0
machine_allocation_dict = {}
cpu_compact = False
mem_compact = False

usages_list=[]
machine_usage_dict = {}

# 分配状态
# 全部的分配，按估值排了序
reliable_allocations = []
unreliable_allocations = []

allocated_reliable_cpus = 0
allocated_reliable_mems = 0
allocated_reliable_cpu_mem_ratio = 1

reliable_allocation_dict = {}
unreliable_allocation_dict = {}


# 按每台机器分开，废弃
allocations_list = []

# 等待队列，按估值排序
reliable_waiting_queue = []
unreliable_waiting_queue = []

machine_allocation_dict = {}


node_manager = {}
lxcname_allocation_dict = {}
max_cpu = 4
max_mem = 8

# 寻找最稀疏的机器
def findSparseMachine():
    return

# 通过迁移平衡机器
def balanceMachines():
    return


def init_allocations():
    global machine_allocation_dict
    global allocations_list
    global node_manager
    global usages_list
    global machine_usage_dict
    print("init allocations")
    machines = node_manager.get_allnodes()
    for machine in machines:
        allocation = AllocationOfMachine()
        allocation.machineid = machine
        allocation.resources = 2
        allocation.reliable_available = 0
        allocation.reliable_allocations = []
        allocation.restricted_allocations = []
        
        machine_allocation_dict[machine] = allocation
        bisect.insort(allocations_list,allocation)
        
        usage_of_machine = {}
        usage_of_machine['machineid']=machine
        usage_of_machine['cpu_utilization']=0.1
        
        usages_list.append(usage_of_machine)
        machine_usage_dict[machine] = 0.1
        
        #logger.info(allocations_list)
        #logger.info(allocations_dic)

        
def addNode(machineid, cpus=10, mems=10):
    global machine_allocation_dict
    global allocations_list
    global node_manager
    global usages_list
    global machine_usage_dict

    #3.0
    global active_machines
    global reliable_allocations
    
    #logger.info("add node")

    active_machines += 1
    
    allocation = AllocationOfMachine()
    allocation.machineid = machineid
    allocation.resources = 3
    allocation.reliable_available = 3
    allocation.reliable_allocations = []
    allocation.restricted_allocations = []

    allocation.cpus = cpus
    allocation.mems = mems
    allocation.cpus_available = 64
    allocation.mems_available = 340
    allocation.cpu_price = 16
    allocation.mem_price = 1
    allocation.cpu_compact = False
    allocation.mem_compact = False
    allocation.dominant_queue = []

    #4.0
    allocation.tasks = []
    allocation.opt = [[[0 for i in range(allocation.mems+1)] for i in range(allocation.cpus+1)]]

    #allocation.opt = []
    allocation.opt_complementary = []
    allocation.reliable_arrays = []
    
    bisect.insort(allocations_list,allocation)
    
    usage_of_machine = {}
    usage_of_machine['machineid']=machineid
    usage_of_machine['cpu_utilization']=0.1
    
    usages_list.append(usage_of_machine)
    machine_usage_dict[machineid] = 0.1
    



def dp_allocate_task(allocation_of_machine, task_allocation_request):
    tasks = allocation_of_machine.tasks
    allocation_of_machine.tasks.append(task_allocation_request)
    step = len(allocation_of_machine.tasks)
#    print("step:",step)
    cpus = int(task_allocation_request['cpus'])
    mems = int(task_allocation_request['mems'])
    bid = int(task_allocation_request['bidprice'])

        
    opt = allocation_of_machine.opt
    opt.append([[0 for i in range(allocation_of_machine.mems+1)] for i in range(allocation_of_machine.cpus+1)])

#    print(opt)

    opt_complementary = allocation_of_machine.opt_complementary


    # 注意range的用法i in range(a,b,-1), 那么 i<=a, i>b
    for opt_com in opt_complementary:
        for i in range(allocation_of_machine.cpus, cpus-1,-1):
            for j in range(allocation_of_machine.mems, mems-1,-1):
                opt_com[i][j] = max( opt_com[i-cpus][j-mems] + bid, opt_com[i][j])

    b = copy.deepcopy(opt[step-1])
    opt_complementary.append(b)

#    print(opt_complementary)    
#    print(opt)
    for i in range(allocation_of_machine.cpus, cpus-1,-1):
            for j in range(allocation_of_machine.mems, mems-1,-1):
                opt[step][i][j] = max( opt[step-1][i-cpus][j-mems]+bid, opt[step-1][i][j])

#    print(opt)
    # 倒推计算出 最优解集：
    allocation_of_machine.reliable_arrays = []
    tmp_opt = opt[step][allocation_of_machine.cpus][allocation_of_machine.mems]
    tmp_cpus = allocation_of_machine.cpus
    tmp_mems = allocation_of_machine.mems
    # 注意step序列与task下标序列差1
    for i in range(step,0,-1):
            i_cpus = int(allocation_of_machine.tasks[i-1]['cpus'])
            i_mems = int(allocation_of_machine.tasks[i-1]['mems'])
            i_bid = int(allocation_of_machine.tasks[i-1]['bidprice'])
            if opt[i-1][tmp_cpus-i_cpus][tmp_mems-i_mems]+ i_bid > opt[i-1][tmp_cpus][tmp_mems]:
                allocation_of_machine.reliable_arrays.append(i-1)
                tmp_opt -= i_bid
                tmp_cpus -= i_cpus
                tmp_mems -= i_mems
                if tmp_opt == 0:
                    break

#    print("reliable sets: ")
#    print(allocation_of_machine.reliable_arrays)
    allocation_of_machine.reliable_allocations = []
    for i in allocation_of_machine.reliable_arrays:
        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = tasks[i]['userid']
        allocation_of_task.jobid = tasks[i]['jobid']
        allocation_of_task.taskid = i
        #            allocation_of_task.resources = job_allocation_request['resources']
        allocation_of_task.cpus = tasks[i]['cpus']
        allocation_of_task.mems = tasks[i]['mems']
        allocation_of_task.bidprice = int(tasks[i]['bidprice'])
        allocation_of_task.machineid = allocation_of_machine.machineid
        allocation_of_task.lxc_name = (allocation_of_task.userid
                                       + "-"
                                       + str(allocation_of_task.jobid)
                                       + "-"
                                       + str(allocation_of_task.taskid))
        allocation_of_task.type = 'reliable'

        # 实际收费：容器的边际成本
        # 容器的边际成本 = 用户出价 - 总价值最优解 + 不分配该容器时的总价值最优解
        allocation_of_task.charge = (allocation_of_task.bidprice -
                                     opt[step][allocation_of_machine.cpus][allocation_of_machine.mems] +
                                     opt_complementary[i][allocation_of_machine.cpus][allocation_of_machine.mems])
        allocation_of_machine.reliable_allocations.append(allocation_of_task)


#    print(opt)
    print(allocation_of_machine.reliable_allocations)
    
def has_restricted_resources(allocation_of_machine,task_allocation_request):
    if(task_allocation_request['resources']
       + machine_usage_dict[allocation_of_machine.machineid]
       < allocation_of_machine.resources * 0.8):
        return True
    else:
        return False


def allocate_task_restricted(allocation_of_machine,task_allocation_request):
    if(has_restricted_resources(allocation_of_machine,task_allocation_request)):
        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = task_allocation_request['userid']
        allocation_of_task.jobid = task_allocation_request['jobid']
        allocation_of_task.taskid = task_allocation_request['taskid']
        allocation_of_task.resources = task_allocation_request['resources']
        allocation_of_task.bidprice = task_allocation_request['bidprice']
        allocation_of_task.resources = task_allocation_request['resources']
        allocation_of_task.machineid = allocation_of_machine.machineid
        allocation_of_task.lxc_name = (allocation_of_task.userid
                                       + "-"
                                       + str(allocation_of_task.jobid)
                                       + "-"
                                       + str(allocation_of_task.taskid))
        allocation_of_task.type = 'restricted'
        bisect.insort(allocation_of_machine.restricted_allocations, allocation_of_task)
        lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task
        return {'status':'success', 'allocation':allocation_of_task}

    else:
        return {'status': 'failed'}




# 在不考虑迁移和负载不可预测的情况下，给出一个精确算法：
# A1. 收到请求(ci,mi,vi),
#     计算所有机器上的opt(C-ci,M-mi)+vi-OPT(C,M)，选择最大的放入，O(m)复杂度，m为机器数
#     如果该请求在所有机器上的边际收益都小于等于0，不分配资源，加入全局等待队列
#     全局等待队列长度需要做限制，降低计算时间

# A2. 等待队列应用于释放资源时
#     当某台机器m有资源释放后，从m上的不可靠资源任务和全局等待队列中挑选边际收益最大的请求
#     这一步很困难


# B1: 对于只用不可靠资源的请求, 立即尝试分配不可靠资源, 选择最饱和的机器,如果资源利用率不高,即分配
# B2: 如果不能分配,并且愿意等待,放入不可靠资源的等待队列


def dispatch(job_allocation_request):
    global reliable_waiting_queue
    global unreliable_waiting_queue

#    print("dispatch request")
    cpus = int(job_allocation_request['cpus'])
    mems = int(job_allocation_request['mems'])
    bid = int(job_allocation_request['bidprice'])
    allocated = 0
    allocations = []
    count = job_allocation_request['tasks_count']    

    if (job_allocation_request['once_for_all']==True):
        could_accept = 0
        for a in allocations_list:
            for i in range(1, min(count+1,a.cpus//cpus,a.mems//mems)):
                if  a.opt[-1][a.cpus-i*cpus][a.mems-i*mems]+i*bid > a.opt[-1][a.cpus][a.mems]:
                    could_accept +=1
                    if could_accept == count:
                        break
                # TO-DO: 这里可能有问题：或许存在在某个机器上放一个container不行，但可以放两个
                    

            if could_accept == count:
                break

        # 如果可以分配，那么开始一个一个分配
        if could_accept == count:
 #           print("can allocate")
            allocated = count
            for j in range(1,count+1):
                max_margin = 0 
                max_margin_index = 0
                tmp_margin = 0
                a = {}

                for i in range(0,len(allocations_list)):
                    a = allocations_list[i]
                    tmp_margin = a.opt[-1][a.cpus-cpus][a.mems-mems]+bid > a.opt[-1][a.cpus][a.mems]
                    if tmp_margin > max_margin:
                        max_margin = tmp_margin
                        max_margin_index = i
#                print("max_margin_index: ", max_margin_index)
                allocations.append(dp_allocate_task(allocations_list[max_margin_index],job_allocation_request))

            job_allocation_request['allocated'] = allocated
            job_allocation_request['allocation'] = allocations

#        else:
#            print("wait")
            # 放入等待队列

    else:

        for j in range(1,count+1):
            max_margin = 0 
            max_margin_index = 0
            tmp_margin = 0
            a = {}
            
            for i in range(0,len(allocations_list)):
                a = allocations_list[i]
                tmp_margin = a.opt[-1][a.cpus-cpus][a.mems-mems]+bid > a.opt[-1][a.cpus][a.mems]
                if tmp_margin > max_margin:
                    max_margin = tmp_margin
                    max_margin_index = i

            if max_margin > 0:
                allocated += 1 
                allocations.append(dp_allocate_task(allocations_list[max_margin_index],job_allocation_request))
            else:
                break

#        print("allocated: ", allocated)
        job_allocation_request['allocated'] = allocated
        job_allocation_request['allocations'] = allocations
        
#        if allocated < count:
            # 放入等待队列
#            print('wait')

            
    
# A3: 如果once_for_all == False, 每台机器可以分配就立即分配; 依次挑选最饱和的机器，查看能分配多少可靠资源, 能分配一个container就立即分配一个
# A4: 如果once_for_all==true,依次检查每个机器能分配几个container,如果所有机器能分配的总量不够,那么返回资源不够,继续等待.如果足够分配,才进行分配.    
def allocate_reliable(job_allocation_request):

    print ("try allocate reliable")
    global machine_allocation_dict
    global allocations_list
    job_allocation_response = []

    job_allocation_request['available'] = 0
    job_allocation_request['allocated'] = []
    job_allocation_request['allocated_count'] = 0
    if (job_allocation_request['once_for_all']==False): 
        for a in allocations_list:
            task_allocations = allocate_on_each(a,job_allocation_request)
            print(job_allocation_request)
            job_allocation_request['allocated'] = task_allocations
            job_allocation_request['allocated_count'] = len(task_allocations)
            if job_allocation_request['tasks_count'] == len(job_allocation_request['allocated']):
                break
        if job_allocation_request['tasks_count'] == len(job_allocation_request['allocated']):
            return 'success'
        else:
            return 'failed'

    else:
        for a in allocations_list:
            task_allocations = pre_allocate_on_each(a,job_allocation_request)

            job_allocation_request['allocated'] = task_allocations
            job_allocation_request['allocated_count'] = len(task_allocations)

        if job_allocation_request['tasks_count'] == len(job_allocation_request['allocated']):
            for a in allocations_list:
                task_allocations = allocate_on_each(a,job_allocation_request)
                
                job_allocation_request['allocated'] = task_allocations
                job_allocation_request['allocated_count'] = len(task_allocations)
                print(job_allocation_request)
                return 'success'
                
        else:
            job_allocation_request['allocated'] = []
            job_allocation_request['allocated_count'] = 0

            return 'failed'

#        print(job_allocation_request)

# 1. 删除该任务所占的资源,从每个机器的已分配队列中删除
# 2. 从该台物理上的不可靠资源和全局等待队列中,挑选最合适的任务

def release_reliable(job_release_request):
    # 取出等待队列中价值最大的那一个,尝试分配
    job_allocation_request = reliable_waiting_queue[len(reliable_waiting_queue)-1]
    job_allocation_response = allocate_reliable(job_allocation_request)
    if job_allocation_response['status']=='success':
        return 'success',job_allocation_response
    else:
        return 'failed'



def release_allocation(lxc_name):
    allocation_of_task = lxcname_allocation_dict[lxc_name]
    allocation_of_machine = machine_allocation_dict[allocation_of_task.machineid]
    if allocation_of_task.type == "reliable":
        i = bisect.bisect_left(allocation_of_machine.reliable_allocations,allocation_of_task)
        del allocation_of_machine.reliable_allocations[i]
    else:
        i = bisect.bisect_left(allocation_of_machine.restricted_allocations,allocation_of_task)
        del allocation_of_machine.restricted_allocations[i]
    return

def change_cgroup_settings(lxc_name, type):
    global lxcname_allocation_dict
    global node_manager
    allocation_of_task = lxcname_allocation_dict[lxc_name]
    configuration = {
        'resources': allocation_of_task.resources,
        'type': type,
        'lxc_name':allocation_of_task.lxc_name
    }
    node_manager.ip_to_rpc(allocation_of_task.machineid).change_cgroup_settings(configuration)



# 用户设置请求的slot数量,不能单独设置cpu和memory
def test1():
    print("init allocations:")
    for i in range(0,10):
        addNode(i)

    job_allocation_request_normal = {
        'jobid': 1,
        'userid': 'root',
        'tasks_count': 17,
        'resources': 1,
        'bidprice': 7,
        'always_reliable':False,
        'alwayas_unreliable':False,
        'once_for_all':False,
        'willing_to_wait':True
    }
    status,job_allocations = dispatch(job_allocation_request_normal)
    print(status)

    job_allocation_request_normal2 = {
        'jobid': 1,
        'userid': 'root',
        'tasks_count': 17,
        'resources': 1,
        'bidprice': 8,
        'always_reliable':False,
        'alwayas_unreliable':False,
        'once_for_all':True,
        'willing_to_wait':True
    }
#    status,job_allocations = dispatch(job_allocation_request_normal2)
#   print(status)

    job_allocation_request_always_reliable = {
        'jobid': 2,
        'userid': 'root',
        'tasks_count': 1,
        'resources': 1,
        'bidprice': -1,
        'always_reliable':True,
        'alwayas_unreliable':False,
        'once_for_all':False,
        'willing_to_wait':True
    }
#    job_allocations = allocate(job_allocation_request_always_reliable)
    job_allocation_request_always_unreliable = {
        'jobid': 3,  #clusterid
        'userid': 'root',
        'tasks_count': 1,
        'resources': 1,
        'bidprice': -1,
        'always_reliable':False,
        'alwayas_unreliable':True,
        'once_for_all':False,
        'willing_to_wait':True
    }
#    job_allocations = allocate(job_allocation_request_always_unreliable)
    job_allocation_request_once_for_all = {
        'jobid': 3,  #clusterid
        'userid': 'root',
        'tasks_count': 1,
        'resources': 1,
        'bidprice': -1,
        'always_reliable':False,
        'alwayas_unreliable':True,
        'once_for_all':False,
        'willing_to_wait':True
    }
#    job_allocations = allocate(job_allocation_request_always_unreliable)

# 用户可以请求单独设置cpu和memory, 测试当所有请求都按cpu:mem = 1:2 的时候,是否正确
def test2():
    print("init allocations:")
    addNode(1)

    job_allocation_request_1 = {
        'jobid': 1,
        'userid': 'root',
        'tasks_count': 1,
        'resources': 1,
        'bidprice': 18,
        'cpus': 1,
        'mems': 2,
        'always_reliable':False,
        'alwayas_unreliable':False,
        'once_for_all':False,
        'willing_to_wait':True
    }
    for i in range(0,64):
        print('request_1: '+str(i))
        status,job_allocations = dispatch(job_allocation_request_1)
    print(status)

    job_allocation_request_normal2 = {
        'jobid': 1,
        'userid': 'root',
        'tasks_count': 1,
        'resources': 1,
        'bidprice': 36,
        'cpus': 1,
        'mems': 2,
        'always_reliable':False,
        'alwayas_unreliable':False,
        'once_for_all':False,
        'willing_to_wait':True
    }
    for i in range(0,64):
        print('request_2: ' + str(i))
        status,job_allocations = dispatch(job_allocation_request_normal2)
        print(status)

def random_task_request():
    random_task_request = {
        'jobid': 1,
        'userid': 'root',
        'resources': 1,
        'bidprice': random.randint(1,100),
        'cpus': random.randint(1,8),
        'mems': random.randint(1,8),
        'always_reliable':False,
        'alwayas_unreliable':False,
        'once_for_all':False,
        'willing_to_wait':True
    }
    return random_task_request

def random_job_request(i):
    job_allocation_request = {
        'jobid': i,
        'userid': 'root',
        'tasks_count': random.randint(1,3),
        'bidprice': random.randint(1,100),
        'cpus': random.randint(1,10),
        'mems': random.randint(1,10),
        'always_reliable':False,
        'alwayas_unreliable':False,
        'once_for_all':True,
        'willing_to_wait':True
    }
    return job_allocation_request
    
# 1个节点，100个task请求
def test3():
    addNode(1)

    for a in allocations_list:
        for i in range(0,100):
            request = random_task_request()
            print(request)
            dp_allocate_task(a, rpequest)

# 1个节点，100个once_for_all == True 的job请求
def test4():
    addNode(1)
    for a in allocations_list:
        for i in range(0,100):
            request = random_job_request()
            print(request)
            dispatch(request)
    

# 1个节点，100个once_for_all == False 的job请求
def test5():
    addNode(1)
    for a in allocations_list:
        for i in range(0,100):
            request = random_job_request()
            request['once_for_all']=False
            print(request)
            dispatch(request)

    return
# 3个节点, 100 个once_for_all == True的job请求
def test6():
    addNode(1)
    addNode(2)
    addNode(3)
    for i in range(0,2000):
        request = random_job_request()
        print(request)
        dispatch(request)

    print("result:")
    for a in allocations_list:    
        print(a.opt[-1][a.cpus][a.mems])

# 3个节点, 10 个once_for_all == False 的job请求，验证正确性
def test7():
    addNode(1)
    addNode(2)
    addNode(3)
    for a in allocations_list:
        print("add machine:::  id:%s cpus:%d  mems:%d" % (a.machineid, a.cpus, a.mems))
    print("")
    for i in range(0,10):
        request = random_job_request(i)
        request['once_for_all']=False
        print("request %s::: cpus:%s mems:%s bidprice:%s tasks_count:%s" % (request['jobid'],request['cpus'],request['mems'],request['bidprice'],request['tasks_count']))
        dispatch(request)

    print("")
    for a in allocations_list:
        print("allocations on machine  %s has total value %s" % (a.machineid, a.opt[-1][a.cpus][a.mems]))
        for allo in a.reliable_allocations:
            print( "job:%s cpus:%s mems:%s bidprice:%s charge:%s" % (allo.jobid, allo.cpus, allo.mems,allo.bidprice,allo.charge))


# 3个节点，1000个once_for_all == False的job请求，测试性能：
def test8():
    addNode(1, 24, 340)
    addNode(2, 24, 340)
    addNode(3, 24, 340)
    for a in allocations_list:
        print("add machine:::  id:%s cpus:%d  mems:%d" % (a.machineid, a.cpus, a.mems))
    print("")
    for i in range(0,1000):
        request = random_job_request(i)
        request['once_for_all']=False
        print("request %s::: cpus:%s mems:%s bidprice:%s tasks_count:%s" % (request['jobid'],request['cpus'],request['mems'],request['bidprice'],request['tasks_count']))
        dispatch(request)

    print("")
    for a in allocations_list:
        print("allocations on machine  %s has total value %s" % (a.machineid, a.opt[-1][a.cpus][a.mems]))
        for allo in a.reliable_allocations:
            print( "job:%s cpus:%s mems:%s bidprice:%s charge:%s" % (allo.jobid, allo.cpus, allo.mems,allo.bidprice,allo.charge))
            
if __name__=='__main__':
    from time import clock
#    matrix = [[0 for i in range(3)] for i in range(3)]
#    matrix[0][1]=2
#    matrix.append([3,3,3,3])
#    print(matrix)
#    print(matrix[3][3])
    test7()
#    start = clock()
#    test8()
#    finish = clock()
#    print("1000 requests need %d seconds" % ((finish-start)))

