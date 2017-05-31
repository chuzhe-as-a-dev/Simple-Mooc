import MySQLdb

from random import shuffle
from time import time


class simulator:
    def __init__(self, host="localhost", user="db_course", passwd="0000", db="SimpleMOOC", week_num=52):
        self.week_num = week_num
        self.connect = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
        self.student_login_timer = 0.0
        self.view_open_course_timer = 0.0
        self.view_courseware_timer = 0.0
        self.teacher_login_timer = 0.0
        self.update_courseware_timer = 0.0
        self.view_learning_process_timer = 0.0

    def run(self):
        # add tasks
        day_num = 7
        todos = []
        for week_index in range(self.week_num):
            todos += [self.sim_student_login] * 5 * 50
            todos += [self.sim_view_open_course] * 5 * 50
            todos += [self.sim_view_courseware] * 5 * 2 * 50
            todos += [self.sim_teacher_login] * 1 * 2
            todos += [self.sim_update_courseware] * 1 * 2
            todos += [self.sim_view_learning_process] * 1 * 2

        # randomly execute all tasks
        shuffle(todos)
        for todo in todos:
            todo()

        # show result
        print "student_login_timer: %.3fs" % self.student_login_timer
        print "view_open_course_timer: %.3fs" % self.view_open_course_timer
        print "view_courseware_timer: %.3fs" % self.view_courseware_timer
        print "teacher_login_timer: %.3fs" % self.teacher_login_timer
        print "update_courseware_timer: %.3fs" % self.update_courseware_timer
        print "view_learning_process_timer: %.3fs" % self.view_learning_process_timer

    def sim_student_login(self):
        start_time = time()
        print "student login"
        self.student_login_timer += time() - start_time

    def sim_view_open_course(self):
        start_time = time()
        print "view open course"
        self.view_open_course_timer += time() - start_time

    def sim_view_courseware(self):
        start_time = time()
        print "view courseware"
        self.view_courseware_timer += time() - start_time

    def sim_teacher_login(self):
        start_time = time()
        print "teacher login"
        self.teacher_login_timer += time() - start_time

    def sim_update_courseware(self):
        start_time = time()
        print "update courseware"
        self.update_courseware_timer += time() - start_time

    def sim_view_learning_process(self):
        start_time = time()
        print "view learning process"
        self.view_learning_process_timer += time() - start_time


def main():
    sim = simulator(host="localhost", user="db_course", passwd="0000", db="SimpleMOOC", week_num=52)
    sim.run()


if __name__ == '__main__':
    main()
