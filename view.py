import psycopg2
import config

def users_view():
    db = psycopg2.connect(
    database = config.PSQL_DB_NAME,
    user = config.PSQL_USERNAME, 
    password = config.PSQL_PASSWORD, 
    host = config.PSQL_HOST, 
    port = config.PSQL_PORT)
    cur = db.cursor()
    cur.execute("SELECT firstname,lastname,email,register,user_roles,to_char(create_at, 'MonthD, YYYY at HH12:MI AM') FROM lms_users WHERE user_roles != 'A';" )
    all_users = cur.fetchall()
    users_list = []
    for user in all_users:
        firstname,lastname,email,register,user_roles,create_at = user
        firstname = firstname.replace(' ','')
        lastname = lastname.replace(' ','')
        if register:
            register = 'Registered'
        else:
            register = 'Not Register'

        if user_roles == 'T':
            user_roles = user_roles.replace('T','Teacher')
        if user_roles == 'S':
            user_roles = user_roles.replace('S','Student')

        users_list.append({'firstname':firstname,'lastname':lastname,'email':email,'register':register,'create_at':create_at,'user_roles':user_roles})
    
    db.close()
    
    return users_list

def course_excerpt_view():
    db = psycopg2.connect(
    database = config.PSQL_DB_NAME,
    user = config.PSQL_USERNAME, 
    password = config.PSQL_PASSWORD, 
    host = config.PSQL_HOST, 
    port = config.PSQL_PORT)
    cur = db.cursor()
    cur.execute("SELECT * FROM lms_posts;" )
    lms_posts = cur.fetchall()
    # for course in courses:
    #     id , name = course
    #     print(str(id)+' : '+name)
    list_posts = []
    for post in lms_posts:
        id = post[0]
        author_id = post[1]
        cur.execute("SELECT to_char(post_date, 'MonthDD, YYYY at HH12:MI AM') FROM lms_posts WHERE id=%s;" % (id) )
        time = cur.fetchall()[0][0]
        cur.execute("SELECT FIRSTNAME,LASTNAME FROM lms_users WHERE id=%s;" % (author_id) )
        post_author = cur.fetchall()
        author_firstname = post_author[0][0].replace(' ','')
        author_lastname = post_author[0][1].replace(' ','')
        post_author = author_firstname + '  ' +author_lastname
        course_content = post[3]
        course_name = post[4]
        course_summary = post[5]
        img = post[6]
        dict_course = {'id':id, 'course_name':course_name, 'course_content':course_content, 'course_summary': course_summary, 'img':img, 'post_author': post_author, 'time':time}
        list_posts.append(dict_course)
    
    cur.execute("SELECT id FROM lms_posts;" )
    post_ids = cur.fetchall() 
    ids = []
    for id in post_ids:
        id = str(id[0])
        ids.append(id)

    db.close()
    result_list = [list_posts, ids]
    return result_list

def img_slider():
    
    db = psycopg2.connect(
    database = config.PSQL_DB_NAME,
    user = config.PSQL_USERNAME, 
    password = config.PSQL_PASSWORD, 
    host = config.PSQL_HOST, 
    port = config.PSQL_PORT)
    cur = db.cursor()
    cur.execute("SELECT  id,img_path FROM site_setting;" )
    path = cur.fetchall()

    # list_courses = []
    # for course in courses:
    #     id = course[0]
    #     course_name = course[1]
    #     img = course[2]
    #     dict_course = {'id':id, 'course_name':course_name, 'img':img}
    #     list_courses.append(dict_course)
    db.close()

    return path


# course_excerpt_view()