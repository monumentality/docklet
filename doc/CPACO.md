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
<li><a href="#sec-1-4">1.4. CPACO算法：</a>
<ul>
<li><a href="#sec-1-4-1">1.4.1. 为什么使用蚁群优化算法</a></li>
<li><a href="#sec-1-4-2">1.4.2. 算法步骤</a></li>
<li><a href="#sec-1-4-3">1.4.3. 启发规则：</a></li>
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

## CPACO算法：<a id="sec-1-4" name="sec-1-4"></a>

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
