
from monitor import summary_resources, summary_usage, curr_usage
from monitor import summary_usage_per_user, summary_usage_per_user
from monitor import curr_usage_per_machine

def has_reliable_resources(request):
    if(request['slots']+allocated_resources<summary_resources['slots']):
        return True
    else:
        return False

def can_preempt_relibale_resources(request):
    reliable_allocated_sorted_by_bid = sorted(reliable_allocated, key=lambda k:k['bidprice'])
    can_be_preempted=0
    for a in reliable_allocated_sorted_by_bid:
        if(a['bidprice']<request['bidprice']):
            can_be_preempted += a['slots']
            if can_be_preempted>request['slots']:
                return True
        else:
            break
    return False

def has_restricted_resources(request):
    if request['slots']+curr_usage['slots']<summary_resources['slots']:
        return True
    else:
        return False

def can_preempt_restricted_resources(request):
    restricted_allocated_sorted_by_bid = sorted(reliable_allocated, key=lambda k:k['bidprice'])
    can_be_preempted=0
    for a in restricted_allocated_sorted_by_bid:
        if(a['bidprice']<request['bidprice']):
            can_be_preempted += a['slots']
            if can_be_preempted>request['slots']:
                return True
        else:
            break
    return False

reliable_allocated = []
reliabel_allocated_sorted_by_bid = []
restricted_allocated = []
restricted_allocated_sorted_by_bid = []
def allocate_resources(request):
    global allocated_resources
    global relibale_allocated
    global relibale_allocated_sorted_by_bid
    global restricted_allocated
    global restricted_allocated_sorted_by_bid

    if(has_reliable_resources(request)):
        allocated_machine=sorted_usage_per_machine.keys[0]
        reliable_allocation={userId: request['userId'],
                             slots: request['slots'],
                             machine: allocated_machine,
                             bidprice: request['bidprice']}
        reliable_allocations.insert(reliable_allocation)
        #  to-do 把reliable_allocation插入reliable_allocation_sorted_by_bid,并且保持有序
        allocation = {userId: request['userId'],
                      slots: request['slots'],
                      machine: allocated_machine,
                      bidprice: request['bidprice'],
                      type: reliable}
        return {status:success, allocation:allocation}

    if(can_preempt_restricted_resources(request)):
        can_preempt = 0
        can_preempt_count = 0
        # 把被抢占的可靠资源变成受限制资源
        for i,a in reliable_allocation_sorted_by_bid:
            can_preempt+=a['slots']
            can_preempt_count+=1
            restricted_allocation={userId: request['userId'],
                                   slots: request['slots'],
                                   machine: allocated_machine,
                                   bidprice: request['bidprice']}
            restricted_allocations.insert(restricted_allocation)
            # to-do 同时把restricted_allocation插入restricted_allocations_sorted_by_bid，并保持有序

            if can_preempt>=request['slots']:
                break
        # 把被抢占的可靠资源从reliable_allocation中删除
        del reliable_allocations[0..can_preempt_count]

        # to-do 同时从reliable_allocation_sorted_by_bid中删除

        # to-do 以下寻找实际分配的物理机的方法暂时是错的
        allocated_machine=reliable_allocation_sorted_by_bid[0]['machine']

        reliable_allocation={userId: request['userId'],
                             slots: request['slots'],
                             machine: allocated_machine}
        reliable_allocations.insert(reliable_allocation)
        allocation = {userId: request['userId'],
                      slots: request['slots'],
                      machine: allocated_machine,
                      type: reliable}
        return {status:success, allocation:allocation}

    if(has_restricted_resources(request)):
        sorted_usage_per_machine = sorted(usage_per_machine, key=lambda k: k['usage'], reverse=True)
        allocated_machines=sorted_usage_per_machine.keys[0]
        restricted_allocation={userId: request['userId'],
                               slots: request['slots'],
                               machines: allocated_machine}
        restricted_allocations.insert(restricted_allocation)
        allocation = {userId: request['userId'],
                      slots: request['slots'],
                      machines: allocated_machines,
                      type: restricted}
        allocations.insert(allocation)
        return {status:'success', allocation:allocation}

    else:
        return {status: 'failed'}
