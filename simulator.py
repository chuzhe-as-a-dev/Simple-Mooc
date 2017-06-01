import MySQLdb

from random import choice, randint, random, sample, shuffle
from time import localtime, strftime, time

TEACHER_VIEW_PER_WEEK = 1
STUDENT_VIEW_PER_WEEK = 5
STUDENT_PROGRESS_PER_TEACHER_VIEW = 2
STUDENT_COURSEWARE_VIEW_PER_OPEN_COURSE_VIEW = 2


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

        self.student_login_count = 0
        self.view_open_course_count = 0
        self.view_courseware_count = 0
        self.teacher_login_count = 0
        self.update_courseware_count = 0
        self.view_learning_process_count = 0

        # prepare data for future mocking
        cursor = self.connect.cursor()

        # cursor.execute("SELECT student_id FROM Student")
        # self.student_ids = cursor.fetchall()

        cursor.execute("SELECT username, email FROM User WHERE user_id IN (SELECT student_id FROM Student)")
        self.student_usernames = []
        self.student_emails = []
        for row in cursor.fetchall():
            self.student_usernames.append(row[0])
            self.student_emails.append(row[1])

        # cursor.execute("SELECT teacher_id FROM Teacher")
        # self.teacher_ids = cursor.fetchall()

        cursor.execute("SELECT username, email FROM User WHERE user_id IN (SELECT teacher_id FROM Teacher)")
        self.teacher_usernames = []
        self.teacher_emails = []
        for row in cursor.fetchall():
            self.teacher_usernames.append(row[0])
            self.teacher_emails.append(row[1])

        cursor.execute("SELECT open_course_id FROM OpenCourse")
        self.open_course_ids = cursor.fetchall()

        cursor.execute("SELECT file_id FROM File")
        self.file_ids = cursor.fetchall()

    def run(self):
        # add tasks
        todos = []
        for week_index in xrange(self.week_num):
            todos += [self.sim_student_login] * STUDENT_VIEW_PER_WEEK * 14
            todos += [self.sim_teacher_login] * TEACHER_VIEW_PER_WEEK * 1

        # randomly execute all tasks
        shuffle(todos)
        for todo in todos:
            todo()

        # show result
        print "student_login_per_1000_times: %.6fs" % (self.student_login_timer / self.student_login_count * 1000)
        print "view_open_course_per_1000_times: %.6fs" % (
            self.view_open_course_timer / self.view_open_course_count * 1000)
        print "view_courseware_per_1000_times: %.6fs" % (self.view_courseware_timer / self.view_courseware_count * 1000)
        print "teacher_login_per_1000_times: %.6fs" % (self.teacher_login_timer / self.teacher_login_count * 1000)
        print "update_courseware_per_1000_times: %.6fs" % (
            self.update_courseware_timer / self.update_courseware_count * 1000)
        print "view_learning_process_per_1000_times: %.6fs" % (
            self.view_learning_process_timer / self.view_learning_process_count * 1000)

    def sim_view_courseware(self, student_id, courseware_id, courseware_type):
        self.view_courseware_count += 1

        cursor = self.connect.cursor()
        view_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

        start_time = time()
        if courseware_type == 1:
            # get info
            cursor.execute(
                "SELECT * FROM Video LEFT JOIN File ON Video.file_id = File.file_id WHERE Video.video_id = %s;",
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
                cursor.callproc("addVideoStudyRecordItem",
                                (video_study_record_id, view_time, view_time, 0, randint(1, 50), 0))
            else:
                video_study_record_id = rows[0][0]
                cursor.callproc("addVideoStudyRecordItem",
                                (video_study_record_id, view_time, view_time, 0, randint(1, 50), 0))

        elif courseware_type == 2:
            cursor.execute(
                "SELECT * FROM Document LEFT JOIN File ON Document.file_id = File.file_id WHERE Document.document_id = %s;",
                (courseware_id,))
            cursor.fetchone()

            # update record if study record exits, or add study record then update
            cursor.execute("SELECT dsr_id FROM DocumentStudyRecord WHERE student_id = %s AND document_id = %s",
                           (student_id, courseware_id))
            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute("""INSERT INTO DocumentStudyRecord (document_id, student_id, recent_page, front_page, has_finished, is_downloaded) 
                                  VALUES (%s, %s, %s, %s, %s, %s)""", (courseware_id, student_id, 0, 0, 0, 0))
                cursor.execute("SELECT last_insert_id();")
                document_study_record_id = cursor.fetchone()[0]
                cursor.callproc("addDocumentStudyRecordItem",
                                (document_study_record_id, view_time, view_time, 0, randint(1, 50), 0))
            else:
                document_study_record_id = rows[0][0]
                cursor.callproc("addDocumentStudyRecordItem",
                                (document_study_record_id, view_time, view_time, 0, randint(1, 50), 0))

        elif courseware_type == 3:
            cursor.execute(
                "SELECT * FROM Homework LEFT JOIN Problem ON Homework.homework_id = Problem.homework_id WHERE Homework.homework_id = %s;",
                (courseware_id,))
            cursor.fetchall()

            # update record if study record exits, or add study record then update
            cursor.execute("SELECT hsr_id FROM HomeworkSubmitRecord WHERE student_id = %s AND homework_id = %s",
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
                homework_submit_record_id = rows[0][0]
                cursor.execute("""INSERT INTO HomeworkSubmitRecordItem (hsr_id, enter_time, leave_time) 
                                  VALUES (%s, %s, %s)""", (homework_submit_record_id, view_time, view_time))
        else:
            print "error occurred in courseware type!", courseware_type, type(courseware_type)

        # time it
        cursor.close()
        self.connect.commit()
        self.view_courseware_timer += time() - start_time

    def sim_view_open_course(self, open_course_id, student_id):
        self.view_open_course_count += 1

        cursor = self.connect.cursor()
        start_time = time()
        coursewares = []

        # get chapters
        cursor.execute("SELECT * FROM Chapter WHERE open_course_id = %s;", (open_course_id,))
        for chapter in cursor.fetchall():
            chapter_id = chapter[0]
            cursor.execute("SELECT * FROM Section WHERE chapter_id = %s;", (chapter_id,))
            for section in cursor.fetchall():
                section_id = section[0]
                cursor.execute("SELECT courseware_id, courseware_type FROM Courseware WHERE section_id = %s;",
                               (section_id,))
                for row in cursor.fetchall():
                    coursewares.append(row)
                    courseware_id = row[0]
                    courseware_type = row[1]
                    if courseware_type == 1:
                        cursor.execute("SELECT * FROM Video WHERE video_id = %s;", (courseware_id,))
                        cursor.fetchone()
                    elif courseware_type == 2:
                        cursor.execute("SELECT * FROM Document WHERE document_id = %s;", (courseware_id,))
                        cursor.fetchone()
                    elif courseware_type == 3:
                        cursor.execute("SELECT * FROM Homework WHERE homework_id = %s;", (courseware_id,))
                        cursor.fetchone()
                    else:
                        print "courseware typr occurred here~", courseware_type, type(courseware_type), section_id

        # time it
        cursor.close()
        self.view_open_course_timer += time() - start_time

        # view courseware
        if len(coursewares) >= STUDENT_COURSEWARE_VIEW_PER_OPEN_COURSE_VIEW:
            for row in sample(coursewares, STUDENT_COURSEWARE_VIEW_PER_OPEN_COURSE_VIEW):
                courseware_id = row[0]
                courseware_type = row[1]
                self.sim_view_courseware(student_id, courseware_id, courseware_type)

    def sim_student_login(self):
        self.student_login_count += 1

        cursor = self.connect.cursor()
        rand = random()
        if rand < 0.5:
            token = choice(self.student_usernames)
        else:
            token = choice(self.student_emails)
        start_time = time()

        # login and get basic information
        cursor.execute(
            "SELECT user_id FROM User LEFT JOIN File ON User.avatar_id = File.file_id WHERE username = %s OR email = %s;",
            (token, token))
        user_id = cursor.fetchone()[0]

        # get profile
        cursor.execute("SELECT * FROM Student WHERE student_id = %s;", (user_id,))
        cursor.fetchone()

        # get open course list that the student participates in
        cursor.execute("SELECT open_course_id FROM StudentCourse WHERE student_id = %s;", (user_id,))
        rows = cursor.fetchall()

        # time it
        cursor.close()
        self.student_login_timer += time() - start_time

        if len(rows) > 1:
            row = choice(rows)
            open_course_id = row[0]
            self.sim_view_open_course(open_course_id, user_id)

    def sim_update_courseware(self, open_course_id):
        self.update_courseware_count += 1

        # randomly choose a section to update courseware
        cursor = self.connect.cursor()
        cursor.execute("""SELECT section_id
                          FROM Section
                          WHERE chapter_id IN (SELECT chapter_id
                                               FROM Chapter
                                               WHERE open_course_id = %s)""" % (open_course_id,))
        rows = cursor.fetchall()
        if len(rows) > 1:
            section_id = choice(rows)[0]
            file_id = choice(self.file_ids)
            homework_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            rand = random()

            start_time = time()
            if rand < 1 / 3:
                cursor.callproc("addDocument", (section_id, 0, "NMB,QNMB", file_id, randint(20, 70), 0, 0))
            elif rand < 2 / 3:
                cursor.callproc("addVideo", (section_id, 0, "NMB,QNMB", file_id, randint(60, 1800), 0, 0))
            else:
                cursor.callproc("addHomework", (
                    section_id, 0, "NMB,QNMB", homework_time, homework_time, randint(0, 3), randint(2, 3),
                    randint(60, 21600), 0))

                # time it
            self.connect.commit()
            self.update_courseware_timer += time() - start_time

    def sim_view_learning_progress(self, open_course_id):
        self.view_learning_process_count += 1

        cursor = self.connect.cursor()

        start_time = time()
        cursor.execute("""SELECT section_id
                          FROM Section
                          WHERE chapter_id IN (SELECT chapter_id
                                               FROM Chapter
                                               WHERE open_course_id = %s)""", (open_course_id,))
        # view overall progress of each section
        for row in cursor.fetchall():
            section_id = row[0]
            cursor.execute("""SELECT *
                              FROM VideoStudyRecord
                              WHERE video_id IN (SELECT courseware_id
                                                 FROM Courseware
                                                 WHERE section_id = %s);""", (section_id,))
            # cursor.execute("""SELECT *
            #                               FROM VideoStudyRecord
            #                               WHERE video_id IN (SELECT courseware_id
            #                                                  FROM Courseware
            #                                                  WHERE section_id = %s AND courseware_type = 1);""", (section_id,))
            cursor.fetchall()
            cursor.execute("""SELECT *
                              FROM DocumentStudyRecord
                              WHERE document_id IN (SELECT courseware_id
                                                FROM Courseware
                                                WHERE section_id = %s);""", (section_id,))
            # cursor.execute("""SELECT *
            #                               FROM DocumentStudyRecord
            #                               WHERE document_id IN (SELECT courseware_id
            #                                                 FROM Courseware
            #                                                 WHERE section_id = %s AND courseware_type = 2);""", (section_id,))
            cursor.fetchall()
            cursor.execute("""SELECT *
                              FROM HomeworkSubmitRecord
                              WHERE homework_id IN (SELECT courseware_id
                                                    FROM Courseware
                                                    WHERE section_id = %s);""", (section_id,))
            # cursor.execute("""SELECT *
            #                               FROM HomeworkSubmitRecord
            #                               WHERE homework_id IN (SELECT courseware_id
            #                                                     FROM Courseware
            #                                                     WHERE section_id = %s AND courseware_type = 3);""", (section_id,))
            cursor.fetchall()

        # time it
        cursor.close()
        self.view_learning_process_timer += time() - start_time

        # randomly pick a few student to view specific progress
        # cursor.execute("SELECT student_id FROM StudentCourse WHERE open_course_id = %s;", (open_course_id))
        # for row in sample(cursor.fetchall(), STUDENT_PROGRESS_PER_TEACHER_VIEW):
        #     student_id = row[0]
        #     cursor.execute("""SELECT courseware_id, courseware_type
        #                       FROM Courseware
        #                       WHERE section_id IN (SELECT section_id
        #                                            FROM Section
        #                                            WHERE chapter_id IN (SELECT chapter_id
        #                                                                 FROM OpenCourse
        #                                                                 WHERE open_course_id = %s))""",
        #                    (open_course_id))

    def sim_teacher_login(self):
        self.teacher_login_count += 1

        cursor = self.connect.cursor()
        rand = random()
        if rand < 0.5:
            token = choice(self.teacher_usernames)
        else:
            token = choice(self.teacher_emails)
        start_time = time()

        # login and get basic information
        cursor.execute(
            "SELECT user_id FROM User LEFT JOIN File ON User.avatar_id = File.file_id WHERE username = %s OR email = %s;",
            (token, token))
        user_id = cursor.fetchone()[0]

        # get profile
        cursor.execute("SELECT * FROM Teacher WHERE teacher_id = %s;", (user_id,))
        cursor.fetchone()

        # get open course list that the student participates in
        cursor.execute("""SELECT * FROM OpenCourse WHERE teacher_id = %s;""", (user_id,))
        open_courses = cursor.fetchall()

        # time it
        self.teacher_login_timer += time() - start_time

        # operation for each open course
        for open_course in open_courses:
            open_course_id = open_course[0]
            self.sim_update_courseware(open_course_id)
            self.sim_view_learning_progress(open_course_id)


def main():
    sim = simulator(host="localhost", user="db_course", passwd="0000", db="SimpleMOOC", week_num=52)
    sim.run()


if __name__ == '__main__':
    main()
