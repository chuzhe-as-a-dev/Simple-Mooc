import random
import datetime
import time

codeRange = range(ord('a'), ord('z'))
alphaRange = [chr(x) for x in codeRange]
alphaMax = len(alphaRange)
schools = [chr(x) for x in codeRange]
departments = [chr(x) for x in codeRange]
category = [chr(x) for x in codeRange]
options = ['A', 'B', 'C', 'D', 'AB', 'AC', 'AD', 'BC', 'BD', 'CD', 'ABC', 'ABD', 'BCD', 'ABCD']

# parameters
courseCnt = 500
userCnt = 10000  # std:tea = 14:1
coursecategoryCnt = 20
opencourseCnt = courseCnt * 3  # active = 1000
studentcourseCnt = int(opencourseCnt * 50 / 3)
chapterCnt = opencourseCnt * 15
sectionCnt = chapterCnt * 4
coursewareCnt = sectionCnt * 3
fileCnt = int(userCnt * 0.2 + courseCnt + coursewareCnt * 0.7 * 0.7)
problemCnt = int(coursewareCnt / 3 * 4)
vsrCnt = int(coursewareCnt / 3 * 30)
dsrCnt = int(coursewareCnt / 3 * 30)
vsriCnt = vsrCnt * 2
dsriCnt = dsrCnt * 2
hsrCnt = int(coursewareCnt / 3 * 45)
hsriCnt = hsrCnt * 2
parCnt = int(coursewareCnt / 3 * 5 * 45)


# end parameters

def genRandomName(nameLength):
    global alphaRange, alphaMax
    length = random.randint(1, nameLength)
    name = ''
    for i in range(length):
        name += alphaRange[random.randint(0, alphaMax - 1)]
    return "\"" + name + "\""


def genRandomInt(length):
    return random.randint(1, length)


def genRandomIndex(myList):
    return "\"" + myList[random.randint(0, len(myList) - 1)] + "\""


def genUniqueStr(length, mySet):
    myStr = genRandomName(length)
    while myStr in mySet:
        myStr = genRandomName(length)
    mySet.add(myStr)
    return myStr


def genRandomSetMember(mySet):
    return mySet[random.randint(0, len(mySet) - 1)]


if __name__ == "__main__":
    fp = open("SimpleMooc_data.sql", 'w')
    fp.write("begin;\n")

    print("---user---")
    emails = set()
    usernames = set()
    # used by opencourse
    teachers = []
    # used by studentcourse
    students = []

    for i in range(1, userCnt + 1):
        email = genUniqueStr(16, emails)
        username = genUniqueStr(8, usernames)
        nickname = genRandomName(8)
        sql = "insert into user (user_id,email,username,nickname) values("
        sql = sql + str(i) + "," + email + "," + username + "," + nickname + ");\n"
        fp.write(sql)

    print("---teacher,student,admin---")
    for i in range(1, userCnt + 1):
        # fixed ratio
        role = random.randint(1, 15)

        # admin
        # if role == 1:
        #   sql = "insert into admin (admin_id) values("
        #   sql = sql + str(i) + ");\n"

        # teacher
        if role == 1:
            teachers.append(i)
            name = genRandomName(8)
            university = genRandomIndex(schools)
            department = genRandomIndex(departments)
            sql = "insert into teacher (teacher_id,teacher_name,university,department) values("
            sql = sql + str(i) + "," + name + "," + university + "," + department + ");\n"

        # student
        else:
            students.append(i)
            sql = "insert into student (student_id) values("
            sql = sql + str(i) + ");\n"
        fp.write(sql)

    print("---course---")

    for i in range(1, courseCnt + 1):
        coursename = genRandomName(16)
        sql = "insert into course (course_id,course_name) values("
        sql = sql + str(i) + "," + coursename + ");\n"
        fp.write(sql)

    print("---category---")
    for i in range(len(category)):
        sql = "insert into category (category_id,category_name) values("
        sql = sql + str(i + 1) + ",\"" + category[i] + "\");\n"
        fp.write(sql)

    print("---coursecategory---")

    coursecategory = set()
    for i in range(coursecategoryCnt):
        # generate unique c_id c_id pairs
        category_id = genRandomInt(len(category))
        course_id = genRandomInt(courseCnt)
        while (category_id, course_id) in coursecategory:
            category_id = genRandomInt(len(category))
            course_id = genRandomInt(courseCnt)
        coursecategory.add((category_id, course_id))

        sql = "insert into coursecategory (category_id,course_id) values("
        sql = sql + str(category_id) + "," + str(course_id) + ");\n"
        fp.write(sql)

    print("---opencourse---")

    for i in range(1, opencourseCnt + 1):
        # fixed ratio
        registry = random.randint(1, 8)
        if registry > 1:    registry = 0
        course_id = genRandomInt(courseCnt)
        teacher_id = genRandomSetMember(teachers)
        sql = "insert into opencourse (open_course_id,course_id,teacher_id,allow_register) values("
        sql = sql + str(i) + "," + str(course_id) + "," + str(teacher_id) + "," + str(registry) + ");\n"
        fp.write(sql)

    print("---studentcourse---")

    studentcourse = set()
    for i in range(1, opencourseCnt + 1):
        open_course_id = genRandomInt(opencourseCnt)
        student_id = genRandomSetMember(students)
        while (student_id, open_course_id) in studentcourse:
            open_course_id = genRandomInt(opencourseCnt)
            student_id = genRandomSetMember(students)
        studentcourse.add((student_id, open_course_id))
        sql = "insert into studentcourse (open_course_id,student_id) values("
        sql = sql + str(open_course_id) + "," + str(student_id) + ");\n"
        fp.write(sql)

    print("---chapter---")

    chapter_orders = [0] * opencourseCnt
    for i in range(1, chapterCnt + 1):
        title = genRandomName(16)
        open_course_id = genRandomInt(opencourseCnt)
        display_order = chapter_orders[open_course_id - 1] = chapter_orders[open_course_id - 1] + 1
        sql = "insert into chapter (chapter_id,open_course_id,display_order,chapter_title) values("
        sql = sql + str(i) + "," + str(open_course_id) + "," + str(display_order) + "," + title + ");\n"
        fp.write(sql)
    # print(chapter_orders)

    print("---section---")

    section_orders = [0] * chapterCnt
    for i in range(1, sectionCnt + 1):
        title = genRandomName(16)
        chapter_id = genRandomInt(chapterCnt)
        display_order = section_orders[chapter_id - 1] = section_orders[chapter_id - 1] + 1
        sql = "insert into section (section_id, chapter_id, display_order,section_title) values("
        sql = sql + str(i) + "," + str(chapter_id) + "," + str(display_order) + "," + title + ");\n"
        fp.write(sql)
    # print(section_orders)

    print("---courseware---")

    courseware_orders = [0] * sectionCnt
    for i in range(1, coursewareCnt + 1):
        title = genRandomName(16)
        courseware_type = random.randint(1, 3)
        section_id = genRandomInt(sectionCnt)
        display_order = courseware_orders[section_id - 1] = courseware_orders[section_id - 1] + 1
        sql = "insert into courseware (courseware_id, section_id, display_order,courseware_type, courseware_title) values("
        sql = sql + str(i) + "," + str(section_id) + "," + str(display_order) + "," + str(
            courseware_type) + "," + title + ");\n"
        fp.write(sql)
        # print(courseware_orders)

    print("---file---")

    for i in range(1, fileCnt + 1):
        auth_key = genRandomName(16)
        path = genRandomName(16)
        sql = "insert into file (file_id,auth_key,path) values("
        sql = sql + str(i) + "," + auth_key + "," + path + ");\n"
        fp.write(sql)

    print("---video document homework---")
    videos = []
    documents = []
    homeworks = []
    for i in range(1, coursewareCnt + 1):
        filetype = random.randint(1, 3)
        # video
        if filetype == 1:
            file_id = genRandomInt(fileCnt)
            duration = random.randint(300, 3600)
            allow_download = random.randint(0, 1)
            sql = "insert into video (video_id, file_id,duration,allow_download) values("
            sql = sql + str(i) + "," + str(file_id) + "," + str(duration) + "," + str(allow_download) + ");\n"
            fp.write(sql)
            videos.append(i)
        # document
        elif filetype == 2:
            file_id = genRandomInt(fileCnt)
            page_count = genRandomInt(20)
            allow_download = random.randint(0, 1)
            sql = "insert into document (document_id, file_id,page_count,allow_download) values("
            sql = sql + str(i) + "," + str(file_id) + "," + str(page_count) + "," + str(allow_download) + ");\n"
            fp.write(sql)
            documents.append(i)
        # homework
        else:
            max_submit_times = genRandomInt(5)
            time_limit = random.randint(500, 3600)
            sql = "insert into homework (homework_id, max_submit_times,time_limit) values("
            sql = sql + str(i) + "," + str(max_submit_times) + "," + str(time_limit) + ");\n"
            fp.write(sql)
            homeworks.append(i)

    print("---problem---")

    problem_orders = [0] * coursewareCnt
    for i in range(1, problemCnt + 1):
        homework_id = genRandomSetMember(homeworks)
        display_order = problem_orders[homework_id - 1] = problem_orders[homework_id - 1] + 1
        problem_type = random.randint(0, 1)
        content = genRandomName(32)
        option = genRandomIndex(options)
        solution = genRandomName(32)
        points = genRandomInt(5)
        sql = "insert into problem (problem_id, homework_id, display_order, problem_type, content, options, solution, points) values("
        sql = sql + str(i) + "," + str(homework_id) + "," + str(display_order) + "," + str(
            problem_type) + "," + content + "," + option + "," + solution + "," + str(points) + ");\n"
        fp.write(sql)
    # print(problem_orders)

    print("---VideoStudyRecord---")
    videostudent = set()
    for i in range(1, vsrCnt + 1):
        video_id = genRandomSetMember(videos)
        student_id = genRandomSetMember(students)
        while (video_id, student_id) in videostudent:
            video_id = genRandomSetMember(videos)
            student_id = genRandomSetMember(students)
        videostudent.add((video_id, student_id))
        sql = "insert into videostudyrecord (vsr_id, video_id, student_id) values("
        sql = sql + str(i) + "," + str(video_id) + "," + str(student_id) + ");\n"
        fp.write(sql)

    print("---DocumentStudyRecord---")
    documentstudent = set()
    for i in range(1, dsrCnt + 1):
        document_id = genRandomSetMember(documents)
        student_id = genRandomSetMember(students)
        while (document_id, student_id) in documentstudent:
            document_id = genRandomSetMember(documents)
            student_id = genRandomSetMember(students)
        documentstudent.add((document_id, student_id))
        sql = "insert into documentstudyrecord (dsr_id, document_id, student_id) values("
        sql = sql + str(i) + "," + str(document_id) + "," + str(student_id) + ");\n"
        fp.write(sql)

    print("---VideoStudyRecordItem---")

    for i in range(1, vsriCnt + 1):
        vsr_id = genRandomInt(vsrCnt)
        start_position = genRandomInt(3600)
        end_position = max(start_position, genRandomInt(3600))
        sql = "insert into videostudyrecorditem (vsri_id, vsr_id, start_position, end_position) values("
        sql = sql + str(i) + "," + str(vsr_id) + "," + str(start_position) + "," + str(end_position) + ");\n"
        fp.write(sql)

    print("---DocumentStudyRecordItem---")

    for i in range(1, dsriCnt + 1):
        dsr_id = genRandomInt(dsrCnt)
        start_page = genRandomInt(20)
        end_page = max(start_page, genRandomInt(20))
        sql = "insert into documentstudyrecorditem (dsri_id, dsr_id, start_page, end_page) values("
        sql = sql + str(i) + "," + str(vsr_id) + "," + str(start_page) + "," + str(end_page) + ");\n"
        fp.write(sql)

    print("---HomeworkSubmitRecord---")

    for i in range(1, hsrCnt + 1):
        homework_id = genRandomSetMember(homeworks)
        student_id = genRandomSetMember(students)
        is_submitted = random.randint(0, 1)
        score = genRandomInt(100)
        sql = "insert into homeworksubmitrecord (hsr_id, homework_id, student_id, is_submitted, score) values("
        sql = sql + str(i) + "," + str(homework_id) + "," + str(student_id) + "," + str(is_submitted) + "," + str(
            score) + ");\n"
        fp.write(sql)

    print("---HomeworkSubmitRecordItem---")

    for i in range(1, hsriCnt + 1):
        hsr_id = genRandomInt(hsrCnt)
        sql = "insert into homeworksubmitrecorditem (hsri_id, hsr_id) values("
        sql = sql + str(i) + "," + str(hsr_id) + ");\n"
        fp.write(sql)

    print("---ProblemAnswerRecord---")

    studentproblem = set()
    for i in range(1, parCnt + 1):
        hsr_id = genRandomInt(hsrCnt)
        problem_id = genRandomInt(problemCnt)
        while (hsr_id, problem_id) in studentproblem:
            hsr_id = genRandomInt(hsrCnt)
            problem_id = genRandomInt(problemCnt)
        studentproblem.add((hsr_id, problem_id))
        answer = genRandomIndex(options)
        time_cost = random.randint(30, 3600)
        sql = "insert into problemanswerrecord (hsr_id, problem_id, answer, time_cost) values("
        sql = sql + str(hsr_id) + "," + str(problem_id) + "," + answer + "," + str(time_cost) + ");\n"
        fp.write(sql)

    fp.write("commit;\n")
    fp.close()
