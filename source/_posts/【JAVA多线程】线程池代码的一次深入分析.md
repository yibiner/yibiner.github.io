---
title: 【JAVA多线程】线程池代码的一次深入分析
top: false
cover: false
toc: true
mathjax: true
date: 2020-09-13 11:35:56
password:
summary: 本文记录了在一次定位线上系统问题时，根据发现的一些问题对JAVA中线程池代码做了下简单的分析
tags:
- JAVA
- 源码分析
- 线程池
categories:
- 编程
---

## 前言

本文记录了在一次定位线上系统问题时，根据发现的一些问题对JAVA中线程池代码做了下简单的分析。作者水平有限，非喜勿喷。





## 背景

在一次统计线上系统每秒处理消息的线程数中，发现有些机器有37个线程在运行，有些机器在重启了服务后由之前的500个线程变为8个线程。在确认了所有机器的JAVA版本、启动参数没有问题后，将分析重点放到了代码中的线程池部分。



将系统中线程池部分的代码单独摘出，写了个demo，方便在单机上分析和复现，代码在[test-thread](https://github.com/yibiner/blog-demo-code/tree/master/test-thread)，下文中的实例分析和代码验证都是在这个demo上跑的，读者可以自行验证。



系统版本

```sh
$ uname -a
Linux linux 5.4.0-45-generic #49~18.04.2-Ubuntu SMP Wed Aug 26 16:29:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

JAVA版本

```sh
$ java -version
java version "1.8.0_241"
Java(TM) SE Runtime Environment (build 1.8.0_241-b07)
Java HotSpot(TM) 64-Bit Server VM (build 25.241-b07, mixed mode)
```





##  线程池源码简单分析

由示例代码中可以看到

```java
BlockingQueue<Runnable> workQueue = new LinkedBlockingQueue<>(20);
RejectedExecutionHandler handler = new BlockRejectedExecutionHandler();
executor = new ThreadPoolExecutor(corePoolSize, executorMaximumPoolSize, 1, TimeUnit.SECONDS, workQueue, handler);
```

线程池直接使用了 ThreadPoolExecutor ，任务队列使用了 LinkedBlockingQueue 并设置了size，拒绝策略自行实现了 RejectedExecutionHandler 。

所以重点在于 ThreadPoolExecutor 的内部实现。



### 源码与简单解释

```java
/**
     * Creates a new {@code ThreadPoolExecutor} with the given initial
     * parameters and default thread factory.
     *
     * @param corePoolSize the number of threads to keep in the pool, even
     *        if they are idle, unless {@code allowCoreThreadTimeOut} is set
     * @param maximumPoolSize the maximum number of threads to allow in the
     *        pool
     * @param keepAliveTime when the number of threads is greater than
     *        the core, this is the maximum time that excess idle threads
     *        will wait for new tasks before terminating.
     * @param unit the time unit for the {@code keepAliveTime} argument
     * @param workQueue the queue to use for holding tasks before they are
     *        executed.  This queue will hold only the {@code Runnable}
     *        tasks submitted by the {@code execute} method.
     * @param handler the handler to use when execution is blocked
     *        because the thread bounds and queue capacities are reached
     * @throws IllegalArgumentException if one of the following holds:<br>
     *         {@code corePoolSize < 0}<br>
     *         {@code keepAliveTime < 0}<br>
     *         {@code maximumPoolSize <= 0}<br>
     *         {@code maximumPoolSize < corePoolSize}
     * @throws NullPointerException if {@code workQueue}
     *         or {@code handler} is null
     */
    public ThreadPoolExecutor(int corePoolSize,
                              int maximumPoolSize,
                              long keepAliveTime,
                              TimeUnit unit,
                              BlockingQueue<Runnable> workQueue,
                              RejectedExecutionHandler handler) {
        this(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue,
             Executors.defaultThreadFactory(), handler);
    }
```

- corePoolSize

  线程池中的核心线程数。除非设置了allowCoreThreadTimeOut，否则一直存活。

- maximumPoolSize

  线程池中的最大线程数。

- workQueue

  用于保存还没执行到的任务的队列。

- handler

  线程池的饱和策略，当线程池中的阻塞队列满了，且没有空闲的工作线程，如果继续提交任务，需要进行某种处理，默认是抛出异常，这里是将任务放入workQueue中



```java
//只是对参数做了判空
public ThreadPoolExecutor(int corePoolSize,
                              int maximumPoolSize,
                              long keepAliveTime,
                              TimeUnit unit,
                              BlockingQueue<Runnable> workQueue,
                              ThreadFactory threadFactory,
                              RejectedExecutionHandler handler) {
        if (corePoolSize < 0 ||
            maximumPoolSize <= 0 ||
            maximumPoolSize < corePoolSize ||
            keepAliveTime < 0)
            throw new IllegalArgumentException();
        if (workQueue == null || threadFactory == null || handler == null)
            throw new NullPointerException();
        this.acc = System.getSecurityManager() == null ?
                null :
                AccessController.getContext();
        this.corePoolSize = corePoolSize;
        this.maximumPoolSize = maximumPoolSize;
        this.workQueue = workQueue;
        this.keepAliveTime = unit.toNanos(keepAliveTime);
        this.threadFactory = threadFactory;
        this.handler = handler;
    }
```





```java
//提交任务时调用    execute ，源码中的注释已经将基本的流程说明清楚了，这里就不翻译了。
public void execute(Runnable command) {
    if (command == null)
        throw new NullPointerException();
    /*
         * Proceed in 3 steps:
         *
         * 1. If fewer than corePoolSize threads are running, try to
         * start a new thread with the given command as its first
         * task.  The call to addWorker atomically checks runState and
         * workerCount, and so prevents false alarms that would add
         * threads when it shouldn't, by returning false.
         *
         * 2. If a task can be successfully queued, then we still need
         * to double-check whether we should have added a thread
         * (because existing ones died since last checking) or that
         * the pool shut down since entry into this method. So we
         * recheck state and if necessary roll back the enqueuing if
         * stopped, or start a new thread if there are none.
         *
         * 3. If we cannot queue task, then we try to add a new
         * thread.  If it fails, we know we are shut down or saturated
         * and so reject the task.
         */
    int c = ctl.get();
    if (workerCountOf(c) < corePoolSize) {
        if (addWorker(command, true))
            return;
        c = ctl.get();
    }
    //isRunning 线程池使用int 的前个二进制3位表示状态，后29位表示数量，具体值看下面说明。
    //当当前运行的线程数量大于设定的核心线程数量时，会优先将任务放入队列中。
    //代入实际业务处理，此处会导致任务数小于队列最大值时，线程池中只有核心线程在处理
    if (isRunning(c) && workQueue.offer(command)) {
        int recheck = ctl.get();
        if (! isRunning(recheck) && remove(command))
            reject(command);
        else if (workerCountOf(recheck) == 0)
            addWorker(null, false);
    }
    //若队列已经满了，则会尝试将直接添加worker，若当前核心线程数小于设定的最大线程数，则会新增线程。
    //代入实际业务处理，此处会导致当模块启动时，待处理任务数为70，大于队列最大长度50，若核心线程数是8，最大线程数是30，则会使线程数增加到20处理任务；若核心线程数是8，最大线程数是10，则会增加到10个线程数，且有部分任务会执行reject策略。详细见下面实例分析
    else if (!addWorker(command, false))
        reject(command);
}
```





```java
private static final int COUNT_BITS = Integer.SIZE - 3;//29
private static final int CAPACITY   = (1 << COUNT_BITS) - 1;//1左移29位后，二进制表示： 10 0000 0000 0000 0000 0000 0000 0000 ，-1 后则为 1 1111 1111 1111 1111 1111 1111 1111

// runState is stored in the high-order bits
private static final int RUNNING    = -1 << COUNT_BITS;     //11100000000000000000000000000000
private static final int SHUTDOWN   =  0 << COUNT_BITS; //0
private static final int STOP       =  1 << COUNT_BITS;   		   //100000000000000000000000000000
private static final int TIDYING    =  2 << COUNT_BITS;  		//1000000000000000000000000000000
private static final int TERMINATED =  3 << COUNT_BITS;  //1100000000000000000000000000000

// Packing and unpacking ctl
private static int runStateOf(int c)     { return c & ~CAPACITY; }
private static int workerCountOf(int c)  { return c & CAPACITY; }
private static int ctlOf(int rs, int wc) { return rs | wc; }
```

```java
//根据设定的核心线程数和最大线程数来决定是否要新增线程来处理任务
/**
     * Checks if a new worker can be added with respect to current
     * pool state and the given bound (either core or maximum). If so,
     * the worker count is adjusted accordingly, and, if possible, a
     * new worker is created and started, running firstTask as its
     * first task. This method returns false if the pool is stopped or
     * eligible to shut down. It also returns false if the thread
     * factory fails to create a thread when asked.  If the thread
     * creation fails, either due to the thread factory returning
     * null, or due to an exception (typically OutOfMemoryError in
     * Thread.start()), we roll back cleanly.
     *
     * @param firstTask the task the new thread should run first (or
     * null if none). Workers are created with an initial first task
     * (in method execute()) to bypass queuing when there are fewer
     * than corePoolSize threads (in which case we always start one),
     * or when the queue is full (in which case we must bypass queue).
     * Initially idle threads are usually created via
     * prestartCoreThread or to replace other dying workers.
     *
     * @param core if true use corePoolSize as bound, else
     * maximumPoolSize. (A boolean indicator is used here rather than a
     * value to ensure reads of fresh values after checking other pool
     * state).
     * @return true if successful
     */
private boolean addWorker(Runnable firstTask, boolean core) {
    retry:
    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        // Check if queue empty only if necessary.
        if (rs >= SHUTDOWN &&
            ! (rs == SHUTDOWN &&
               firstTask == null &&
               ! workQueue.isEmpty()))
            return false;

        for (;;) {
            int wc = workerCountOf(c);
            if (wc >= CAPACITY ||
                wc >= (core ? corePoolSize : maximumPoolSize))
                return false;
            if (compareAndIncrementWorkerCount(c))
                break retry;
            c = ctl.get();  // Re-read ctl
            if (runStateOf(c) != rs)
                continue retry;
            // else CAS failed due to workerCount change; retry inner loop
        }
    }

    boolean workerStarted = false;
    boolean workerAdded = false;
    Worker w = null;
    try {
        w = new Worker(firstTask);
        final Thread t = w.thread;
        if (t != null) {
            final ReentrantLock mainLock = this.mainLock;
            mainLock.lock();
            try {
                // Recheck while holding lock.
                // Back out on ThreadFactory failure or if
                // shut down before lock acquired.
                int rs = runStateOf(ctl.get());

                if (rs < SHUTDOWN ||
                    (rs == SHUTDOWN && firstTask == null)) {
                    if (t.isAlive()) // precheck that t is startable
                        throw new IllegalThreadStateException();
                    workers.add(w);
                    int s = workers.size();
                    if (s > largestPoolSize)
                        largestPoolSize = s;
                    workerAdded = true;
                }
            } finally {
                mainLock.unlock();
            }
            if (workerAdded) {
                t.start();
                workerStarted = true;
            }
        }
    } finally {
        if (! workerStarted)
            addWorkerFailed(w);
    }
    return workerStarted;
}
```





### 实例分析与代码验证

- 核心线程数4，最大线程数10，队列长度20，任务数20

```shell
$ mvn spring-boot:run
2020-09-13 13:58:54.531  INFO 19092 --- [  restartedMain] com.neo.WebFluxApplication               : Started WebFluxApplication in 1.176 seconds (JVM running for 1.413)
2020-09-13 13:58:54.533  INFO 19092 --- [pool-1-thread-1] com.neo.web.MessageService               : running 0 ActiveCount: 2 PoolSize:2 TaskCount:2 Queue size:0
2020-09-13 13:58:54.533  INFO 19092 --- [pool-1-thread-2] com.neo.web.MessageService               : running 1 ActiveCount: 3 PoolSize:3 TaskCount:3 Queue size:0
2020-09-13 13:58:54.533  INFO 19092 --- [pool-1-thread-3] com.neo.web.MessageService               : running 2 ActiveCount: 4 PoolSize:4 TaskCount:4 Queue size:0
2020-09-13 13:58:54.537  INFO 19092 --- [pool-1-thread-4] com.neo.web.MessageService               : running 3 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:16
2020-09-13 13:58:54.543  INFO 19092 --- [pool-1-thread-1] com.neo.web.MessageService               : running 4 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:15
2020-09-13 13:58:54.543  INFO 19092 --- [pool-1-thread-2] com.neo.web.MessageService               : running 5 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:14
2020-09-13 13:58:54.543  INFO 19092 --- [pool-1-thread-3] com.neo.web.MessageService               : running 6 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:13
2020-09-13 13:58:54.547  INFO 19092 --- [pool-1-thread-4] com.neo.web.MessageService               : running 7 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:12
2020-09-13 13:58:54.553  INFO 19092 --- [pool-1-thread-2] com.neo.web.MessageService               : running 9 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:10
2020-09-13 13:58:54.553  INFO 19092 --- [pool-1-thread-1] com.neo.web.MessageService               : running 8 ActiveCount: 3 PoolSize:4 TaskCount:19 Queue size:10
2020-09-13 13:58:54.554  INFO 19092 --- [pool-1-thread-3] com.neo.web.MessageService               : running 10 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:9
2020-09-13 13:58:54.557  INFO 19092 --- [pool-1-thread-4] com.neo.web.MessageService               : running 11 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:8
2020-09-13 13:58:54.564  INFO 19092 --- [pool-1-thread-1] com.neo.web.MessageService               : running 13 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:6
2020-09-13 13:58:54.564  INFO 19092 --- [pool-1-thread-2] com.neo.web.MessageService               : running 12 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:7
2020-09-13 13:58:54.564  INFO 19092 --- [pool-1-thread-3] com.neo.web.MessageService               : running 14 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:5
2020-09-13 13:58:54.567  INFO 19092 --- [pool-1-thread-4] com.neo.web.MessageService               : running 15 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:4
2020-09-13 13:58:54.574  INFO 19092 --- [pool-1-thread-2] com.neo.web.MessageService               : running 17 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:2
2020-09-13 13:58:54.574  INFO 19092 --- [pool-1-thread-3] com.neo.web.MessageService               : running 18 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:1
2020-09-13 13:58:54.574  INFO 19092 --- [pool-1-thread-1] com.neo.web.MessageService               : running 16 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:3
2020-09-13 13:58:54.578  INFO 19092 --- [pool-1-thread-4] com.neo.web.MessageService               : running 19 ActiveCount: 4 PoolSize:4 TaskCount:20 Queue size:0

```

任务数量小于队列最大长度时，20个任务由4个线程消费完





- 核心线程数4，最大线程数10，队列长度20，任务数30

```shell
2020-09-13 14:06:55.919  INFO 20216 --- [  restartedMain] com.neo.WebFluxApplication               : Started WebFluxApplication in 1.177 seconds (JVM running for 1.412)
2020-09-13 14:06:55.921  INFO 20216 --- [pool-1-thread-1] com.neo.web.MessageService               : running 0 ActiveCount: 2 PoolSize:2 TaskCount:2 Queue size:0
2020-09-13 14:06:55.921  INFO 20216 --- [pool-1-thread-2] com.neo.web.MessageService               : running 1 ActiveCount: 3 PoolSize:3 TaskCount:3 Queue size:0
2020-09-13 14:06:55.921  INFO 20216 --- [pool-1-thread-3] com.neo.web.MessageService               : running 2 ActiveCount: 4 PoolSize:4 TaskCount:5 Queue size:1
2020-09-13 14:06:55.921  INFO 20216 --- [pool-1-thread-4] com.neo.web.MessageService               : running 3 ActiveCount: 5 PoolSize:5 TaskCount:25 Queue size:20
2020-09-13 14:06:55.922  INFO 20216 --- [pool-1-thread-5] com.neo.web.MessageService               : running 24 ActiveCount: 6 PoolSize:6 TaskCount:26 Queue size:20
2020-09-13 14:06:55.922  INFO 20216 --- [pool-1-thread-6] com.neo.web.MessageService               : running 25 ActiveCount: 7 PoolSize:7 TaskCount:27 Queue size:20
2020-09-13 14:06:55.924  INFO 20216 --- [pool-1-thread-7] com.neo.web.MessageService               : running 26 ActiveCount: 8 PoolSize:8 TaskCount:28 Queue size:20
2020-09-13 14:06:55.924  INFO 20216 --- [pool-1-thread-8] com.neo.web.MessageService               : running 27 ActiveCount: 9 PoolSize:9 TaskCount:29 Queue size:20
2020-09-13 14:06:55.925  INFO 20216 --- [pool-1-thread-9] com.neo.web.MessageService               : running 28 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:20
2020-09-13 14:06:55.925  INFO 20216 --- [ool-1-thread-10] com.neo.web.MessageService               : running 29 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:20
2020-09-13 14:06:55.931  INFO 20216 --- [pool-1-thread-1] com.neo.web.MessageService               : running 4 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:19
2020-09-13 14:06:55.931  INFO 20216 --- [pool-1-thread-2] com.neo.web.MessageService               : running 5 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:18
2020-09-13 14:06:55.931  INFO 20216 --- [pool-1-thread-3] com.neo.web.MessageService               : running 6 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:17
2020-09-13 14:06:55.931  INFO 20216 --- [pool-1-thread-4] com.neo.web.MessageService               : running 7 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:16
2020-09-13 14:06:55.932  INFO 20216 --- [pool-1-thread-5] com.neo.web.MessageService               : running 8 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:15
2020-09-13 14:06:55.932  INFO 20216 --- [pool-1-thread-6] com.neo.web.MessageService               : running 9 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:14
2020-09-13 14:06:55.934  INFO 20216 --- [pool-1-thread-7] com.neo.web.MessageService               : running 10 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:13
2020-09-13 14:06:55.934  INFO 20216 --- [pool-1-thread-8] com.neo.web.MessageService               : running 11 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:12
2020-09-13 14:06:55.935  INFO 20216 --- [pool-1-thread-9] com.neo.web.MessageService               : running 12 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:11
2020-09-13 14:06:55.935  INFO 20216 --- [ool-1-thread-10] com.neo.web.MessageService               : running 13 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:10
2020-09-13 14:06:55.941  INFO 20216 --- [pool-1-thread-1] com.neo.web.MessageService               : running 14 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:9
2020-09-13 14:06:55.941  INFO 20216 --- [pool-1-thread-2] com.neo.web.MessageService               : running 15 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:8
2020-09-13 14:06:55.941  INFO 20216 --- [pool-1-thread-3] com.neo.web.MessageService               : running 16 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:7
2020-09-13 14:06:55.942  INFO 20216 --- [pool-1-thread-4] com.neo.web.MessageService               : running 17 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:6
2020-09-13 14:06:55.942  INFO 20216 --- [pool-1-thread-5] com.neo.web.MessageService               : running 18 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:5
2020-09-13 14:06:55.942  INFO 20216 --- [pool-1-thread-6] com.neo.web.MessageService               : running 19 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:4
2020-09-13 14:06:55.944  INFO 20216 --- [pool-1-thread-7] com.neo.web.MessageService               : running 20 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:3
2020-09-13 14:06:55.944  INFO 20216 --- [pool-1-thread-8] com.neo.web.MessageService               : running 21 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:2
2020-09-13 14:06:55.945  INFO 20216 --- [pool-1-thread-9] com.neo.web.MessageService               : running 22 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:1
2020-09-13 14:06:55.945  INFO 20216 --- [ool-1-thread-10] com.neo.web.MessageService               : running 23 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:0

```

任务数量大于队列最大长度，任务数量-队列最大长度<最大线程数量时，超过队列最大长度的任务会尝试新增线程（由日志中第6行可以推断出），30个任务由10个线程消费完。

且如果任务数设置为27，则处理任务线程数为7，这也就解释了实际环境中为什么有时候会有37个线程处理消息，有时候有500个线程处理（最大线程数值模块设置为500）。





- 核心线程数4，最大线程数10，队列长度20，任务数50

```shell
2020-09-13 14:14:11.501  INFO 20899 --- [  restartedMain] com.neo.WebFluxApplication               : Started WebFluxApplication in 1.17 seconds (JVM running for 1.402)
2020-09-13 14:14:11.504  INFO 20899 --- [pool-1-thread-1] com.neo.web.MessageService               : running 0 ActiveCount: 3 PoolSize:3 TaskCount:3 Queue size:0
2020-09-13 14:14:11.504  INFO 20899 --- [pool-1-thread-2] com.neo.web.MessageService               : running 1 ActiveCount: 3 PoolSize:3 TaskCount:3 Queue size:0
2020-09-13 14:14:11.509  INFO 20899 --- [pool-1-thread-7] com.neo.web.MessageService               : running 26 ActiveCount: 8 PoolSize:8 TaskCount:28 Queue size:20
2020-09-13 14:14:11.504  INFO 20899 --- [pool-1-thread-3] com.neo.web.MessageService               : running 2 ActiveCount: 4 PoolSize:4 TaskCount:4 Queue size:0
2020-09-13 14:14:11.505  INFO 20899 --- [pool-1-thread-4] com.neo.web.MessageService               : running 3 ActiveCount: 5 PoolSize:5 TaskCount:25 Queue size:20
2020-09-13 14:14:11.505  INFO 20899 --- [pool-1-thread-5] com.neo.web.MessageService               : running 24 ActiveCount: 7 PoolSize:7 TaskCount:27 Queue size:20
2020-09-13 14:14:11.505  INFO 20899 --- [pool-1-thread-6] com.neo.web.MessageService               : running 25 ActiveCount: 7 PoolSize:7 TaskCount:27 Queue size:20
2020-09-13 14:14:11.510  INFO 20899 --- [pool-1-thread-8] com.neo.web.MessageService               : running 27 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:20
2020-09-13 14:14:11.510  INFO 20899 --- [ool-1-thread-10] com.neo.web.MessageService               : running 29 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:20
2020-09-13 14:14:11.510  INFO 20899 --- [pool-1-thread-9] com.neo.web.MessageService               : running 28 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:20
2020-09-13 14:14:11.515  INFO 20899 --- [pool-1-thread-1] com.neo.web.MessageService               : running 4 ActiveCount: 10 PoolSize:10 TaskCount:30 Queue size:19
2020-09-13 14:14:11.519  INFO 20899 --- [pool-1-thread-7] com.neo.web.MessageService               : running 5 ActiveCount: 10 PoolSize:10 TaskCount:31 Queue size:19
2020-09-13 14:14:11.520  INFO 20899 --- [pool-1-thread-2] com.neo.web.MessageService               : running 6 ActiveCount: 10 PoolSize:10 TaskCount:32 Queue size:19
2020-09-13 14:14:11.520  INFO 20899 --- [pool-1-thread-3] com.neo.web.MessageService               : running 7 ActiveCount: 10 PoolSize:10 TaskCount:33 Queue size:19
2020-09-13 14:14:11.522  INFO 20899 --- [pool-1-thread-8] com.neo.web.MessageService               : running 9 ActiveCount: 9 PoolSize:10 TaskCount:34 Queue size:19
2020-09-13 14:14:11.522  INFO 20899 --- [ool-1-thread-10] com.neo.web.MessageService               : running 8 ActiveCount: 10 PoolSize:10 TaskCount:36 Queue size:20
2020-09-13 14:14:11.522  INFO 20899 --- [pool-1-thread-5] com.neo.web.MessageService               : running 10 ActiveCount: 10 PoolSize:10 TaskCount:36 Queue size:19
2020-09-13 14:14:11.522  INFO 20899 --- [pool-1-thread-4] com.neo.web.MessageService               : running 11 ActiveCount: 10 PoolSize:10 TaskCount:37 Queue size:19
2020-09-13 14:14:11.523  INFO 20899 --- [pool-1-thread-6] com.neo.web.MessageService               : running 13 ActiveCount: 10 PoolSize:10 TaskCount:40 Queue size:20
2020-09-13 14:14:11.523  INFO 20899 --- [pool-1-thread-9] com.neo.web.MessageService               : running 12 ActiveCount: 10 PoolSize:10 TaskCount:39 Queue size:20
2020-09-13 14:14:11.525  INFO 20899 --- [pool-1-thread-1] com.neo.web.MessageService               : running 14 ActiveCount: 10 PoolSize:10 TaskCount:40 Queue size:19
2020-09-13 14:14:11.529  INFO 20899 --- [pool-1-thread-7] com.neo.web.MessageService               : running 15 ActiveCount: 10 PoolSize:10 TaskCount:42 Queue size:20
2020-09-13 14:14:11.530  INFO 20899 --- [pool-1-thread-2] com.neo.web.MessageService               : running 16 ActiveCount: 10 PoolSize:10 TaskCount:42 Queue size:19
2020-09-13 14:14:11.530  INFO 20899 --- [pool-1-thread-3] com.neo.web.MessageService               : running 17 ActiveCount: 10 PoolSize:10 TaskCount:44 Queue size:20
2020-09-13 14:14:11.532  INFO 20899 --- [ool-1-thread-10] com.neo.web.MessageService               : running 19 ActiveCount: 10 PoolSize:10 TaskCount:45 Queue size:19
2020-09-13 14:14:11.532  INFO 20899 --- [pool-1-thread-8] com.neo.web.MessageService               : running 18 ActiveCount: 10 PoolSize:10 TaskCount:44 Queue size:19
2020-09-13 14:14:11.532  INFO 20899 --- [pool-1-thread-4] com.neo.web.MessageService               : running 20 ActiveCount: 10 PoolSize:10 TaskCount:46 Queue size:18
2020-09-13 14:14:11.532  INFO 20899 --- [pool-1-thread-5] com.neo.web.MessageService               : running 21 ActiveCount: 10 PoolSize:10 TaskCount:46 Queue size:18
2020-09-13 14:14:11.533  INFO 20899 --- [pool-1-thread-9] com.neo.web.MessageService               : running 22 ActiveCount: 10 PoolSize:10 TaskCount:48 Queue size:18
2020-09-13 14:14:11.533  INFO 20899 --- [pool-1-thread-6] com.neo.web.MessageService               : running 23 ActiveCount: 9 PoolSize:10 TaskCount:48 Queue size:18
2020-09-13 14:14:11.535  INFO 20899 --- [pool-1-thread-1] com.neo.web.MessageService               : running 30 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:19
2020-09-13 14:14:11.539  INFO 20899 --- [pool-1-thread-7] com.neo.web.MessageService               : running 31 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:18
2020-09-13 14:14:11.540  INFO 20899 --- [pool-1-thread-3] com.neo.web.MessageService               : running 32 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:17
2020-09-13 14:14:11.540  INFO 20899 --- [pool-1-thread-2] com.neo.web.MessageService               : running 33 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:16
2020-09-13 14:14:11.544  INFO 20899 --- [pool-1-thread-5] com.neo.web.MessageService               : running 36 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:13
2020-09-13 14:14:11.544  INFO 20899 --- [pool-1-thread-4] com.neo.web.MessageService               : running 37 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:12
2020-09-13 14:14:11.544  INFO 20899 --- [pool-1-thread-8] com.neo.web.MessageService               : running 38 ActiveCount: 9 PoolSize:10 TaskCount:50 Queue size:11
2020-09-13 14:14:11.544  INFO 20899 --- [ool-1-thread-10] com.neo.web.MessageService               : running 39 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:10
2020-09-13 14:14:11.544  INFO 20899 --- [pool-1-thread-6] com.neo.web.MessageService               : running 35 ActiveCount: 9 PoolSize:10 TaskCount:50 Queue size:13
2020-09-13 14:14:11.544  INFO 20899 --- [pool-1-thread-9] com.neo.web.MessageService               : running 34 ActiveCount: 8 PoolSize:10 TaskCount:50 Queue size:14
2020-09-13 14:14:11.545  INFO 20899 --- [pool-1-thread-1] com.neo.web.MessageService               : running 40 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:9
2020-09-13 14:14:11.550  INFO 20899 --- [pool-1-thread-7] com.neo.web.MessageService               : running 41 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:8
2020-09-13 14:14:11.552  INFO 20899 --- [pool-1-thread-2] com.neo.web.MessageService               : running 42 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:7
2020-09-13 14:14:11.552  INFO 20899 --- [pool-1-thread-3] com.neo.web.MessageService               : running 43 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:6
2020-09-13 14:14:11.554  INFO 20899 --- [pool-1-thread-8] com.neo.web.MessageService               : running 45 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:4
2020-09-13 14:14:11.554  INFO 20899 --- [pool-1-thread-5] com.neo.web.MessageService               : running 44 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:4
2020-09-13 14:14:11.555  INFO 20899 --- [pool-1-thread-4] com.neo.web.MessageService               : running 46 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:3
2020-09-13 14:14:11.555  INFO 20899 --- [ool-1-thread-10] com.neo.web.MessageService               : running 47 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:2
2020-09-13 14:14:11.556  INFO 20899 --- [pool-1-thread-1] com.neo.web.MessageService               : running 48 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:1
2020-09-13 14:14:11.558  INFO 20899 --- [pool-1-thread-6] com.neo.web.MessageService               : running 49 ActiveCount: 10 PoolSize:10 TaskCount:50 Queue size:0

```

任务数量大于最大线程数加上队列长度，会执行拒绝策略，在此处重写了 rejectedExecution 使用put阻塞将消息插入队列，所以所有任务都会被处理。



至此，如何产生不同数量线程的原因找到了，但更进一步思考，非核心线程在产生之后 就会一直存在去处理消息吗？有没有什么情况下整个线程池的线程数量会下降为核心线程数量？





## 添加线程后续

### 源码与简单解释

```java
private boolean addWorker(Runnable firstTask, boolean core) {
    retry:
    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        // Check if queue empty only if necessary.
        if (rs >= SHUTDOWN &&
            ! (rs == SHUTDOWN &&
               firstTask == null &&
               ! workQueue.isEmpty()))
            return false;

        for (;;) {
            int wc = workerCountOf(c);
            if (wc >= CAPACITY ||
                wc >= (core ? corePoolSize : maximumPoolSize))
                return false;
            if (compareAndIncrementWorkerCount(c))
                break retry;
            c = ctl.get();  // Re-read ctl
            if (runStateOf(c) != rs)
                continue retry;
            // else CAS failed due to workerCount change; retry inner loop
        }
    }

    boolean workerStarted = false;
    boolean workerAdded = false;
    Worker w = null;
    try {
        w = new Worker(firstTask);
        final Thread t = w.thread;
        if (t != null) {
            //获取锁
            final ReentrantLock mainLock = this.mainLock;
            mainLock.lock();
            try {
                // Recheck while holding lock.
                // Back out on ThreadFactory failure or if
                // shut down before lock acquired.
                int rs = runStateOf(ctl.get());

                if (rs < SHUTDOWN ||
                    (rs == SHUTDOWN && firstTask == null)) {
                    if (t.isAlive()) // precheck that t is startable
                        throw new IllegalThreadStateException();
                    //workers是hashset， getPoolSize 方法获取的就是workers的大小
                    workers.add(w);
                    int s = workers.size();
                    if (s > largestPoolSize)
                        largestPoolSize = s;
                    workerAdded = true;
                }
            } finally {
                mainLock.unlock();
            }
            if (workerAdded) {
                t.start();
                workerStarted = true;
            }
        }
    } finally {
        if (! workerStarted)
            addWorkerFailed(w);
    }
    return workerStarted;
}
```

```java
/**
         * Creates with given first task and thread from ThreadFactory.
         * @param firstTask the first task (null if none)
         */
Worker(Runnable firstTask) {
    setState(-1); // inhibit interrupts until runWorker
    this.firstTask = firstTask;
    this.thread = getThreadFactory().newThread(this);
}

/** Delegates main run loop to outer runWorker  */
public void run() {
    runWorker(this);
}

/**
     * Main worker run loop.  Repeatedly gets tasks from queue and
     * executes them, while coping with a number of issues:
     *
     * 1. We may start out with an initial task, in which case we
     * don't need to get the first one. Otherwise, as long as pool is
     * running, we get tasks from getTask. If it returns null then the
     * worker exits due to changed pool state or configuration
     * parameters.  Other exits result from exception throws in
     * external code, in which case completedAbruptly holds, which
     * usually leads processWorkerExit to replace this thread.
     *
     * 2. Before running any task, the lock is acquired to prevent
     * other pool interrupts while the task is executing, and then we
     * ensure that unless pool is stopping, this thread does not have
     * its interrupt set.
     *
     * 3. Each task run is preceded by a call to beforeExecute, which
     * might throw an exception, in which case we cause thread to die
     * (breaking loop with completedAbruptly true) without processing
     * the task.
     *
     * 4. Assuming beforeExecute completes normally, we run the task,
     * gathering any of its thrown exceptions to send to afterExecute.
     * We separately handle RuntimeException, Error (both of which the
     * specs guarantee that we trap) and arbitrary Throwables.
     * Because we cannot rethrow Throwables within Runnable.run, we
     * wrap them within Errors on the way out (to the thread's
     * UncaughtExceptionHandler).  Any thrown exception also
     * conservatively causes thread to die.
     *
     * 5. After task.run completes, we call afterExecute, which may
     * also throw an exception, which will also cause thread to
     * die. According to JLS Sec 14.20, this exception is the one that
     * will be in effect even if task.run throws.
     *
     * The net effect of the exception mechanics is that afterExecute
     * and the thread's UncaughtExceptionHandler have as accurate
     * information as we can provide about any problems encountered by
     * user code.
     *
     * @param w the worker
     */
final void runWorker(Worker w) {
    Thread wt = Thread.currentThread();
    Runnable task = w.firstTask;
    w.firstTask = null;
    w.unlock(); // allow interrupts
    boolean completedAbruptly = true;
    try
        //当启动了一个worker之后，会一直去获取队列里面的任务。 这也就是当 任务数量大于队列长度时，新增的线程会一直工作下去的原因
        while (task != null || (task = getTask()) != null) {
            w.lock();
            // If pool is stopping, ensure thread is interrupted;
            // if not, ensure thread is not interrupted.  This
            // requires a recheck in second case to deal with
            // shutdownNow race while clearing interrupt
            if ((runStateAtLeast(ctl.get(), STOP) ||
                 (Thread.interrupted() &&
                  runStateAtLeast(ctl.get(), STOP))) &&
                !wt.isInterrupted())
                wt.interrupt();
            try {
                beforeExecute(wt, task);
                Throwable thrown = null;
                try {
                    task.run();
                } catch (RuntimeException x) {
                    thrown = x; throw x;
                } catch (Error x) {
                    thrown = x; throw x;
                } catch (Throwable x) {
                    thrown = x; throw new Error(x);
                } finally {
                    afterExecute(task, thrown);
                }
            } finally {
                task = null;
                w.completedTasks++;
                w.unlock();
            }
        }
        completedAbruptly = false;
    } finally {
        processWorkerExit(w, completedAbruptly);
    }
}

/**
     * Performs blocking or timed wait for a task, depending on
     * current configuration settings, or returns null if this worker
     * must exit because of any of:
     * 1. There are more than maximumPoolSize workers (due to
     *    a call to setMaximumPoolSize).
     * 2. The pool is stopped.
     * 3. The pool is shutdown and the queue is empty.
     * 4. This worker timed out waiting for a task, and timed-out
     *    workers are subject to termination (that is,
     *    {@code allowCoreThreadTimeOut || workerCount > corePoolSize})
     *    both before and after the timed wait, and if the queue is
     *    non-empty, this worker is not the last thread in the pool.
     *
     * @return task, or null if the worker must exit, in which case
     *         workerCount is decremented
     */
private Runnable getTask() {
    boolean timedOut = false; // Did the last poll() time out?

    for (;;) {
        int c = ctl.get();
        int rs = runStateOf(c);

        // Check if queue empty only if necessary.
        if (rs >= SHUTDOWN && (rs >= STOP || workQueue.isEmpty())) {
            decrementWorkerCount();
            return null;
        }

        int wc = workerCountOf(c);

        // Are workers subject to culling?
        //在本次设置中没有设置allowCoreThreadTimeOut，所以为默认值false。 任务数量大于队列长度时， wc > corePoolSize 成立，不过也就是会让下面获取下个任务多了个超时检查而已。 若60s（在本案例中的设置）队列为空，就会关闭超过核心线程的部分（不过对于当前业务来说，永远不会关闭 :)  ）
        boolean timed = allowCoreThreadTimeOut || wc > corePoolSize;

        if ((wc > maximumPoolSize || (timed && timedOut))
            && (wc > 1 || workQueue.isEmpty())) {
            if (compareAndDecrementWorkerCount(c))
                return null;
            continue;
        }

        try {
            //poll和take差别在于poll多了keepAliveTime的检查，最后都是调用dequeue
            Runnable r = timed ?
                workQueue.poll(keepAliveTime, TimeUnit.NANOSECONDS) :
            workQueue.take();
            if (r != null)
                return r;
            timedOut = true;
        } catch (InterruptedException retry) {
            timedOut = false;
        }
    }
}
```





### 实例分析与代码验证

- 将线程池设置参数 keepAliveTime 设为1s，在所有任务处理完后查看线程池中的线程数量，可以验证。2s 后线程数量等于设置的核心线程数

```shell
2020-09-14 13:42:01.380  INFO 13147 --- [  restartedMain] com.neo.web.MessageService               : 500ms ActiveCount: 0 PoolSize:10 TaskCount:50 Queue size:0
2020-09-14 13:42:03.381  INFO 13147 --- [  restartedMain] com.neo.web.MessageService               : 2s ActiveCount: 0 PoolSize:4 TaskCount:50 Queue size:0

```

- 将  allowCoreThreadTimeOut 设置为 true。2s 后线程池中线程数连核心线程也不在保持

```shell
2020-09-14 13:47:39.829  INFO 14381 --- [  restartedMain] com.neo.web.MessageService               : 500ms ActiveCount: 0 PoolSize:10 TaskCount:50 Queue size:0
2020-09-14 13:47:41.829  INFO 14381 --- [  restartedMain] com.neo.web.MessageService               : 2s ActiveCount: 0 PoolSize:0 TaskCount:50 Queue size:0

```





## 结论与参数说明

- **corePoolSize** :核心线程数。根据正常情况下每秒的任务数量，单个任务消耗时间来确定。若正常情况下每秒600个请求，平均每个请求耗时20ms，那么需要设置为12，同时还要考虑线程因为其他任务被占用或因为异常导致线程停滞，还有业务主要是CPU密集还是IO密集，避免增加过多线程引起上下文切换开销大于业务开销。
- **maximumPoolSize**: 当任务数量超过队列长度后，允许开启的最大线程数。需要注意的是若不存在空闲时间来让线程消亡，会一直保持当前的线程数量处理消息。即 corePoolSize <= 实际线程数 <= maximumPoolSize
- **keepAliveTime**: worker 获取task时，最大等待的时间。 即当线程处理完成当前任务，从任务队列中获取下一个任务时，最大允许队列为空的时间。
- **workQueue**: 任务队列。这里需要关注的是队列的长度。需要考虑自身业务是否允许消息延时处理？最大允许多久的延时？若可接受5s的延时，平均每个请求处理时间为20ms，核心线程数为4，则5s内允许积压1000条请求。若队列长度设置为1000 ，当请求数量积压超过1000时， 会增加不超过最大线程数的线程处理，若 maximumPoolSize 为20，假设此时处理请求线程数为最大20，则允许积压5000条消息。所以需要根据业务突增来确定
- **allowCoreThreadTimeOut** : 允许核心线程超时。请求量不大可以考虑设置为true，一直有消息处理的情况下设置true也没啥用。





*如果觉得本文对你有所帮助，欢迎点击右上角GitHub图标给个Star呗~*