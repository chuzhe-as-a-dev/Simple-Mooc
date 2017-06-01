def file_len(fname):
    i = 0
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

print file_len("/Users/tang/Documents/Courses/SE223 Dasabase/Simple-Mooc/SimpleMooc_data.sql")