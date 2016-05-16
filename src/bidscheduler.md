<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. 多租户平台必须满足的要求：</a>
<ul>
<li><a href="#sec-1-1">1.1. Multi-tenancy:</a></li>
<li><a href="#sec-1-2">1.2. From an administrator’s perspective, multi-tenancy requirements are to</a></li>
<li><a href="#sec-1-3">1.3. 从用户角度看</a></li>
</ul>
</li>
<li><a href="#sec-2">2. 现有的多租户环境下的资源调度算法</a></li>
<li><a href="#sec-3">3. 动机</a></li>
<li><a href="#sec-4">4. 与Amazon竞价系统的不同</a></li>
<li><a href="#sec-5">5. 与敏捷开发的比较：</a></li>
<li><a href="#sec-6">6. 基于竞价方式的资源调度</a>
<ul>
<li><a href="#sec-6-1">6.1. 机制</a></li>
<li><a href="#sec-6-2">6.2. trade off</a></li>
<li><a href="#sec-6-3">6.3. 策略；</a>
<ul>
<li><a href="#sec-6-3-1">6.3.1. 资源分类：</a></li>
<li><a href="#sec-6-3-2">6.3.2. 用户只需要设置：</a></li>
<li><a href="#sec-6-3-3">6.3.3. 用户可以实时调整自己的策略</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-7">7. 实现方式：</a>
<ul>
<li><a href="#sec-7-1">7.1. mesos or yarn？</a></li>
<li><a href="#sec-7-2">7.2. yarn的调度器实现方式学习</a>
<ul>
<li><a href="#sec-7-2-1">7.2.1. capacity scheduler</a></li>
<li><a href="#sec-7-2-2">7.2.2. fair scheduler</a></li>
<li><a href="#sec-7-2-3">7.2.3. Heterogeneous scheduler</a></li>
<li><a href="#sec-7-2-4">7.2.4. random scheduler</a></li>
</ul>
</li>
<li><a href="#sec-7-3">7.3. 搭建hadoop开发环境</a>
<ul>
<li><a href="#sec-7-3-1">7.3.1. docker</a></li>
<li><a href="#sec-7-3-2">7.3.2. 虚拟机</a></li>
<li><a href="#sec-7-3-3">7.3.3. 最终方法</a></li>
<li><a href="#sec-7-3-4">7.3.4. 导入eclipse</a></li>
<li><a href="#sec-7-3-5">7.3.5. 目前好用的翻墙方法</a></li>
</ul>
</li>
<li><a href="#sec-7-4">7.4. 编译，打包，测试方法</a>
<ul>
<li><a href="#sec-7-4-1">7.4.1. maven的生命周期</a></li>
</ul>
</li>
<li><a href="#sec-7-5">7.5. 阅读源码</a>
<ul>
<li><a href="#sec-7-5-1">7.5.1. fifo scheduler 源码分析</a></li>
<li><a href="#sec-7-5-2">7.5.2. capacity scheduler 源码分析</a></li>
<li><a href="#sec-7-5-3">7.5.3. fair scheduler 源码分析</a></li>
</ul>
</li>
<li><a href="#sec-7-6">7.6. 编写bid scheduler</a></li>
</ul>
</li>
<li><a href="#sec-8">8. Background or Discussion</a>
<ul>
<li><a href="#sec-8-1">8.1. Dynamic Proportional Share Scheduling in Hadoop</a>
<ul>
<li><a href="#sec-8-1-1">8.1.1. Abstract</a></li>
<li><a href="#sec-8-1-2">8.1.2. Introduction</a></li>
<li><a href="#sec-8-1-3">8.1.3. Hadoop MapReduce:</a></li>
<li><a href="#sec-8-1-4">8.1.4. Design</a></li>
<li><a href="#sec-8-1-5">8.1.5. evaluation</a></li>
<li><a href="#sec-8-1-6">8.1.6. discussion</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-9">9. 理论证明：</a>
<ul>
<li><a href="#sec-9-1">9.1. 概念辨析：</a>
<ul>
<li><a href="#sec-9-1-1">9.1.1. computational ecology 与 centralized scheduling</a></li>
<li><a href="#sec-9-1-2">9.1.2. microeconomic approach 与 game theory approach</a></li>
<li><a href="#sec-9-1-3">9.1.3. competitive equilibrium 与 game theory</a></li>
<li><a href="#sec-9-1-4">9.1.4. game with perfect information 与 game with imperfect information</a></li>
<li><a href="#sec-9-1-5">9.1.5. open market-based 与 auction</a></li>
<li><a href="#sec-9-1-6">9.1.6. 经济学中的公平与计算机领域的公平</a></li>
<li><a href="#sec-9-1-7">9.1.7. sealed-bid secound-price auction 与 first-price auction</a></li>
</ul>
</li>
<li><a href="#sec-9-2">9.2. 最优化证明：</a>
<ul>
<li><a href="#sec-9-2-1">9.2.1. 用户作业的损失函数</a></li>
<li><a href="#sec-9-2-2">9.2.2. 用户预估的作业资源使用量</a></li>
<li><a href="#sec-9-2-3">9.2.3. 系统总资源量</a></li>
</ul>
</li>
<li><a href="#sec-9-3">9.3. 价值评估：</a></li>
</ul>
</li>
<li><a href="#sec-10">10. bidscheduler实现</a>
<ul>
<li><a href="#sec-10-1">10.1. 两级调度架构：</a></li>
<li><a href="#sec-10-2">10.2. 提供的接口：</a></li>
<li><a href="#sec-10-3">10.3. 实现：</a>
<ul>
<li><a href="#sec-10-3-1">10.3.1. 数据结构：</a></li>
<li><a href="#sec-10-3-2">10.3.2. 数据初始化</a></li>
<li><a href="#sec-10-3-3">10.3.3. allocate方法：</a></li>
<li><a href="#sec-10-3-4">10.3.4. has<sub>reliable</sub><sub>resources</sub></a></li>
<li><a href="#sec-10-3-5">10.3.5. can<sub>preempt</sub><sub>reliable</sub><sub>resources</sub></a></li>
<li><a href="#sec-10-3-6">10.3.6. has<sub>restricted</sub><sub>resources</sub></a></li>
<li><a href="#sec-10-3-7">10.3.7. allocate<sub>task</sub></a></li>
<li><a href="#sec-10-3-8">10.3.8. allocate<sub>task</sub><sub>restricted</sub></a></li>
<li><a href="#sec-10-3-9">10.3.9. bidscheduler.py</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-11">11. 待解决的问题：</a>
<ul>
<li><a href="#sec-11-1">11.1. 架构的重构</a></li>
<li><a href="#sec-11-2">11.2. 性能问题，一秒能够处理多少调度请求</a></li>
<li><a href="#sec-11-3">11.3. 分布式</a></li>
<li><a href="#sec-11-4">11.4. 一致性，容错</a></li>
<li><a href="#sec-11-5">11.5. 调度作业与调度workspace的不同：</a></li>
</ul>
</li>
</ul>
</div>
</div>

# 多租户平台必须满足的要求：<a id="sec-1" name="sec-1"></a>

## Multi-tenancy:<a id="sec-1-1" name="sec-1-1"></a>

 Multi-tenancy is the ability of a single instance of software to serve multiple tenants. A tenant is a group of users that have the same view of the system. Hadoop, as an enterprise data hub, naturally demands multi-tenancy. Creating different instances of Hadoop for various users or functions is not acceptable as it makes it harder to share data across departments and creates silos.
多租户是使用某个软件的一个实例来服务多个租户。对系统拥有某一相同视图的一组用户是一个租户。通常租户可以是企业内部的部门或用户

## From an administrator’s perspective, multi-tenancy requirements are to<a id="sec-1-2" name="sec-1-2"></a>

Ensure SLAs are met 满足每个用户的服务层协议
Guarantee isolation 提供资源隔离
Enforce quotas      约束每个用户的配额
Establish security and delegation 确立安全和委派
Ensure low cost operations and simpler manageability 低运维成本和简化管理

## 从用户角度看<a id="sec-1-3" name="sec-1-3"></a>

即满足用户的服务层协议

# 现有的多租户环境下的资源调度算法<a id="sec-2" name="sec-2"></a>

yarn:优先级，队列，分层级的优先级列队，最小最大公平算法
mesos：DRF 主要资源公平算法
yarn对多租户的支持更多，mesos更侧重公平，缺少多租户支持

# 动机<a id="sec-3" name="sec-3"></a>

公平算法，对于高优先级的任务不公平
租户设定优先级，难以控制
实现一个竞价调度算法，使更有价值的作业获得更多资源，实现资源的公平和高效利用，需要引用一些经济理论来证明

# 与Amazon竞价系统的不同<a id="sec-4" name="sec-4"></a>

amazon把资源按照固定价格卖给客户，客户把自己的某些时段的空闲资源放到竞价系统交易
这个调度器则适用于某个组织内部，多部门或用户共享有限资源的环境，目的是实现资源的公平和高效利用，避免恶意竞争，鼓励良性竞争。

# 与敏捷开发的比较：<a id="sec-5" name="sec-5"></a>

敏捷开发方法中存在一个类似的过程：即团队确定了一个迭代周期需要完成的所有ticket之后，团队中所有成员对所有ticket进行竞价，所需工作时最少的程序员将获得该ticket。这个调度器和ticket竞价的策略是一致的，即鼓励团队内部成员的良性竞争，公平高效地利用团队资源。

# 基于竞价方式的资源调度<a id="sec-6" name="sec-6"></a>

## 机制<a id="sec-6-1" name="sec-6-1"></a>

平台资源数量是有限的，发给每个租户虚拟币，租户使用虚拟币来对资源竞标，出价高者获得资源
当资源紧张时，出价更高的租户将抢占出价低的租户使用的资源。由于允许抢占，作业/服务必须支持故障恢复

## trade off<a id="sec-6-2" name="sec-6-2"></a>

用户使用更复杂，用户需要权衡每个作业的重要性，选择为每个作业给出合适的竞价
用户需要关注整个平台的竞价排名，确保自己的作业按照预期完成
用户需要研究整个平台的竞价排名状况，与其他租户竞争，才能获得更多的资源占用；比如选择空闲时刻占据资源，甚至操纵竞价

## 策略；<a id="sec-6-3" name="sec-6-3"></a>

### 资源分类：<a id="sec-6-3-1" name="sec-6-3-1"></a>

空闲资源、可抢占资源、自动匹配最高竞价的不可抢占资源

### 用户只需要设置：<a id="sec-6-3-2" name="sec-6-3-2"></a>

只使用空闲资源
抢占BidHigh区间以下的资源
自动匹配最高竞价，使用所有能抢占的资源

### 用户可以实时调整自己的策略<a id="sec-6-3-3" name="sec-6-3-3"></a>

# 实现方式：<a id="sec-7" name="sec-7"></a>

## mesos or yarn？<a id="sec-7-1" name="sec-7-1"></a>

mesos 不支持抢占
mesos 没有原生支持hadoop

## yarn的调度器实现方式学习<a id="sec-7-2" name="sec-7-2"></a>

### capacity scheduler<a id="sec-7-2-1" name="sec-7-2-1"></a>

### fair scheduler<a id="sec-7-2-2" name="sec-7-2-2"></a>

### Heterogeneous scheduler<a id="sec-7-2-3" name="sec-7-2-3"></a>

### random scheduler<a id="sec-7-2-4" name="sec-7-2-4"></a>

## 搭建hadoop开发环境<a id="sec-7-3" name="sec-7-3"></a>

hadoop的编译在mac下必须使用虚拟机或者docker

### docker<a id="sec-7-3-1" name="sec-7-3-1"></a>

hadoop的官方提示：docker存储部分的bug，使得io非常慢，编译时很慢。我自己测试在mac下用docker编译hadoop，即使已经翻墙还是报hash mismatch，无法解决，放弃。

### 虚拟机<a id="sec-7-3-2" name="sec-7-3-2"></a>

在mac中使用ubuntu虚拟机上编译打包。发现virtualbox的共享文件夹有bug。把源文件放在共享文件夹下无法编译成功，放在普通文件夹下编译成功

### 最终方法<a id="sec-7-3-3" name="sec-7-3-3"></a>

在mac的eclipse客户端开发，传到虚拟机上编译测试

### 导入eclipse<a id="sec-7-3-4" name="sec-7-3-4"></a>

把hadoop源码导入eclipse，出现446个错误提示，主要是build path的问题。缺少一些java文件，需要手动把ptotobuf和avro的文件编译成java文件再加入build path。发现maven和eclipse集成的一些bug，自动创建的build path，有一些莫名其妙的无法识别，需要手动删除再重新添加就好了。

### 目前好用的翻墙方法<a id="sec-7-3-5" name="sec-7-3-5"></a>

1.  digitalocean的账户名

    clive.programmer.doyle@gmail.com woody.programmer.dylan@gmail.com

2.  shadowsocks

    在digitalocean上搭建shadowsocks server，客户端使用shadowsock-libev,使用iptables使所有流量都通过ss-redir发送出去。mac下无iptables难弄

3.  openswan

    基于ipsec协议，IKG是密码传输协议。可以使用密码，共享密码，证书方式登录，学习了证书的授权，安装方式。mac下的客户端支持不好，难搞

4.  openvpn，sslvpn，l2tp等

    有很多种vpn协议和软件包，这一块领域看来是没有研究价值，而且工程量很大的

## 编译，打包，测试方法<a id="sec-7-4" name="sec-7-4"></a>

### maven的生命周期<a id="sec-7-4-1" name="sec-7-4-1"></a>

在mac下可以使用mvn compile, 测试时使用mvn test,打包必须在linux下，跳过测试-DskipTests

## 阅读源码<a id="sec-7-5" name="sec-7-5"></a>

apache hadoop自带的三个scheduler，fifo scheduler，capacity scheduler和fair scheduler

### fifo scheduler 源码分析<a id="sec-7-5-1" name="sec-7-5-1"></a>

1.  实现的上层接口

    1.  initScheduler
    
    2.  serviceInit
    
    3.  serviceStart
    
    4.  serviceStop
    
    5.  setConf
    
    6.  getConf
    
    7.  getNumClusterNodes
    
    8.  setRMContext
    
    9.  reinitialize
    
    10. allocate (important)
    
    11. handle (important)
    
    12. getQueueInfo
    
    13. getQueueUserAclInfo
    
    14. getResourceCalculator
    
    15. recover
    
    16. getRMContainer
    
    17. getRootQueueMetrics
    
    18. checkAccess
    
    19. getAppsInQueue
    
    20. decreaseContainer

2.  相关的类

    1.  FiCaSchedulerApp
    
        需要调度的App，作业，所需资源量等
    
    2.  Resouce
    
        队列中的资源
    
    3.  ResourceRequest
    
        资源请求，包括位置，名称，容量，多少个容器（还是按照slot方式？），优先级

3.  allocate

    实际的获得resource的方法在CapacityHeadroomProvider下的getHeadroom里
    
    //从队列头部获取
    
    application.getHeadroom()
    
    //传给资源监控模块
    
    application.setApplicationHeadroomForMetrics(headroom);
    
    //更新nodemanager，applicationmanager状态？
    
    new Allocation(application.pullNewlyAllocatedContainers(),
              headroom, null, null, null, application.pullUpdatedNMTokens())

4.  handle

    以下事件都会影响到调度器模块，因此必须处理？
    
    1.  NODE<sub>ADDED</sub>
    
    2.  NODE<sub>REMOVED</sub>
    
    3.  NODE<sub>RESOURCE</sub><sub>UPDATE</sub>
    
    4.  NODE<sub>UPDATE</sub>
    
    5.  APP<sub>ADDED</sub>
    
    6.  APP<sub>REMOVED</sub>
    
    7.  APP<sub>ATTEMPT</sub><sub>ADDED</sub>
    
    8.  APP<sub>ATTEMPT</sub><sub>REMOVED</sub>
    
    9.  CONTAINER<sub>EXPIRED</sub>

### capacity scheduler 源码分析<a id="sec-7-5-2" name="sec-7-5-2"></a>

capacity和fifo耦合在一块，fifo需要调用capacity的代码，capacity也需要hadoop其他模块的支持才能运行。

1.  capacity添加的新类

    1.  CapacitySchedulerConfiguration
    
        自己的注册文件解析类
    
    2.  CSQueue, LeafQueue, ParentQueue, PlanQueue
    
        Job 队列，接口
    
    3.  QueueCapacities
    
        保存所有队列的容量信息
    
    4.  CSQueueMetrics
    
        job 队列的统计类
    
    5.  UserInfo
    
        用户信息类
    
    6.  CapacityHeadroomProvider
    
        从各种队列里分配资源的算法，真正的算法逻辑藏在这里

2.  capacity scheduler 算法

### fair scheduler 源码分析<a id="sec-7-5-3" name="sec-7-5-3"></a>

## 编写bid scheduler<a id="sec-7-6" name="sec-7-6"></a>

# Background or Discussion<a id="sec-8" name="sec-8"></a>

## Dynamic Proportional Share Scheduling in Hadoop<a id="sec-8-1" name="sec-8-1"></a>

### Abstract<a id="sec-8-1-1" name="sec-8-1-1"></a>

It allows users to control their allocated capacity by adjusting their spending over time.

This simple mechanism allows the scheduler to make more efficient decisions about which jobs and users to prioritize and gives users the tool to optimize and customize their allocations to fit the importance and requirements of their jobs.

We envision our scheduler to be used by deadline or budget optimizing agents on behalf of users.

We show that our scheduler enforces service levels more accurately and also scales to more users with distinct service levels than existing schedulers.

### Introduction<a id="sec-8-1-2" name="sec-8-1-2"></a>

we have developed the Dynamic Priority (DP) scheduler, a novel scheduler that extends the existing FIFO and fair-share schedulers in Hadoop.

这个跟我们的一样，作为hadoop已有的调度框架的一个插件，利用hadoop已经实现的很多接口和方法。

This scheduler plug-in allows users to purchase and bid for capacity or quality of service levels dynamically. This simple mechanism allows the scheduler to make more efficient decisions about which jobs and users to prioritize and gives users the tool to optimize and customize their allocations to fit the importance and requirements of their jobs.

这一点跟我们完全一样

it gives users the incentive to scale back their jobs when demand is high, since the cost of running on a slot is then also more expensive.

这一点并不重要

The capacity allotted, represented by Map and Reduce task slots, is proportional to the spending rate a user is willing to pay for a slot and inversely proportional to the aggregate spending rate of all existing users.

主要不同！他并不是完全的基于用户出价来抢占资源的，而是按照用户出价占总报价的比例来分配资源。而我们的策略是：出价最高的用户可以得到他需要的所有资源。按比例分配并不能使真正重要的任务获得优先执行！不符合经济规律。

### Hadoop MapReduce:<a id="sec-8-1-3" name="sec-8-1-3"></a>

review the current hadoop schedulers

### Design<a id="sec-8-1-4" name="sec-8-1-4"></a>

The primary design goal of our Hadoop task scheduler is to allow capacity distribution across concurrent users to change dynamically based on user preferences.

Traditional priority systems that try to guess user priority are too inaccurate , and unregulated user priorities assume trusted small groups of users.

Our scheduler automates capacity allocation and redistribution in a regulated task slot resource market.

1.  Mechanism

    The core of our design is a proportional share resource allocation mechanism that allows users to purchase or be granted a queue priority budget.
    
    This budget may be used to set spending rates denoting the willingness to pay a certain amount of the budget per Hadoop map or reduce task slot per time unit.
    
    The time unit is configurable, and referred to as allocation interval. It is typically set to somewhere between 10 seconds and 1 minute.
    
    In each allocation interval the scheduler:
    
    &#x2014;aggregates all spending rates s from all current users to calculate the Hadoop cluster price, p,
    
    &#x2014;for all users, allocates (si/p) × c task slots (both mappers and reducers) to user i, where si, is the spending rate of user i, and c is the aggregate slot capacity of the cluster
    
    &#x2014;for all users, deducts si × ui from budget b where ui, is the number of slots used by user i
    
    用户管理员可根据集群资源总量为每个用户分配一定的预算。用户可根据自己的需要动态调整自己的消费率，即每个时间单元内单个slot的价钱。在每个时间单元内，调度器按照以下步骤计算每个用户获得的资源量：
    
    1.  计算所有用户的消费率之和p
    
    2.  对于每个用户分配i，分配si/p\*c 的资源量，si是用户i的消费率，c为hadoop集群中资源总数
    
    3.  对于每个用户i，从其预算中扣除si \* ui，ui为用户正使用的slot数目
    
    The key feature of this mechanism is that it discourages free-riding and gaming by users.
    
    恰好相反，我们想要创造一个自由市场，鼓励博弈。为什么本文作者专门消除这些行为？
    
    The disadvantage is less capacity predictability and more variation in capacity allocated to an application.
    
    This introduces the difficulty of making spending rate decisions to meet the SLA and deadline requirements.
    
    Possible starvation of low-priority (low-spending) tasks can be mitigated by using the standard approach in Hadoop of limiting the time each task is allowed to run on a node.
    
    即使是低优先级的任务仍然不会被饿死。没有必要！
    
    We note that the Dynamic Priority scheduler can easily be configured to mimic the behavior of the other schedulers. If no queues or users have any credits left the scheduler reduces to a FIFO scheduler. If all queues are configured with the same share (spending rate in our case) and the allocation interval is set to a very large value, the scheduler reduces to the behavior of the static fair-share schedulers.
    
    可以退化为FIFO 和Fair Share scheduler

2.  implementation

### evaluation<a id="sec-8-1-5" name="sec-8-1-5"></a>

In the first set, we examine the correlation of spending rates, budgets and performance metrics.

In the second set, we study how accurately and effectively service levels can be supported.

### discussion<a id="sec-8-1-6" name="sec-8-1-6"></a>

Our scheduling approach is closely related to and inspired by economic schedulers,whereby you bid for resources on a market and receive allocations based on various auction mechanisms [18,19,20,17,21,22,23,24].We do not preclude nor require that our scheduler budgets are tied to a real currency. Furthermore, we do not assume that there are competing users who should be given different shares of the resources.

动态优先级调度受到经济学调度器的启发并且和他们很接近，都是用户在一个市场上基于各种各样的拍卖机制竞标资源。动态优先调度器不排除也不阻止用户的预算跟一种虚拟货币或者真实货币绑定。（编者注：其实不能同真实或者虚拟货币挂钩，因为不是自由市场）。

18-24这些论文都是05年以前，还没有hadoop和大数据的时代，主要面向网格计算和HPC。调研一下是否算是与它们重复。

应用了经济模型的调度器一定会引用这篇论文，因此我调研了所有160篇引用这篇论文的其他论文，暂时还没有发现跟我们重复的方案，有十几篇论文可能与我们有关联，可能需要引用，之后再读。

# 理论证明：<a id="sec-9" name="sec-9"></a>

## 概念辨析：<a id="sec-9-1" name="sec-9-1"></a>

### computational ecology 与 centralized scheduling<a id="sec-9-1-1" name="sec-9-1-1"></a>

中心化的调度: 按序处理，分配资源

computational ecology:  various processes can collaborate to solve problems while competing for the available computational resources, and may also directly interact with the physical world

这篇论文比较早，它提出的计算生态指的是类似现在没有中心调度器的分布式集群，这类集群使用多个协作的分布式调度器。每个调度器没有其他调度器的完备信息。目前好像没有类似的系统。目前的系统都是中心调度器。偶尔有一些随机调度器。但不符合这个模型。

### microeconomic approach 与 game theory approach<a id="sec-9-1-2" name="sec-9-1-2"></a>

一部分论文采用微观经济学的方法，一部分论文采用博弈论的方法

应当采用博弈论的方法

### competitive equilibrium 与 game theory<a id="sec-9-1-3" name="sec-9-1-3"></a>

前者把市场中的所有人的行为看成是一个人，后者把每个人看作是与整个系统博弈的，独立的人

### game with perfect information 与 game with imperfect information<a id="sec-9-1-4" name="sec-9-1-4"></a>

有些论文实现计算市场时，不允许用户知道其他用户的行为，这似乎是不合理的

还需要继续读完全信息博弈和不完全信息博弈的相关文章

### open market-based 与 auction<a id="sec-9-1-5" name="sec-9-1-5"></a>

拍卖适用于价格难以确定的商品，需要通过市场发现来确定

计算资源的需求是时间敏感的，而且是随机分布的，很难确定哪个时间段需求突然增多。对于一个资源量固定的计算集群来说，其价格因此是时间敏感，而且随机分布的

当前阶段企业私有计算集群的资源利用率是非常低的，其价格不能依据计算设施本身的价格计算得出

### 经济学中的公平与计算机领域的公平<a id="sec-9-1-6" name="sec-9-1-6"></a>

宏观经济学中的公平：

在计算机领域追求绝对公平没有价值。计算资源为计算任务服务，最终目标是使收益最大，尤其对于企业和组织的私有计算资源。

### sealed-bid secound-price auction 与 first-price auction<a id="sec-9-1-7" name="sec-9-1-7"></a>

## 最优化证明：<a id="sec-9-2" name="sec-9-2"></a>

### 用户作业的损失函数<a id="sec-9-2-1" name="sec-9-2-1"></a>

### 用户预估的作业资源使用量<a id="sec-9-2-2" name="sec-9-2-2"></a>

### 系统总资源量<a id="sec-9-2-3" name="sec-9-2-3"></a>

## 价值评估：<a id="sec-9-3" name="sec-9-3"></a>

理论之所以有价值，不仅是因为它得出的结论和所解释的现象，而且是因为它提出的问题和所指引的发现

# bidscheduler实现<a id="sec-10" name="sec-10"></a>

## 两级调度架构：<a id="sec-10-1" name="sec-10-1"></a>

bidscheduler作为一个通用的调度框架，应当采用资源调度和任务调度解耦合的架构。

由于bidscheduler考虑多租户，考虑作业价值的不同，不关注绝对公平，因此与yarn更类似，采用了类似yarn的两级调度架构。

bidscheduler作为 rasource manager， 之上可以运行多种application master, 我们的系统可以看做是一个 workspace master。之后将尝试，支持更多的计算框架，比如spark，比如崔嵬之前的跑作业的计算框架。

为了之后可以支持更多的计算框架，借鉴沿用了yarn的很多概念。

vclustermgr可看做是一个application master的实现。一个mapreduce job包含多个task, 类似于一个workspace包含多个容器。因此，还是沿用了yarn中的job和task的概念

存在一个问题：resource manager分给mapreducerMaster一个容器，就启动一个task，不需要等到所有容器都分配够了才启动执行；那么，一个workspace包含多个容器，是all or nothing 还是分开处理

## 提供的接口：<a id="sec-10-2" name="sec-10-2"></a>

allocate(jobAllocationRequest)
release(allocationid)

vclustermgr中create<sub>cluster函数调用allocation</sub>

    # call bidscheduler.allocate, get resources
    jobAllocationRequest = {
        jobid: clusterid,
        userid: json.loads(user_info)["userid"],
        tasks: clustersize,
        resourcesPerTask: containersize,
        bidprice: bidprice
    }
    import bidscheduler
    job_allocations = bidscheduler.allocate(jobAllocationRequest)

vclustermgr中调用release<sub>allocation</sub>

## 实现：<a id="sec-10-3" name="sec-10-3"></a>

### 数据结构：<a id="sec-10-3-1" name="sec-10-3-1"></a>

把分配出去的资源分为两类：
可靠资源，即受到隔离保护的资源，使用cgroup的cpu和memeory保护
受限制资源：使用cgroup的软限制分配的资源，当系统cpu或者内存不足时，将会减少这些容器的资源

    class AllocationOfTask(object):
        __slots__ = 'uuid','userid','jobid','taskid','resources','bidprice','type'
    
    class AllocationOfMachine(object):
        __slots__ = ['machineid',"resources","reliable_resources_allocation_summary",
                    'reliable_allocation','curr_usage', 'restricted_allocation']

在httprest的main函数中调用以下init方法：

### 数据初始化<a id="sec-10-3-2" name="sec-10-3-2"></a>

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

### allocate方法：<a id="sec-10-3-3" name="sec-10-3-3"></a>

接受job的调度请求，为job中包含的每一个task分配资源，然后把所有的资源打包返回：
选择可靠资源剩余最多的机器，检查是否可以分配可靠资源，如果可以即分配
否则，选择使用率最低的机器，分配受限制资源

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

### has<sub>reliable</sub><sub>resources</sub><a id="sec-10-3-4" name="sec-10-3-4"></a>

    def has_reliable_resources(allocation_of_machine,task_allocation_request):
        if(task_allocation_request['resource']
           +allocation_of_machine.reliable_resources_allocation_summary
           < allocation_of_machine.resources):
            return True
        else:
            return False

### can<sub>preempt</sub><sub>reliable</sub><sub>resources</sub><a id="sec-10-3-5" name="sec-10-3-5"></a>

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

### has<sub>restricted</sub><sub>resources</sub><a id="sec-10-3-6" name="sec-10-3-6"></a>

    def has_restricted_resources(allocation_of_machine,task_allocation_request):
        if(task_allocation_request['resources']
           + curr_usage
           < allocation_of_machine.resources * 0.8):
            return True
        else:
            return False

### allocate<sub>task</sub><a id="sec-10-3-7" name="sec-10-3-7"></a>

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

### allocate<sub>task</sub><sub>restricted</sub><a id="sec-10-3-8" name="sec-10-3-8"></a>

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

### bidscheduler.py<a id="sec-10-3-9" name="sec-10-3-9"></a>

1.  依赖的库

        #  from monitor import summary_resources, summary_usage, curr_usage
        #  from monitor import summary_usage_per_user, summary_usage_per_user
        #  from monitor import curr_usage_per_machine
        from log import logger
        import nodemgr

2.  bidscheduler.py

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

# 待解决的问题：<a id="sec-11" name="sec-11"></a>

## 架构的重构<a id="sec-11-1" name="sec-11-1"></a>

重构成一个独立的调度框架，包括resourcemanager和nodemanager两个独立的进程

## 性能问题，一秒能够处理多少调度请求<a id="sec-11-2" name="sec-11-2"></a>

## 分布式<a id="sec-11-3" name="sec-11-3"></a>

为了提高每秒处理的调度请求，未来将重构为分布式设计，多个resourcemanager协同工作

## 一致性，容错<a id="sec-11-4" name="sec-11-4"></a>

还是需要保存在etcd中
最佳方案是，高可靠的内存数据库

## 调度作业与调度workspace的不同：<a id="sec-11-5" name="sec-11-5"></a>

作业可以排队
创建workspace的请求立即得到回应，为了用户的交互体验，不能排队
之后再考虑是否需要队列

<div id="footnotes">
<h2 class="footnotes">Footnotes: </h2>
<div id="text-footnotes">

<div class="footdef"><sup><a id="fn.1" name="fn.1" class="footnum" href="#fnr.1">1</a></sup> <p>DEFINITION NOT FOUND.</p></div>


</div>
</div>
