

#  from monitor import summary_resources, summary_usage, curr_usage
#  from monitor import summary_usage_per_user, summary_usage_per_user
#  from monitor import curr_usage_per_machine
from log import logger

import math
import nodemgr
import bisect, uuid,json

ratio_price_cpu_mem = 14

class AllocationOfTask(object):
    __slots__ = 'id','userid','jobid','taskid','resources','bidprice','type','machineid','lxc_name','cpus','mems','unit_price'

    def recompute_unit_price():
        return float(self.bidprice) / float(self.cpus * ratio_price_cpu_mem + slef.mems) * math.sqrt( ratio_price_cpu_mem * ratio_price_cpu_mem +1)
    
    def __key(self):
        return (self.userid, self.jobid, self.taskid)
    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.unit_price < other.unit_price
    def __le__(self, other):
        return self.unit_price <= other.unit_price

    def __eq__(self, other):
        return self.unit_price == other.unit_price
        
    def __ne__(self, other):
        return self.unit_price != other.unit_price

    def __gt__(self, other):
        return self.unit_price > other.unit_price

    def __ge__(self, other):
        return self.unit_price >= other.unit_price

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    
    def __repr__(self):
        return str({
            'id': self.id,
            'userid': self.userid,
            'jobid': self.jobid,
            'taskid': self.taskid,
            'resources': self.resources,
            'bidprice': self.bidprice,
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
            'resources': self.resources,
            'bidprice': self.bidprice,
            'type': self.type,
            'machineid':self.machineid,
            'lxc-name':self.lxc_name
        })
     
class AllocationOfMachine(object):
    __slots__ = ['machineid',"resources","reliable_available",
                 'reliable_allocations', 'restricted_allocations',
                 'cpus','mems','total_value','tasks','colony','total_value_invert']

    def add_task(self,task):
        self.tasks[task['id']]=tasks
        self.colony.tasks_to_add[task['id']]=task
        self.total_value += task['price']
        
        
    def __lt__(self, other):
        if self.total_value < other.total_value:
            return True
        else:
            return False
    def __le__(self, other):
        if self.total_value <= other.total_value:
            return True
        else:
            return False
    def __eq__(self, other):
        if self.total_value == other.total_value:
            return True
        else:
            return False
    def __ne__(self, other):
        if self.total_value != other.total_value:
            return True
        else:
            return False
    def __gt__(self, other):
        if self.total_value > other.total_value:
            return True
        else:
            return False
    def __ge__(self, other):
        if self.total_value >=  other.total_value:
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

        allocation.cpus = 24
        allocation.mems = 280
        
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

    allocation.cpus = 24
    allocation.mems = 280
    
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

# 重构:修改成尽量饱和
# 每接收一个资源请求,


# A1: 对于给出了价值估值的可靠资源请求和一直匹配最高出价的请求，不管出价多高,都立即计算一次是否可满足(因为可能存在资源碎片,即使这个请求出价较低,也有可能得到资源)
# A2: 不能满足的资源请求,如果设置了愿意等待,那么放入可靠资源的等待队列中(按出价排序)
# A3: 检查是否愿意使用不可靠资源, 如果愿意的话,尝试为这个请求分配不可靠资源


    
# B1: 对于只用不可靠资源的请求, 立即尝试分配不可靠资源, 选择最饱和的机器,如果资源利用率不高,即分配
# B2: 如果不能分配,并且愿意等待,放入不可靠资源的等待队列

def dispatch(job_allocation_request):
    global reliable_waiting_queue
    global unreliable_waiting_queue

    #可靠资源
    if job_allocation_request['always_reliable'] or int(job_allocation_request['bidprice'])>0:

        #计算单位资源价格
        bidprice = float(job_allocation_request['bidprice'])
        cpus = float(job_allocation_request['cpus'])
        mems = float(job_allocation_request['mems'])
        
        job_allocation_request['unit_price'] = bidprice / (ratio_price_cpu_mem * cpus + mems) * ( math.sqrt( ratio_price_cpu_mem * ratio_price_cpu_mem +1))
        
        # 出价最高的,尝试分配; 如果不是最高,加入等待队列
        if len(reliable_waiting_queue)==0 or job_allocation_request['unit_price']> reliable_waiting_queue[-1]['unit_price']:
            status  = allocate_reliable(job_allocation_request)
            if status =='success':
                return 'success',job_allocation_request['allocated']
        else:
            if job_allocation_request['willing_to_wait']==False:
                bisect.insort(reliable_waiting_queue, job_allocation_request)
                return 'waiting',job_allocation_request['allocated']
            else:
                return 'failed'

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

# 先不考虑信息素和概率
# 先不考虑 once_for_all选项，每次只分配一个容器
# A3: 依次挑选价值最低的机器，空闲资源能分配一个container，就立即分配一个
# A4: 如果需要抢占，按照排序，依次抢占，直到能放下，
# A5: 比较被抢占的容器的价值总和和当前容器的价值，如果总价值下降了，那么放弃抢占
# A6: 如果总价值上升了，把容器放到这个机器上，放置；（计算增加的价值，按概率放置）

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
            job_allocation_request['allocated'] = task_allocations
            job_allocation_request['allocated_count'] = len(task_allocations)
            if job_allocation_request['tasks_count'] == len(job_allocation_request['allocated']):
                return 'success'
                break
        if job_allocation_request['tasks_count'] == len(job_allocation_request['allocated']):
            return 'success',task_allocations
        else:
            return 'failed'
        print(job_allocation_request)

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

        print(job_allocation_request)

def allocate_on_each(allocation_of_machine, job_allocation_request):
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
            bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
            lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task
            
            allocated.append(allocation_of_task)
            reliable_available -= task_resources

            # 如果分满了就跳出while循环
            if len(allocated) >= tasks_count:
                break
    allocation_of_machine.reliable_available = reliable_available
    # 空闲资源就够分了
    if len(allocated)>= tasks_count:
        return allocated


    
    # 查看有多少可抢占资源,够分就抢占,分配: c-style for loop could be simulated using while in python
#    i = 0;
#    while i <len(allocation_of_machine.reliable_allocations):
    while True:
        a = allocation_of_machine.reliable_allocations[0]
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
                bisect.insort(allocation_of_machine.reliable_allocations, allocation_of_task)
                lxcname_allocation_dict[allocation_of_task.lxc_name]=allocation_of_task

                allocated.append(allocation_of_task)
                reliable_available -= task_resources
                # 如果满足请求数量,就跳出while循环
                if len(allocated) >= tasks_count:
                    break
            allocation_of_machine.reliable_available = reliable_available
            
            # 转成受限
            a.type = 'restricted'
            bisect.insort(allocation_of_machine.restricted_allocations,a)
                
            # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源
            #        for i in range(0,can_preempt_count):
            #            change_cgroup_settings(allocation_of_machine.reliable_allocations[i].lxc_name, 'restricted')
                
            # 把被抢占的可靠资源从reliable_allocations中删除
            del allocation_of_machine.reliable_allocations[0]

            if len(allocated) >= tasks_count:
                break
        else:
            break
    return allocated

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
    status,job_allocations = dispatch(job_allocation_request_normal2)
    print(status)

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

# 用户可以请求单独设置cpu和memory
def test2():
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
    status,job_allocations = dispatch(job_allocation_request_normal2)
    print(status)
    
if __name__=='__main__':
    test1()
