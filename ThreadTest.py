#!/usr/bin/env python
# coding:utf-8
import threading
from time import ctime, sleep

loops = [4, 2]


def loop(nloop, nsec, lock):
    print('start loop ', nloop, 'at:', ctime())
    sleep(nsec)
    print('loop', nloop, 'done at:', ctime())
    lock.release()


# def main():
#     print 'starting at: ', ctime()
#     locks = []
#     nloops = range(len(loops))
#
#     for i in nloops:
#         lock = thread.allocate_lock()
#         lock.acquire()
#         locks.append(lock)
#
#     for i in nloops:
#         thread.start_new_thread(loop, (i, loops[i], locks[i]))
#
#     for i in nloops:
#         while locks[i].locked(): pass
#         print 'all Done at:', ctime()


def loop2(nloop, nsec):
    print('start loop ', nloop, 'at:', ctime())
    sleep(nsec)
    print('loop', nloop, 'done at:', ctime())


def main2():
    print('start at:', ctime())
    threads = []
    nloops = range(len(loops))

    for i in nloops:
        t = threading.Thread(target=loop2, args=(i, loops[i]), name= '')
        threads.append(t)
        t.start()

    for i in nloops:
        threads[i].join()

    print('all_done at : ', ctime())


loops = (4,2)

def main3():
    print('start at:', ctime())
    threads = []
    nloops = range(len(loops))

    for i in nloops:
        # t = threading.Thread(target=loop2, args=(i, loops[i]))
        t = MyThread(loop2,(i,loops[i]),loop.__name__)
        threads.append(t)
        t.start()

    for i in nloops:
        threads[i].join()

    print('all_done at : ', ctime())


class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.args = args
        self.func = func

    def run(self):
        threadLock.acquire()
        self.func(*self.args)
        threadLock.release()

threadLock = threading.Lock()

if __name__ == '__main__':
    # main()
    # t = (1, 2)
    # print *t
    # print loop.__name__
    # main2()
    main3()