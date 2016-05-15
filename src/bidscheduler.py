
#  from monitor import summary_resources, summary_usage, curr_usage
#  from monitor import summary_usage_per_user, summary_usage_per_user
#  from monitor import curr_usage_per_machine
from log import logger
import nodemgr

class AllocationOfTask(object):
    __slots__ = 'uuid','userid','jobid','taskid','resources','bidprice','type'

class AllocationOfMachine(object):
    __slots__ = ['machineid',"resources","reliable_resources_allocation_summary",
                'reliable_allocation','curr_usage', 'restricted_allocation']

usages=[]
allocations = {}
nodemanager = {}
def init_allocations():
    global allocations
    global nodemanager
    global usages
    machines = nodemanager.get_allnodes()
    for machine in machines:
        allocation = AllocationOfMachine()
        allocation.machineid = machine
        allocation.resources = 100
        allocation.reliable_resources_allocation_summary = 0
        allocation.reliable_allocation = []
        allocation.restricted_allocation = []

        allocations[machine] = allocation

        usage_of_machine = {}
        usage_of_machine['machineid']=machine
        usage_of_machine['cpu_utilization']=0.1
        usages.append(usage_of_machine)

def has_reliable_resources(allocation_of_machine,task_allocation_request):
    if(task_allocation_request['resource']
       +allocation_of_machine.reliable_resources_allocation_summary
       < allocation_of_machine.resources):
        return True
    else:
        return False

def can_preempt_reliable_resources(taskAllocationRequest):
    to_be_preempted=0
    for a in reliable_allocation:
        if (a.bidprice< task_allocation_request['bidprice']):
            to_be_preempted += a.bidprice
            if to_be_preempted > task_allocation_request['resource']:
                return True
        else:
            break
        return False

def has_restricted_resources(allocation_of_machine,task_allocation_request):
    if(task_allocation_request['resources']
       + curr_usage
       < allocation_of_machine.resources * 0.8):
        return True
    else:
        return False

import uuid, bisect
def allocate_task(allocation_of_machine,task_allocation_request):
    if(has_reliable_resources(request)):
        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = task_allocation_request['userid']
        allocation_of_task.jobid = task_allocation_request['jobid']
        allocation_of_task.taskid = task_allocation_request['taskid']
        allocation_of_task.bidprice = task_allocation_request['bidprice']
        allocation_of_task.type = 'reliable'
        bisect.insort(allocation_of_machine.reliable_allocation, allocation_of_task, lambda x: x.bidprice)
        return {status:success, allocation:allocation_of_task}

    if(can_preempt_reliable_resources(task_allocation_request)):
        can_preempt = 0
        can_preempt_count = 0
        # 把被抢占的可靠资源变成受限制资源
        for i,a in reliableAllocation:
            can_preempt+=a['slots']
            can_preempt_count+=1
            a.type = 'restricted'
            import bisect
            bisect.insort(allocation_of_machine.restricted_allocation,a, lambda x: x.bidprice)
            # to-do 调整这些容器的cgroup设置，使用软限制模式，只能使用空闲资源

            if can_preempt>=task_allocation_request['resources']:
                break
            # 把被抢占的可靠资源从reliable_allocation中删除
        del reliable_allocations[0..can_preempt_count]

        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = task_allocation_request['userid']
        allocation_of_task.jobid = task_allocation_request['jobid']
        allocation_of_task.taskid = task_allocation_request['taskid']
        allocation_of_task.bidprice = task_allocation_request['bidprice']
        allocation_of_task.type = 'reliable'
        bisect.insort(allocation_of_machine.reliable_allocation,AllocationOfTask)
        return {status:success, allocation:allocation}

    if(has_restricted_resources(task_allocation_request)):
        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = task_allocation_request['userid']
        allocation_of_task.jobid = task_allocation_request['jobid']
        allocation_of_task.taskid = task_allocation_request['taskid']
        allocation_of_task.bidprice = task_allocation_request['bidprice']
        allocation_of_task.type = 'restricted'
        bisect.insort(allocation_of_machine.restricted_allocation,AllocationOfTask)
        return {status:'success', allocation:allocation_of_task}

    else:
        return {status: 'failed'}

def allocate_task_restricted(allocation_of_machine,task_allocation_request):
    if(has_restricted_resources(task_allocation_request)):
        allocation_of_task = AllocationOfTask()
        allocation_of_task.id = uuid.uuid4()
        allocation_of_task.userid = task_allocation_request['userid']
        allocation_of_task.jobid = task_allocation_request['jobid']
        allocation_of_task.taskid = task_allocation_request['taskid']
        allocation_of_task.bidprice = task_allocation_request['bidprice']
        allocation_of_task.type = 'restricted'
        bisect.insort(allocation_of_machine.restricted_allocation,AllocationOfTask)
        return {status:'success', allocation:allocation_of_task}

    else:
        return {status: 'failed'}

def allocate(job_allocation_request):
    logger.info("try allocate")
    global allocations
    job_allocation_response = []
    sorted(allocations,lambda x: x[1].reliable_resources_allocation_summary )

    # 先从可靠资源最多的机器分配资源
    for i in range(job_allocation_request['tasks_count']):
        task_allocation_request = {
            userid: job_allocation_request['userid'],
            jobid: job_allocation_request['jobid'],
            taskid: i,
            bidprice: job_allocation_request['bidprice'],
            resources: job_allocation_request['resources'],
        }
        if( has_reliable_resource(allocations[i],task_allocation_request)
            or can_preempt_reliable_resources(allocations[i],task_allocation_request)):
            task_allocation_response = allocate_task(task_allocation_request)
            job_allocation_response.add(task_allocation_response)
        else:
            break

    if (job_allocation_response.size == job_allocation_request['task_count']):
        return job_allocation_response
    else:
        # 选择使用率最低的机器，分配restricted_resources
        global usages
        sorted(usages, lambda x: x['cpu_utilization'], reverse=True)
        for i in range(job_allocation_response.size, job_allocation_request['taskcount']):
            machineid = usages[i]['machineid']
            allocation_of_machine = allocations[machineid]
            task_allocation_request = {
                userid: job_allocation_request['userid'],
                jobid: job_allocation_request['jobid'],
                taskid: i,
                bidprice: job_allocation_request['bidprice'],
                resources: job_allocation_request['resources']
            }
            task_allocation_response = allocate_restricted(allocation_of_machine,task_allocation_request)
            job_allocation_response.add(task_allocation_response)

    return job_allocation_response
