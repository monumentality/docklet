

#  from monitor import summary_resources, summary_usage, curr_usage
#  from monitor import summary_usage_per_user, summary_usage_per_user
#  from monitor import curr_usage_per_machine
from log import logger
import nodemgr
import bisect, uuid,json
class AllocationOfTask(object):
    __slots__ = 'id','userid','jobid','taskid','resources','bidprice','type','machineid','lxc_name','cpus','mems','dominant_price'
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
            'dominant_price':self.dominant_price,
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
                 'value_total','pheromone']
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

usages_list=[]
machine_usage_dict = {}

# 重构
reliable_waiting_queue = []
unreliable_waiting_queue = []
reliable_allocation_queue = []
waiting_dict = {}
unreliable_allocation_dict = {}
reliable_allocation_dict = {}
machine_reliable_dict = {}
reliable = 0
reliable_left = 0


machine_allocation_dict = {}
allocations_list = []
node_manager = {}
lxcname_allocation_dict = {}
max_cpu = 4
max_mem = 8

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

def addNode(machineid):
    global machine_allocation_dict
    global allocations_list
    global node_manager
    global usages_list
    global machine_usage_dict

    #logger.info("add node")
    
    allocation = AllocationOfMachine()
    allocation.machineid = machineid
    allocation.resources = 3
    allocation.reliable_available = 3
    allocation.reliable_allocations = []
    allocation.restricted_allocations = []

    allocation.cpus = 64
    allocation.mems = 128
    allocation.cpus_available =64
    allocation.mems_available = 128
    allocation.cpu_price = 16
    allocation.mem_price = 1
    allocation.cpu_compact = False
    allocation.mem_compact = False
    allocation.dominant_queue = []
    
    bisect.insort(allocations_list,allocation)
    
    usage_of_machine = {}
    usage_of_machine['machineid']=machineid
    usage_of_machine['cpu_utilization']=0.1
    
    usages_list.append(usage_of_machine)
    machine_usage_dict[machineid] = 0.1
        
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


def current_ratio_cpu_memory():
    return 
# 重构:修改成尽量饱和
# 每接收一个资源请求,


# A0: 对于给出了价值估值的可靠资源请求和一直匹配最高出价的请求
# A1: 按照当前的cpu/内存价格比,计算是否是最高的,如果是,则检查是否可满足
# A2: 不能满足的资源请求,如果设置了愿意等待,那么放入可靠资源的等待队列中(按出价排序)
# A3: 检查是否愿意使用不可靠资源, 如果愿意的话,尝试为这个请求分配不可靠资源


    
# B1: 对于只用不可靠资源的请求, 立即尝试分配不可靠资源, 选择最饱和的机器,如果资源利用率不高,即分配
# B2: 如果不能分配,并且愿意等待,放入不可靠资源的等待队列

def dispatch(job_allocation_request):
    global reliable_waiting_queue
    global unreliable_waiting_queue
    #可靠资源
    if job_allocation_request['always_reliable'] or int(job_allocation_request['bidprice'])>0:
        # 出价最高的,尝试分配; 如果不是最高,加入等待队列
        # 计算unitprice
        # lowest_cpu_price = current_lowest_cpu_price()
        ratio_cpu_mem = current_ratio_cpu_memory()
        # 把waiting_queue重新排序
        for request in reliable_waiting_queue:
            request['dominant_price'] = int(request['bidprice'])/( int(request['cpus'])+ int(request['mem']) /ratio_cpu_mem )
        sorted(reliable_waiting_queue, key=lambda k: k['dominant_price'])
        
        if len(reliable_waiting_queue)==0 or job_allocation_request['dominant_price']> reliable_waiting_queue[-1]['dominant_price']:
            status  = allocate_reliable(job_allocation_request)
            print('status:'+status)
            if status =='success':
                return 'success',job_allocation_request['allocated']
            else:
                return 'failed',[]
        else:
            if job_allocation_request['willing_to_wait']==False:
                bisect.insort(reliable_waiting_queue, job_allocation_request)
                return 'waiting',job_allocation_request['allocated']
            else:
                return 'failed',[]

    else:
        status = allocate_unreliable(job_allocation_request)
        if status=='success':
            return 'success',job_allocation_request
        else:
            if job_allocation_request['willing_to_wait']==True:
                bisect.insort(unreliable_queue, job_allocation_request)
            else:
                return 'failed'

# 1. 删除该任务所占的资源,从每个机器的已分配队列中删除
# 2. 从等待队列中,依次挑选出价最高的请求,看哪个请求可以得到满足
# 3. 有可能需要遍历整个queue,这是由于资源碎片导致的
def release_reliable(job_release_request):
    # 取出等待队列中价值最大的那一个,尝试分配
    job_allocation_request = reliable_waiting_queue[len(reliable_waiting_queue)-1]
    job_allocation_response = allocate_reliable(job_allocation_request)
    if job_allocation_response['status']=='success':
        return 'success',job_allocation_response
    else:
        return 'failed'
    
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

def allocate_on_each(allocation_of_machine, job_allocation_request):
    global lxcname_allocation_dict
    allocated = job_allocation_request['allocated']

    task_cpus = int(job_allocation_request['cpus'])
    task_mems = int(job_allocation_request['mems'])
    bidprice = int(job_allocation_request['bidprice'])
    
#    task_resources = int(job_allocation_request['resources'])
    tasks_count= int(job_allocation_request['tasks_count'])
    
    cpus_available = allocation_of_machine.cpus_available
    mems_available = allocation_of_machine.mems_available
    cpu_price = allocation_of_machine.cpu_price
    mem_price = allocation_of_machine.mem_price
    cpu_compact = allocation_of_machine.cpu_compact
    mem_compact = allocation_of_machine.mem_compact
    
    # 初始默认是cpu_price
    job_allocation_request['dominant_price'] = cpu_price

    #初始taskid
    taskid = len(allocated)
    print("try allocate task:"+str(taskid))

    while True:    

        # cpu已经紧致,而且不够分配,需要抢占cpu
        if allocation_of_machine.cpu_compact and not allocation_of_machine.mem_compact and task_cpus > cpus_available:
            job_allocation_request['dominant_price'] = (bidprice - mem_price * task_mems) / task_cpus
            a = allocation_of_machine.dominant_queue[0]
            if (a.dominant_price < job_allocation_request['dominant_price']):
                cpus_available += a.cpus
                mems_available += a.mems
            
                # 转成受限
                a.type = 'restricted'
                bisect.insort(allocation_of_machine.restricted_allocations,a)
                
                # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源
                #        for i in range(0,can_preempt_count):
                #            change_cgroup_settings(allocation_of_machine.reliable_allocations[i].lxc_name, 'restricted')    

                # 把被抢占的可靠资源从reliable_allocations中删除
                del allocation_of_machine.dominant_queue[0]
                # 改变cpu价格
                cpu_price = a.dominant_price

                allocation_of_machin.cpus_available = cpus_available
                allocation_of_machine.mems_available = mems_available
            else:
                # 可以跳出整个while循环了
                break

        # mem已经紧致,而且不够分,需要抢占mem
        if allocation_of_machine.mem_compact and not allocation_of_machine.cpu_compact and task_mems > mems_available:
            job_allocation_request['dominant_price'] = (bidprice - cpu_price * task_cpus) / task_mems
            a = allocation_of_machine.dominant_queue[0]
            if (a.dominant_price < job_allocation_request['dominant_price']):
                cpus_available += a.cpus
                mems_available += a.mems
            
                # 转成受限
                a.type = 'restricted'
                bisect.insort(allocation_of_machine.restricted_allocations,a)
                
                # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源
                #        for i in range(0,can_preempt_count):
                #            change_cgroup_settings(allocation_of_machine.reliable_allocations[i].lxc_name, 'restricted')    

                # 把被抢占的可靠资源从reliable_allocations中删除
                del allocation_of_machine.dominant_queue[0]
                # 改变mem_price
                mem_price = a.dominant_price

                allocation_of_machine.cpus_available = cpus_available
                allocation_of_machine.mems_available = mems_available
            else:
                # 可以跳出整个while循环了
                break

        # mem cpu 都紧致
        if allocation_of_machine.mem_compact and  allocation_of_machine.cpu_compact and task_cpus > cpus_available and task_mems>mems_available:
            job_allocation_request['dominant_price'] = bidprice / (task_cpus + task_mems * mem_price / cpu_price)
            a = allocation_of_machine.dominant_queue[0]
            print('haha')
            if (a.dominant_price < job_allocation_request['dominant_price']):
                cpus_available += a.cpus
                mems_available += a.mems
            
                # 转成受限
                a.type = 'restricted'
                bisect.insort(allocation_of_machine.restricted_allocations,a)
                
                # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源
                #        for i in range(0,can_preempt_count):
                #            change_cgroup_settings(allocation_of_machine.reliable_allocations[i].lxc_name, 'restricted')    

                # 把被抢占的可靠资源从reliable_allocations中删除
                del allocation_of_machine.dominant_queue[0]

                allocation_of_machine.cpus_available = cpus_available
                allocation_of_machine.mems_available = mems_available
            else:
                # 可以跳出整个while循环了
                break

        # 都不紧致,至少可以分配一个!
        if cpus_available >= task_cpus and mems_available >= task_mems:
            print('can allocate now, enouth resource')
            allocation_of_task = AllocationOfTask()
            allocation_of_task.id = uuid.uuid4()
            allocation_of_task.userid = job_allocation_request['userid']
            allocation_of_task.jobid = job_allocation_request['jobid']
            allocation_of_task.taskid = len(allocated)
            #            allocation_of_task.resources = job_allocation_request['resources']
            allocation_of_task.cpus = task_cpus
            allocation_of_task.mems = task_mems
            allocation_of_task.bidprice = job_allocation_request['bidprice']
            allocation_of_task.dominant_price = job_allocation_request['dominant_price']
            allocation_of_task.machineid = allocation_of_machine.machineid
            allocation_of_task.lxc_name = (allocation_of_task.userid
                                           + "-"
                                           + str(allocation_of_task.jobid)
                                           + "-"
                                           + str(allocation_of_task.taskid))
            allocation_of_task.type = 'reliable'

#            bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
            lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task
            
            allocated.append(allocation_of_task)
            print('should be 1: '+str(len(allocated)))
            #            reliable_available -= task_resources
            cpus_available -= task_cpus
            mems_available -= task_mems

            # allocation_of_machine.reliable_available = reliable_resources
            allocation_of_machine.cpus_available = cpus_available
            allocation_of_machine.mems_available = mems_available

            # 加入dominant_queue
            bisect.insort(allocation_of_machine.dominant_queue, allocation_of_task)
            
            # 每次成功分配新container之后,需要重新计算 cpu_compact, mem_compact, dominant_queue
            if cpus_available >= max_cpu:
                cpu_compact_new = False
            else:
                cpu_compact_new = True

            if mems_available >= max_mem:
                mem_compact_new = False
            else:
                mem_compact_new = True

            # 内存保持不紧,cpu变紧
            if not cpu_compact and cpu_compact_new and not mem_compact and not mem_compact_new:
                # 重新计算dominant_queue, 内存价格不变,排序cpu价格
                for allocation in allocation_of_machine.dominant_queue:
                    allocation.dominant_price = (allocation.bidprice - allocation.mems* mem_price)/allocation.cpus
                sorted(allocation_of_machine.dominant_queue)
                
            # cpu保持不紧,内存变紧
            if not mem_compact and mem_compact_new and not cpu_compact and not cpu_compact_new:
                # 重新计算dominant_queue, cpu价格保持不变,按照内存价格排序
                for allocation in allocation_of_machine.dominant_queue:
                    allocation.dominant_price = (allocation.bidprice - allocation.cpus* cpu_price)/allocation.mems
                sorted(allocation_of_machine.dominant_queue)

            # cpu和内存都变紧
            if not cpu_compact and not mem_compact and cpu_compact_new and mem_compact_new:
                # 重新计算dominant_queue, 按照cpu和内存价格的比例计算,按照cpu的价格排序
                for allocation in allocation_of_machine.dominant_queue:
                    allocation.dominant_price = allocation.bidprice/( allocation.cpus+allocation.mems * mem_price/cpu_price)
                sorted(allocation_of_machine.dominant_queue)
                
            # 内存和cpu的紧致状态不变的情况,什么都不用做了

            allocation_of_machine.cpu_compact = cpu_compact_new
            allocation_of_machine.mem_compact = mem_compact_new

                
        # 请求分配完毕,跳出循环
        if len(allocated)>= tasks_count:
            break

    job_allocation_request['allocated'] = allocated

    print('allocated tasks: ' + str(len(allocated)))
    return allocated
    
    # 查看有多少可抢占资源,够分就抢占,分配

    # 0  检查现有资源是否足够分配
    
    # A1 如果mem不足,保持cpu价格不变,排序所有请求的mem价格,抢占最低的一个,抢不到就结束
    # A2 被抢占的转为使用不可靠资源
    # A3 可用cpu,mem都增加, 当前mem价格改变
    # A4 返回0


    
    # B1. 如果cpu不足,保持mem价格不变,排序所有请求的cpu价格,抢占最低的一个, 若没有可抢占的就结束
    # B2. 被抢占的转为使用不可靠资源
    # B3. 可用cpu,mem增加，当前cpu价格增加
    # B4. 返回0

    # C1. 如果mem和cpu都不足,假设当前cpu与mem的价格比不变,排序所有请求的cpu价格,抢占最低的一个
    # C2. 被抢占的转为使用不可靠资源
    # C3. 可用cpu,mem增加，当前cpu和mem价格都增加
    # C4. 返回0

    # D1. 如果cpu和mem足够用, 分配新container
    # D2. 每次分配新container,有可能引起cpu或mem从不满变满, 如果引起了这种变化,就需要重置排序表

    
    # 请求申请多个container时,让然要一个个处理,因为每一次抢占可能引起cpu或内存价格的变化,从而导致下一次的不同
    # 什么时候修改dominant价格有序表? mem或cpu紧致状态变化后修改


    

# 检查每台机器上能分多少,但不实际分配
def pre_allocate_on_each(allocation_of_machine, job_allocation_request):
    global lxcname_allocation_dict
    allocated = job_allocation_request['allocated']
    task_resources = int(job_allocation_request['resources'])
    tasks_count= int(job_allocation_request['tasks_count'])
    reliable_available = allocation_of_machine.reliable_available
    #初始taskid
    taskid = len(allocated)
    print("allocated:"+str(taskid))
    # 如果有空闲,分配
    if reliable_available >= task_resources:
        while reliable_available >= task_resources:
            allocation_of_task = AllocationOfTask()
            allocation_of_task.id = uuid.uuid4()
            allocation_of_task.userid = job_allocation_request['userid']
            allocation_of_task.jobid = job_allocation_request['jobid']
            allocation_of_task.taskid = len(allocated)
            allocation_of_task.resources = job_allocation_request['resources']
            allocation_of_task.bidprice = job_allocation_request['bidprice']
            allocation_of_task.machineid = allocation_of_machine.machineid
            allocation_of_task.lxc_name = (allocation_of_task.userid
                                           + "-"
                                           + str(allocation_of_task.jobid)
                                           + "-"
                                           + str(allocation_of_task.taskid))
            allocation_of_task.type = 'reliable'
#            bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
#            lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task
            
            allocated.append(allocation_of_task)
            reliable_available -= task_resources

            # 如果分满了就跳出while循环
            if len(allocated) >= tasks_count:
                break
#    allocation_of_machine.reliable_available = reliable_available
    # 空闲资源就够分了
    if len(allocated)>= tasks_count:
        return allocated


    
    # 查看有多少可抢占资源,够分就抢占,分配
    for a in allocation_of_machine.reliable_allocations:
        if (a.bidprice < job_allocation_request['bidprice']):
            reliable_available += a.resources
            
            while reliable_available >= task_resources:
                allocation_of_task = AllocationOfTask()
                allocation_of_task.id = uuid.uuid4()
                allocation_of_task.userid = job_allocation_request['userid']
                allocation_of_task.jobid = job_allocation_request['jobid']
                allocation_of_task.taskid = len(allocated)
                allocation_of_task.resources = job_allocation_request['resources']
                allocation_of_task.bidprice = job_allocation_request['bidprice']
                allocation_of_task.machineid = allocation_of_machine.machineid
                allocation_of_task.lxc_name = (allocation_of_task.userid
                                               + "-"
                                               + str(allocation_of_task.jobid)
                                               + "-"
                                               + str(allocation_of_task.taskid))
                allocation_of_task.type = 'reliable'
#                bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
#                lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task

                allocated.append(allocation_of_task)
                reliable_available -= task_resources
                # 如果满足请求数量,就跳出while循环
                if len(allocated) >= tasks_count:
                    break
#            allocation_of_machine.reliable_available = reliable_available

            
            # 转成受限
#            a.type = 'restricted'
#            bisect.insort(allocation_of_machine.restricted_allocations,a)
                
            # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源
            #        for i in range(0,can_preempt_count):
            #            change_cgroup_settings(allocation_of_machine.reliable_allocations[i].lxc_name, 'restricted')
                
            # 把被抢占的可靠资源从reliable_allocations中删除
#            del allocation_of_machine.reliable_allocations[a]

            if len(allocated) >= tasks_count:
                break
        else:
            break
    return allocated


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

# 暂时不做，需要设计一下ui
def change_bid(jobid):
    if(has_reliable_resources(allocation_of_machine,task_allocation_request)):
        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = task_allocation_request['userid']
        allocation_of_task.jobid = task_allocation_request['jobid']
        allocation_of_task.taskid = task_allocation_request['taskid']
        allocation_of_task.resources = task_allocation_request['resources']
        allocation_of_task.bidprice = task_allocation_request['bidprice']
        allocation_of_task.machineid = allocation_of_machine.machineid
        allocation_of_task.lxc_name = (allocation_of_task.userid
                                       + "-"
                                       + str(allocation_of_task.jobid)
                                       + "-"
                                       + str(allocation_of_task.taskid))
        allocation_of_task.type = 'reliable'
        bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
        lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task
        
        # update allocation_summary
        allocation_of_machine.reliable_available += task_allocation_request['resources']
        return {'status':'success', 'allocation':allocation_of_task}

    if(can_preempt_reliable_resources(allocation_of_machine,task_allocation_request)):
        can_preempt = 0
        can_preempt_count = 0
        # 把被抢占的可靠资源变成受限制资源
        for a in allocation_of_machine.reliable_allocations:
            can_preempt+=a.resources
            can_preempt_count+=1
            # 转成受限
            a.type = 'restricted'
            bisect.insort(allocation_of_machine.restricted_allocations,a)

            # 更新allocation_machine的reliable_available
            allocation_of_machine.reliable_available -= a.resources
            if can_preempt>=task_allocation_request['resources']:
                break
            
        # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源
#        for i in range(0,can_preempt_count):
#            change_cgroup_settings(allocation_of_machine.reliable_allocations[i], 'restricted')

        # 把被抢占的可靠资源从reliable_allocations中删除
        del allocation_of_machine.reliable_allocations[0:can_preempt_count]

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
        allocation_of_task.lxc_name = allocation_of_task.userid + "-" + allocation_of_task.jobid + "-" + str(allocation_of_task.taskid)
        allocation_of_task.type = 'reliable'
        bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
        lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task
        
        # update allocation_summary
        allocation_of_machine.reliable_available += task_allocation_request['resources']
        return {'status':'success', 'allocation':allocation_of_task}


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
    
if __name__=='__main__':
    test2()
