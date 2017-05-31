import MySQLdb

from random import choice, randint, random, shuffle
from time import localtime, strftime, time


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

        # prepare data for future mocking
        cursor = self.connect.cursor()

        cursor.execute("SELECT student_id FROM Student")
        self.student_ids = cursor.fetchall()

        cursor.execute("SELECT teacher_id FROM Teacher")
        self.teachser_ids = cursor.fetchall()

        cursor.execute("SELECT open_course_id FROM OpenCourse")
        self.open_course_ids = cursor.fetchall()

        cursor.execute("SELECT courseware_id FROM Courseware WHERE courseware_id IN (SELECT video_id FROM Video)")
        self.video_ids = set(cursor.fetchall())

        cursor.execute("SELECT courseware_id FROM Courseware WHERE courseware_id IN (SELECT document_id FROM Document)")
        self.document_ids = set(cursor.fetchall())

        cursor.execute("SELECT courseware_id FROM Courseware WHERE courseware_id IN (SELECT homework_id FROM Homework)")
        self.homework_ids = set(cursor.fetchall())

        cursor.execute("SELECT file_id FROM File")
        self.file_ids = set(cursor.fetchall())

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
        cursor = self.connect.cursor()
        user_id = choice(self.student_ids)[0]
        start_time = time()

        # login and get basic information
        cursor.execute("SELECT * FROM User JOIN File ON User.avatar_id = File.file_id WHERE user_id = %s;", (user_id,))
        cursor.fetchone()

        # get profile
        cursor.execute("SELECT * FROM Student WHERE student_id = %s;", (user_id,))
        cursor.fetchone()

        # get open course list that the student participates in
        cursor.execute("""SELECT *
                          FROM OpenCourse
                          WHERE open_course_id IN (SELECT open_course_id
                                                   FROM StudentCourse
                                                   WHERE student_id = %s );""", (user_id,))
        cursor.fetchall()

        # time it
        self.student_login_timer += time() - start_time

    def sim_view_open_course(self):
        cursor = self.connect.cursor()
        open_course_id = choice(self.open_course_ids)[0]
        start_time = time()

        # get chapters
        cursor.execute("SELECT * FROM Chapter WHERE open_course_id = %s;", (open_course_id,))
        for chapter in cursor.fetchall():
            chapter_id = chapter[0]
            cursor.execute("SELECT * FROM Section WHERE chapter_id = %s;", (chapter_id,))
            for section in cursor.fetchall():
                section_id = section[0]
                cursor.execute("SELECT * FROM Courseware WHERE section_id = %s;", (section_id,))
                for courseware in cursor.fetchall():
                    courseware_id = courseware[0]
                    if courseware_id in self.video_ids:
                        cursor.execute("SELECT * FROM Video WHERE video_id = %s;", (courseware_id,))
                        cursor.fetchone()
                    elif courseware_id in self.document_ids:
                        cursor.execute("SELECT * FROM Document WHERE document_id = coursewareID;", (courseware_id,))
                        cursor.fetchone()
                    elif courseware_id in self.homework_ids:
                        cursor.execute("SELECT * FROM Homework WHERE homework_id = coursewareID;", (courseware_id,))
                        cursor.fetchone()

        # time it
        self.view_open_course_timer += time() - start_time

    def sim_view_courseware(self):
        cursor = self.connect.cursor()
        student_id = choice(self.student_ids)[0]
        view_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

        # randomly choose a courseware to view
        cursor.execute("""SELECT courseware_id
                          FROM Courseware
                          WHERE section_id IN (SELECT section_id
                                               FROM Section
                                               WHERE chapter_id IN (SELECT chapter_id
                                                                    FROM Chapter
                                                                    WHERE open_course_id IN (SELECT open_course_id
                                                                                             FROM StudentCourse
                                                                                             WHERE student_id = %s)))""",
                       (student_id,))
        courseware_id = choice(cursor.fetchall())[0]

        start_time = time()
        if courseware_id in self.video_ids:
            # get info
            cursor.execute(
                "SELECT * FROM Video JOIN File ON Video.file_id = File.file_id WHERE Video.video_id = %s;",
                (courseware_id,))
            cursor.fetchone()

            # update record if study record exits, or add study record then update
            cursor.execute("SELECT vsr_id FROM VideoStudyRecord WHERE student_id = %s AND video_id = %s",
                           (student_id, courseware_id))
            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute("""INSERT INTO VideoStudyRecord (video_id, student_id, recent_position, front_position, has_finished, is_downloaded)
                                  VALUES (%s, %s, %s, %s, %s, %s)""", (courseware_id, student_id, 0, 0, 0, 0))
                cursor.execute("SELECT last_insert_id();")
                video_study_record_id = cursor.fetchone()[0]
                cursor.execute(
                    "CALL addVideoStudyRecordItem(%s, %s, %s, %s, %s, %new_item_id)",
                    (video_study_record_id, view_time, view_time, 0, randint(1, 50)))
            else:
                video_study_record_id = rows[0][0]
                cursor.execute(
                    "CALL addVideoStudyRecordItem(%s, %s, %s, %s, %s, %new_item_id)",
                    (video_study_record_id, view_time, view_time, 0, randint(1, 50)))

        elif courseware_id in self.document_ids:
            cursor.execute(
                "SELECT * FROM Document JOIN File ON Document.file_id = File.file_id WHERE Document.document_id = %s;",
                (courseware_id,))
            cursor.fetchone()

            # update record if study record exits, or add study record then update
            cursor.execute("SELECT dsr_id FROM DocumentStudyRecord WHERE student_id = %s AND video_id = %s",
                           (student_id, courseware_id))
            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute("""INSERT INTO DocumentStudyRecord (document_id, student_id, recent_page, front_page, has_finished, is_downloaded) 
                                  VALUES (%s, %s, %s, %s, %s, %s)""", (courseware_id, student_id, 0, 0, 0, 0))
                cursor.execute("SELECT last_insert_id();")
                document_study_record_id = cursor.fetchone()[0]
                cursor.execute(
                    "CALL addDocumentStudyRecordItem(%s, %s, %s, %s, %s, %new_item_id)",
                    (document_study_record_id, view_time, view_time, 0, randint(1, 50)))
            else:
                document_study_record_id = rows[0][0]
                cursor.execute(
                    "CALL addDocumentStudyRecordItem(%s, %s, %s, %s, %s, %new_item_id)",
                    (document_study_record_id, view_time, view_time, 0, randint(1, 50)))

        elif courseware_id in self.homework_ids:
            cursor.execute(
                "SELECT * FROM Homework JOIN Problem ON Homework.homework_id = Problem.homework_id WHERE Homework.homework_id = %s;",
                (courseware_id,))
            cursor.fetchall()

            # update record if study record exits, or add study record then update
            cursor.execute("SELECT hsr_id FROM HomeworkSubmitRecord WHERE student_id = %s AND video_id = %s",
                           (student_id, courseware_id))
            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute("""INSERT INTO HomeworkSubmitRecord (homework_id, student_id, is_submitted, score)
                                  VALUES (%s, %s, %s, %s)""", (courseware_id, student_id, 0, 0))
                cursor.execute("SELECT last_insert_id();")
                homework_submit_record_id = cursor.fetchone()[0]
                cursor.execute("""INSERT INTO HomeworkSubmitRecordItem (hsr_id, enter_time, leave_time) 
                                  VALUES (%s, %s, %s)""", (homework_submit_record_id, view_time, view_time))
            else:
                homework_submit_record_id = cursor.fetchone()[0]
                cursor.execute("""INSERT INTO HomeworkSubmitRecordItem (hsr_id, enter_time, leave_time) 
                                  VALUES (%s, %s, %s)""", (homework_submit_record_id, view_time, view_time))

        # time it
        self.view_courseware_timer += time() - start_time

    def sim_teacher_login(self):
        cursor = self.connect.cursor()
        user_id = choice(self.teachser_ids)[0]
        start_time = time()

        # login and get basic information
        cursor.execute("SELECT * FROM User JOIN File ON User.avatar_id = File.file_id WHERE user_id = %s;", (user_id,))
        cursor.fetchone()

        # get profile
        cursor.execute("SELECT * FROM Teacher WHERE teacher_id = %s;", (user_id,))
        cursor.fetchone()

        # get open course list that the student participates in
        cursor.execute("""SELECT * FROM OpenCourse WHERE teacher_id = %s;);""", (user_id,))
        open_courses = cursor.fetchall()

        # time it
        self.student_login_timer += time() - start_time

        # operation for each open course
        for open_course in open_courses:
            open_course_id = open_course[0]
            # randomly choose a section to update courseware
            cursor.execute("""SELECT section_id
                              FROM Section
                              WHERE chapter_id IN (SELECT chapter_id
                                                   FROM Chapter
                                                   WHERE open_course_id = %s))""", (open_course_id))
            section_id = choice(cursor.fetchall())[0]
            file_id = choice(self.file_ids)
            homework_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            rand = random
            start_time = time()
            if rand < 1 / 3:
                cursor.execute(
                    "CALL addDocument(%s, %s, %s, %s, %s, %s, %new_document_id)",
                    (section_id, 0, "NMB,QNMB", file_id, randint(20, 70), 0))
            elif rand < 2 / 3:
                cursor.execute(
                    "CALL addVideo(%s, %s, %s, %s, %s, %s, %new_video_id)",
                    (section_id, 0, "NMB,QNMB", file_id, randint(60, 1800), 0))
            else:
                cursor.execute(
                    "CALL addHomework(%s, %s, %s, %s, %s, %s, %s, %s, %new_homework_id)",
                    (section_id, 0, "NMB,QNMB", homework_time, homework_time, randint(0, 3), randint(2, 3),
                     randint(60, 21600)))

            # time it
            self.update_courseware_timer += time() - start_time

        # def sim_update_courseware(self):
        #     start_time = time()
        #     print "update courseware"
        #     self.update_courseware_timer += time() - start_time

        def sim_view_learning_process(self):
            # todo!
            start_time = time()
            print "view learning process"
            self.view_learning_process_timer += time() - start_time

    def main():
        sim = simulator(host="localhost", user="db_course", passwd="0000", db="SimpleMOOC", week_num=52)
        sim.run()

    if __name__ == '__main__':
        main()
