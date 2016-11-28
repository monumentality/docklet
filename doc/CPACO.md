<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Container Placement Ant Colony Optimization Algorithm 容器放置蚁群优化算法</a>
<ul>
<li><a href="#sec-1-1">1.1. 目标</a></li>
<li><a href="#sec-1-2">1.2. 模型</a></li>
<li><a href="#sec-1-3">1.3. 已有的求解算法</a>
<ul>
<li><a href="#sec-1-3-1">1.3.1. 精确解</a></li>
<li><a href="#sec-1-3-2">1.3.2. 近似解</a></li>
<li><a href="#sec-1-3-3">1.3.3. 启发式算法</a></li>
<li><a href="#sec-1-3-4">1.3.4. 元启发式算法</a></li>
</ul>
</li>
<li><a href="#sec-1-4">1.4. 蚁群算法：</a>
<ul>
<li><a href="#sec-1-4-1">1.4.1. 为什么使用蚁群优化算法</a></li>
<li><a href="#sec-1-4-2">1.4.2. 算法步骤</a></li>
<li><a href="#sec-1-4-3">1.4.3. 启发规则：</a></li>
<li><a href="#sec-1-4-4">1.4.4. 蚁群计算方法：</a></li>
</ul>
</li>
<li><a href="#sec-1-5">1.5. CPACO 算法描述：</a>
<ul>
<li><a href="#sec-1-5-1">1.5.1. 调度分两个阶段：</a></li>
<li><a href="#sec-1-5-2">1.5.2. 动态调度算法：</a></li>
</ul>
</li>
<li><a href="#sec-1-6">1.6. CPCAO 算法测试：</a>
<ul>
<li><a href="#sec-1-6-1">1.6.1. 解质量对比</a></li>
<li><a href="#sec-1-6-2">1.6.2. 运行时间测试：</a></li>
</ul>
</li>
</ul>
</li>
</ul>
</div>
</div>

# Container Placement Ant Colony Optimization Algorithm 容器放置蚁群优化算法<a id="sec-1" name="sec-1"></a>

## 目标<a id="sec-1-1" name="sec-1-1"></a>

为了达到我们提出的基于拍卖机制的容器调度机制的帕累托最优的目标，需要设计一个算法，能够搜索到一个容器放置解，使集群中放置的容器的总价值最大

## 模型<a id="sec-1-2" name="sec-1-2"></a>

这个问题本质是一个multi-dimensional multiple knapsack problem(MMKP), 多维多背包问题

目前云计算领域研究的一个热点是节约能耗。云计算产业已经成为美国耗能第四多的产业，空气污染仅次于航空业的产业等等。目标是节约能耗的虚拟机放置问题可抽象为 multi-dimensional mutiple bin packing problem (MBP)

MMBP问题与MMKP 问题的区别在于：MMBP每个物品没有价值，最终目标是使用的被报个数最小。两个问题的共同点是：从数学模型看，都是整数线性规划问题N，或者叫组合优化问题，都是NP-Hard问题，求解算法基本是通用的。由于这两个问题很相似，我调研了目标是降低能耗的虚拟机放置算法。

如果我们同时考虑集群资源利用率，降低能耗，容器价值最大的目标，那么这个问题可抽象为 multi-objective multi-dimensional multiple knapsack problem, 多目标多维多背包问题。这是最近一个新的研究方向，在数学领域很新，在云计算领域也比较新。可以成为以后的工作。

## 已有的求解算法<a id="sec-1-3" name="sec-1-3"></a>

### 精确解<a id="sec-1-3-1" name="sec-1-3-1"></a>

精确解几乎等于暴力搜索，指数级复杂度。

例如这篇论文提出了一种精确求解方法。是关于vm的放置算法，目标是最小化能耗（最小化物理机数量），抽象为多维多bin packing问题

Ghribi, Chaima, Makhlouf Hadji, and Djamal Zeghlache. "Energy efficient VM scheduling for cloud data centers: exact allocation and migration algorithms." Cluster, Cloud and Grid Computing (CCGrid), 2013 13th IEEE/ACM International Symposium on. IEEE, 2013.

这篇文章讲的故事是旧故事，大半篇幅是在分析问题和给出模型描述（其他论文都做过），具体的精确算法步骤和实现一点也没讲，相当于用的还是之前的精确算法。看起来几乎是什么创新都没有，居然有68个引用

### 近似解<a id="sec-1-3-2" name="sec-1-3-2"></a>

一维的情况有近似解，多维的情况没有近似解，多背包没有近似解，多维多背包更没有近似解。但还有很多人一直在研究一维的近似算法

### 启发式算法<a id="sec-1-3-3" name="sec-1-3-3"></a>

1.  First Fit Algorithm

    对每一个任务，寻找空闲最多的物理机放置。按FIFO规则处理每个任务

2.  First Fit Decreasing Algorithm

    在first fit algorithm的基础上，用某种启发规则排序任务队列，先考虑

3.  Best Fit Algorithm、Best Fit Decreasing Algorithm

    使各台物理机资源使用平均，从而可以降低迁移次数

4.  vector volume based approach

    资源体积 = cpu \* 内存 \* 带宽，依据体积来排序物理机和虚拟机
    
    xen的sandpiper使用的的虚拟机放置和迁移

5.  vector dot product approach

    RRV: requirement resource vector, 虚拟机资源需求向量
    
    RUV: resource utilization vector, 物理机已利用资源向量
    
    对每一个虚拟机资源请求，寻找使RRV和RUV的数量积最小的物理机
    
    优点：使各维资源利用率尽可能都得到平衡

6.  vector Based Approach

    Mishra, Mayank, and Anirudha Sahoo. "On theory of vm placement: Anomalies in existing methodologies and their mitigation using a novel vector based approach." Cloud Computing (CLOUD), 2011 IEEE International Conference on. IEEE, 2011
    
    这篇论文指出了上述两种基于向量的算法都是有问题的。提出了一种更好的启发规则：利用一个平面六边形，进行一些几何算术，来判断哪个虚拟机放到哪个物理机上

### 元启发式算法<a id="sec-1-3-4" name="sec-1-3-4"></a>

1.  为什么要用元启发式算法

    1.  启发式算法通常比较快速，但生成的解要比局部搜索算法找到的解差
    
    2.  局部搜索比启发式算法慢，但可能终止在一个非常差的局部最优解上
    
    3.  随机进行多次局部搜索，在实际中没有明显改进（1999年论文）
    
    4.  元启发式算法具有全局搜索能力，又有局部寻优能力，遗传算法，模拟退火算法，蚁群优化算法已经在理论上证明能收敛到最优解。

2.  元启发式算法分类

    大家研究和使用比较多的是 模拟退火算法，遗传算法 和 蚁群优化算法。但每种算法都各有优缺点。目前有好多论文是针对不同问题，混合使用多种元启发式算法，发挥每种算法的优点。例如有混合遗传蚁群算法来解决MMKP问题

3.  蚁群优化算法

## 蚁群算法：<a id="sec-1-4" name="sec-1-4"></a>

### 为什么使用蚁群优化算法<a id="sec-1-4-1" name="sec-1-4-1"></a>

蚁群算法可以连续运行并适应实时变化。容器调度问题的问题空间是动态变化的，蚁群优化算法很适合解动态优化问题。

蚁群算法主要利用启发信息和经验信息来指导搜索过程。当待调度任务很多，计算量大，时间紧迫时，可以尽快给出一个可行解，至少比单纯的启发式算法好

使用蚁群算法的优点：局部搜索能力强，可并行，鲁棒性强。可以配合全局搜索能力强的遗传算法使用。

### 算法步骤<a id="sec-1-4-2" name="sec-1-4-2"></a>

主要参考这篇论文：

Ferdaus, Md Hasanul, et al. "Virtual machine consolidation in cloud data centers using ACO metaheuristic." European Conference on Parallel Processing. Springer International Publishing, 2014.

### 启发规则：<a id="sec-1-4-3" name="sec-1-4-3"></a>

主要参考这篇论文：

Mishra, Mayank, and Anirudha Sahoo. "On theory of vm placement: Anomalies in existing methodologies and their mitigation using a novel vector based approach." Cloud Computing (CLOUD), 2011 IEEE International Conference on. IEEE, 2011

1.  计算所有需求的总向量
2.  计算该物理机剩余资源在总向量上的投影的长度 a
3.  计算放置该请求后，物理机剩余资源在总向量的投影的长度 b
4.  该请求的长度 = a - b
5.  计算该资源单位长度的估价： pu = Bid / (a-b)

### 蚁群计算方法：<a id="sec-1-4-4" name="sec-1-4-4"></a>

蚂蚁依次计算每台物理机上可以放置哪些需求：

启发式规则：

计算所有资源的估价，依据估价计算放置概率
放置一个资源后，再计算所有资源的估价和放置概率，再放置一个资源

信息素：某个需求放置到某个物理机上的信息素

## CPACO 算法描述：<a id="sec-1-5" name="sec-1-5"></a>

### 调度分两个阶段：<a id="sec-1-5-1" name="sec-1-5-1"></a>

1.  动态调度：

    每个任务先加入全局队列，按照启发式规则选择某台机器。选择后一段时间就固定在这台机器上了。
    
    每台机器上运行着一个蚁群算法，一直在优化当前可行解。
    
    算法每运行5秒或者100轮，取当前最优解实际的修改cgroup配置

2.  迁移

    频繁的迁移代价太大。因此每隔一段较长时间（10分钟），把所有的容器按照全局调度算法进行重新调度，每个容器可能重新调度到更优的机器上。
    
    这一部分暂时不实现，论文可以描述一下。

### 动态调度算法：<a id="sec-1-5-2" name="sec-1-5-2"></a>

1.  设置一个cpu/mem价格比例，初始值为当前机器的cpu量与内存量的反比，比如物理机为64核，256G内存，cpu与内存价格比为4：1
    
    计算每一个任务的归一化的单位资源价格

2.  为任务选择虚拟机：
    
    从等待队列中选择归一化单价最高的任务
    
    从物理机中选择总价值最低的物理机
    
    这样就把多维多背包松弛为 多个单独的多维背包问题。
    
    为什么可以？大部分容器的大小远小于物理机的大小，容器大小的分布 假设为某种分布（泊松分布），每台物理机上的容器大小分布 最终会趋于平衡。

3.  j-th机器上的调度算法：
    
    启发式规则：把每个任务的归一化单价作为启发式信息
    
    信息素：   在每个任务上释放信息素，依据初始解设置初始信息素
    
    选择概率： 根据启发式规则和信息素和参数计算出选择概率
    
    初始解：贪心算法依据选择概率来得到一个可行解

全局信息素更新：蚁群中每一个蚂蚁，使用伪随机算法，依据选择概率来得到一个可行解。每当得到一个更好的解，就进行全局信息素更新，让当前最好解得任务上的信息素密度更大

局部信息素更新：每个蚂蚁进行一次搜索后，降低它刚走过的路径上的信息素，避免重复

cpu/mem价格比例调整：如果连续多轮，得到的当前最好解的cpu与mem剩余量都不平衡，那么就调整cpu/mem价格比例

停止：当连续多轮搜不到更好解之后，停止

## CPCAO 算法测试：<a id="sec-1-6" name="sec-1-6"></a>

### 解质量对比<a id="sec-1-6-1" name="sec-1-6-1"></a>

1.  与简单贪心算法对比

2.  与最优解对比（只能比小数据量）

3.  与连续松弛的拉格朗日松弛的 上界 进行对比（比较困难）

### 运行时间测试：<a id="sec-1-6-2" name="sec-1-6-2"></a>

目标： 5秒能得到一个相对稳定的解，解质量可以接受
