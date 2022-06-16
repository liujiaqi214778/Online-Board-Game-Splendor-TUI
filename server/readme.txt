groups:
    一个group为一个棋局，当棋局内的所有人都ready并且人数符合开局要求则游戏开始
    Group对象会创建一个线程开始棋局，并给所有当前棋局内的玩家发送主动消息，玩家的client会响应消息并根据此消息初始化Game/棋盘信息并展示


async server:
    以下是对生成器(generator), 协程(coroutine), 异步io(asyncio)的介绍

    执行实体: 某个运行过程的抽象
    上下文(context): 执行实体的上下文信息即此刻 CPU 寄存器信息
    调度器: 基于某种调度策略切换执行实体，需要保存/恢复执行实体上下文
    异步(asynchronous): 执行实体的快慢先后是不确定的，不等任务执行完直接执行下一个任务
    函数调用栈(call stack): 函数的调用是FILO的, 函数调用发生时将pc寄存器的值改为新函数首地址(在代码段)
        函数中的临时变量放在栈顶,修改栈寄存器rsp,rbp的值,代表当前栈帧(栈顶)的地址.
        函数执行过程中通过rbp的相对地址访问临时变量
        函数调用完成出栈:
            将pc修改为调用前的值(函数返回地址,此值也保存在栈中)
            恢复rbp,rsp为调用前的值(同样保存在栈中)
        继续上一个函数的执行
    进程拥有独立的虚拟地址空间,内部可以有多个线程共享此地址空间
    线程有独立的函数栈, 线程的切换将当前context或者context地址存入线程控制块TCB,调度器选择一个就绪线程,根据它的TCB恢复context(写入CPU)


    生成器(generator):
        当一个函数内部有yield关键字时，python解释器会特殊处理，调用此"函数"会返回一个生成器对象(并不会执行函数)
        def gen():
            n = 1
            yield n
            n += 1

        g = gen()  # g是一个生成器
        生成器同时也是一个迭代器(iterator)
        可迭代对象(iterable): 实现了__iter__方法, iter(iterable)返回一个iterator
        迭代器(iterator): 用于遍历iterable, 实现了__next__方法, next(iterator)返回iterable的一个元素, 建议实现__iter__返回迭代器自身
        for item in iterable:  # 隐含操作: iter(iterable), next(iterator)
            pass

        a = next(g)  # a == 1, 得到的是yield出来的n
        for i in g:
            print(i)

        生成器利用了保存/恢复上下文的机制, yield时函数中断, 抛出n, 下一次next(g)恢复现场从yield处继续执行到下一个yield


    协程(coroutine):
    https://docs.python.org/zh-cn/3/library/asyncio.html
        逻辑模型:
            协程和线程(thread)本质都是一个执行实体, 通过调度器切换执行实体可实现并发(concurrent)
            一个线程包含一或多个协程，协程的切换比线程更快，占用资源更少，协程只在用户空间，操作系统不知道协程
            用多线程也可以从逻辑上做到多协程的效果(实现并发、异步任务)
            如果协程仅仅是比线程切换速度快,为什么不把协程叫做轻量线程呢？
            协程与线程的根本区别:
                线程是抢占式的而协程需要主动释放CPU
                即根本区别是调度器的不同，线程调度器面对的执行实体可能各自为政，需要抢占式调度策略，需要更复杂的同步互斥机制
                一个线程内的不同协程的开发者来自同一个团体,为同一个目标互相协作
            协程与异步IO适用于IO密集型任务,执行实体主要处于阻塞/等待状态,协程相比多线程提高了时空效率

        物理模型/协程的实现 python example:
            分为stack/stackless 有栈/无栈协程，区别在于是否有自己的调用栈来进行函数调用等操作.
            stackless: 1. 栈帧内保存的不是状态而是指向状态的指针. 2. 所有帧的状态保存在堆上. 不做详细介绍
            https://zhuanlan.zhihu.com/p/33739573
            c++ 20 coroutine:
                https://en.cppreference.com/w/cpp/language/coroutines

        协程的使用:
            生成器和协程底层机制一样，作用不同，以下是基于生成器的协程:
            https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio-generator-based-coro
                @asyncio.coroutine
                def old_style_coroutine():
                    yield from asyncio.sleep(1)

            async/await 语法:
                https://docs.python.org/zh-cn/3/library/asyncio-task.html#id2
                async def func():
                    pass

                import asyncio
                async def main():
                    coobject = func()  # 返回一个coroutine对象
                    taskobject = asyncio.create_task(coobject)  # coroutine对象 -> Task并注册进当前线程的协程调度器
                    # 调度器调度的是Task
                    await coobject  # 先将coobject -> 注册Task, 并让出执行权,调度器自动选择一个就绪task执行
                    await taskobject  # 直接await一个task对象
                    # await后只能接coroutine或task对象

                asyncio.run(main())  # 参数必须是一个coroutine对象
                # 不要使用使线程阻塞的函数(所有协程都被阻塞)
                # 比如将 time.sleep(3) 改成 await asyncio.sleep(3)



