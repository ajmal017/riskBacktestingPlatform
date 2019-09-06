# encoding: UTF-8
#创建一个被多个线程共享的 Queue 对象
from queue import Queue
from threading import Thread
import time
import path 
from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine
class Student(Thread):
    def __init__(self, name, queue):
        super(Student,self).__init__()
        self.name = name
        self.queue = queue

    def run(self):
        while True:
            # 阻塞程序，时刻监听老师，接收消息 监听回测程序
            msg = self.queue.get()
            # 一旦发现点到自己名字，就赶紧答到
            if msg == self.name:
                print(u"{}：到！".format(self.name))


class Teacher:
    # 运行回测程序，同时put时间数据
    def __init__(self, queue):
        self.queue=queue

    def call(self, student_name):
        print(u"老师：{}来了没？".format(student_name))
        # 发送消息，要点谁的名
        self.queue.put(student_name)

if __name__ == '__main__':
     queue = Queue()
     teacher = Teacher(queue=queue)
     s1 = Student(name=u"ming", queue=queue)
     s2 = Student(name=u"liang", queue=queue)
     s1.start()
     s2.start()

     print(u'开始点名~')
     teacher.call(u'ming')
     time.sleep(1)
     teacher.call(u'liang')