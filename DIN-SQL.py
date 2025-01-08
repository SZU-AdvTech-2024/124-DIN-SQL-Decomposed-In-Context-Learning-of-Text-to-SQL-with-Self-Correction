import pandas as pd
import time
import openai
import os
import sys


#----------------------------------------------------prompts-----------------------------------------------
schema_linking_prompt = '''Table advisor, columns = [*,s_ID,i_ID]
Table classroom, columns = [*,building,room_number,capacity]
Table course, columns = [*,course_id,title,dept_name,credits]
Table department, columns = [*,dept_name,building,budget]
Table instructor, columns = [*,ID,name,dept_name,salary]
Table prereq, columns = [*,course_id,prereq_id]
Table section, columns = [*,course_id,sec_id,semester,year,building,room_number,time_slot_id]
Table student, columns = [*,ID,name,dept_name,tot_cred]
Table takes, columns = [*,ID,course_id,sec_id,semester,year,grade]
Table teaches, columns = [*,ID,course_id,sec_id,semester,year]
Table time_slot, columns = [*,time_slot_id,day,start_hr,start_min,end_hr,end_min]
Foreign_keys = [course.dept_name = department.dept_name,instructor.dept_name = department.dept_name,section.building = classroom.building,section.room_number = classroom.room_number,section.course_id = course.course_id,teaches.ID = instructor.ID,teaches.course_id = section.course_id,teaches.sec_id = section.sec_id,teaches.semester = section.semester,teaches.year = section.year,student.dept_name = department.dept_name,takes.ID = student.ID,takes.course_id = section.course_id,takes.sec_id = section.sec_id,takes.semester = section.semester,takes.year = section.year,advisor.s_ID = student.ID,advisor.i_ID = instructor.ID,prereq.prereq_id = course.course_id,prereq.course_id = course.course_id]
Q: "Find the buildings which have rooms with capacity more than 50."
A: Let’s think step by step. In the question "Find the buildings which have rooms with capacity more than 50.", we are asked:
"the buildings which have rooms" so we need column = [classroom.capacity]
"rooms with capacity" so we need column = [classroom.building]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [50]. So the Schema_links are:
Schema_links: [classroom.building,classroom.capacity,50]

Table department, columns = [*,Department_ID,Name,Creation,Ranking,Budget_in_Billions,Num_Employees]
Table head, columns = [*,head_ID,name,born_state,age]
Table management, columns = [*,department_ID,head_ID,temporary_acting]
Foreign_keys = [management.head_ID = head.head_ID,management.department_ID = department.Department_ID]
Q: "How many heads of the departments are older than 56 ?"
A: Let’s think step by step. In the question "How many heads of the departments are older than 56 ?", we are asked:
"How many heads of the departments" so we need column = [head.*]
"older" so we need column = [head.age]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [56]. So the Schema_links are:
Schema_links: [head.*,head.age,56]

Table advisor, columns = [*,s_ID,i_ID]
Table classroom, columns = [*,building,room_number,capacity]
Table course, columns = [*,course_id,title,dept_name,credits]
Table department, columns = [*,dept_name,building,budget]
Table instructor, columns = [*,ID,name,dept_name,salary]
Table prereq, columns = [*,course_id,prereq_id]
Table section, columns = [*,course_id,sec_id,semester,year,building,room_number,time_slot_id]
Table student, columns = [*,ID,name,dept_name,tot_cred]
Table takes, columns = [*,ID,course_id,sec_id,semester,year,grade]
Table teaches, columns = [*,ID,course_id,sec_id,semester,year]
Table time_slot, columns = [*,time_slot_id,day,start_hr,start_min,end_hr,end_min]
Foreign_keys = [course.dept_name = department.dept_name,instructor.dept_name = department.dept_name,section.building = classroom.building,section.room_number = classroom.room_number,section.course_id = course.course_id,teaches.ID = instructor.ID,teaches.course_id = section.course_id,teaches.sec_id = section.sec_id,teaches.semester = section.semester,teaches.year = section.year,student.dept_name = department.dept_name,takes.ID = student.ID,takes.course_id = section.course_id,takes.sec_id = section.sec_id,takes.semester = section.semester,takes.year = section.year,advisor.s_ID = student.ID,advisor.i_ID = instructor.ID,prereq.prereq_id = course.course_id,prereq.course_id = course.course_id]
Q: "Find the id of instructors who taught a class in Fall 2009 but not in Spring 2010."
A: Let’s think step by step. In the question "Find the id of instructors who taught a class in Fall 2009 but not in Spring 2010.", we are asked:
"id of instructors who taught " so we need column = [teaches.id]
"taught a class in" so we need column = [teaches.semester,teaches.year]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Fall,2009,Spring,2010]. So the Schema_links are:
schema_links: [teaches.id,teaches.semester,teaches.year,Fall,2009,Spring,2010]

Table city, columns = [*,City_ID,Official_Name,Status,Area_km_2,Population,Census_Ranking]
Table competition_record, columns = [*,Competition_ID,Farm_ID,Rank]
Table farm, columns = [*,Farm_ID,Year,Total_Horses,Working_Horses,Total_Cattle,Oxen,Bulls,Cows,Pigs,Sheep_and_Goats]
Table farm_competition, columns = [*,Competition_ID,Year,Theme,Host_city_ID,Hosts]
Foreign_keys = [farm_competition.Host_city_ID = city.City_ID,competition_record.Farm_ID = farm.Farm_ID,competition_record.Competition_ID = farm_competition.Competition_ID]
Q: "Show the status shared by cities with population bigger than 1500 and smaller than 500."
A: Let’s think step by step. In the question "Show the status shared by cities with population bigger than 1500 and smaller than 500.", we are asked:
"the status shared by cities" so we need column = [city.Status]
"cities with population" so we need column = [city.Population]
Based on the columns and tables, we need these Foreign_keys = [].
Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [1500,500]. So the Schema_links are:
Schema_links: [city.Status,city.Population,1500,500]

'''
classification_prompt = '''Q: "Find the buildings which have rooms with capacity more than 50."
schema_links: [classroom.building,classroom.capacity,50]
A: Let’s think step by step. The SQL query for the question "Find the buildings which have rooms with capacity more than 50." needs these tables = [classroom], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we don't need JOIN and don't need nested queries, then the the SQL query can be classified as "EASY".
Label: "EASY"

Q: "What are the names of all instructors who advise students in the math depart sorted by total credits of the student."
schema_links: [advisor.i_id = instructor.id,advisor.s_id = student.id,instructor.name,student.dept_name,student.tot_cred,math]
A: Let’s think step by step. The SQL query for the question "What are the names of all instructors who advise students in the math depart sorted by total credits of the student." needs these tables = [advisor,instructor,student], so we need JOIN.
Plus, it doesn't need nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we need JOIN and don't need nested queries, then the the SQL query can be classified as "NON-NESTED".
Label: "NON-NESTED"

Q: "How many courses that do not have prerequisite?"
schema_links: [course.*,course.course_id = prereq.course_id]
A: Let’s think step by step. The SQL query for the question "How many courses that do not have prerequisite?" needs these tables = [course,prereq], so we need JOIN.
Plus, it requires nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = ["Which courses have prerequisite?"].
So, we need JOIN and need nested queries, then the the SQL query can be classified as "NESTED".
Label: "NESTED"

Q: "Find the title of course that is provided by both Statistics and Psychology departments."
schema_links: [course.title,course.dept_name,Statistics,Psychology]
A: Let’s think step by step. The SQL query for the question "Find the title of course that is provided by both Statistics and Psychology departments." needs these tables = [course], so we don't need JOIN.
Plus, it requires nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = ["Find the titles of courses that is provided by Psychology departments"].
So, we don't need JOIN and need nested queries, then the the SQL query can be classified as "NESTED".
Label: "NESTED"


Q: "Find the name of the department that offers the highest total credits?"
schema_links: [course.dept_name,course.credits]
A: Let’s think step by step. The SQL query for the question "Find the name of the department that offers the highest total credits?." needs these tables = [course], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we don't need JOIN and don't need nested queries, then the the SQL query can be classified as "EASY".
Label: "EASY"

Q: "What is the name of the instructor who advises the student with the greatest number of total credits?"
schema_links: [advisor.i_id = instructor.id,advisor.s_id = student.id,instructor.name,student.tot_cred ]
A: Let’s think step by step. The SQL query for the question "What is the name of the instructor who advises the student with the greatest number of total credits?" needs these tables = [advisor,instructor,student], so we need JOIN.
Plus, it doesn't need nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we need JOIN and don't need nested queries, then the the SQL query can be classified as "NON-NESTED".
Label: "NON-NESTED"

'''

easy_prompt = '''Q: "Find the buildings which have rooms with capacity more than 50."
Schema_links: [classroom.building,classroom.capacity,50]
SQL: SELECT DISTINCT building FROM classroom WHERE capacity  >  50

Q: "Find the room number of the rooms which can sit 50 to 100 students and their buildings."
Schema_links: [classroom.building,classroom.room_number,classroom.capacity,50,100]
SQL: SELECT building ,  room_number FROM classroom WHERE capacity BETWEEN 50 AND 100

Q: "Give the name of the student in the History department with the most credits."
Schema_links: [student.name,student.dept_name,student.tot_cred,History]
SQL: SELECT name FROM student WHERE dept_name  =  'History' ORDER BY tot_cred DESC LIMIT 1

Q: "Find the total budgets of the Marketing or Finance department."
Schema_links: [department.budget,department.dept_name,Marketing,Finance]
SQL: SELECT sum(budget) FROM department WHERE dept_name  =  'Marketing' OR dept_name  =  'Finance'

Q: "Find the department name of the instructor whose name contains 'Soisalon'."
Schema_links: [instructor.dept_name,instructor.name,Soisalon]
SQL: SELECT dept_name FROM instructor WHERE name LIKE '%Soisalon%'

Q: "What is the name of the department with the most credits?"
Schema_links: [course.dept_name,course.credits]
SQL: SELECT dept_name FROM course GROUP BY dept_name ORDER BY sum(credits) DESC LIMIT 1

Q: "How many instructors teach a course in the Spring of 2010?"
Schema_links: [teaches.ID,teaches.semester,teaches.YEAR,Spring,2010]
SQL: SELECT COUNT (DISTINCT ID) FROM teaches WHERE semester  =  'Spring' AND YEAR  =  2010

Q: "Find the title of the course that is offered by more than one department."
Schema_links: [course.title]
SQL: SELECT title FROM course GROUP BY title HAVING count(*)  >  1

'''
medium_prompt = '''Q: "Find the total budgets of the Marketing or Finance department."
Schema_links: [department.budget,department.dept_name,Marketing,Finance]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select sum(department.budget) from department  where  department.dept_name = \"Marketing\"  or  department.dept_name = \"Finance\"
SQL: SELECT sum(budget) FROM department WHERE dept_name  =  'Marketing' OR dept_name  =  'Finance'

Q: "Find the name and building of the department with the highest budget."
Schema_links: [department.budget,department.dept_name,department.building]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select department.dept_name , department.building from department  order by department.budget desc limit 1
SQL: SELECT dept_name ,  building FROM department ORDER BY budget DESC LIMIT 1

Q: "What is the name and building of the departments whose budget is more than the average budget?"
Schema_links: [department.budget,department.dept_name,department.building]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation:  select department.dept_name , department.building from department  where  @.@ > avg ( department.budget ) 
SQL: SELECT dept_name ,  building FROM department WHERE budget  >  (SELECT avg(budget) FROM department)

Q: "Find the total number of students and total number of instructors for each department."
Schema_links: [department.dept_name = student.dept_name,student.id,department.dept_name = instructor.dept_name,instructor.id]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = [department,student,instructor]. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: "select count( distinct student.ID) , count( distinct instructor.ID) , department.dept_name from department  group by instructor.dept_name
SQL: SELECT count(DISTINCT T2.id) ,  count(DISTINCT T3.id) ,  T3.dept_name FROM department AS T1 JOIN student AS T2 ON T1.dept_name  =  T2.dept_name JOIN instructor AS T3 ON T1.dept_name  =  T3.dept_name GROUP BY T3.dept_name

Q: "list in alphabetic order all course names and their instructors' names in year 2008."
Schema_links: [course.title,course.course_id = teaches.course_id,teaches.id = instructor.id,instructor.name,teaches.year,2008]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = [course,teaches,instructor]. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select course.title , instructor.name from course  where  teaches.year = 2008  order by course.title asc
SQL: SELECT T1.title ,  T3.name FROM course AS T1 JOIN teaches AS T2 ON T1.course_id  =  T2.course_id JOIN instructor AS T3 ON T2.id  =  T3.id WHERE T2.YEAR  =  2008 ORDER BY T1.title

'''
hard_prompt = '''Q: "Find the title of courses that have two prerequisites?"
Schema_links: [course.title,course.course_id = prereq.course_id]
A: Let's think step by step. "Find the title of courses that have two prerequisites?" can be solved by knowing the answer to the following sub-question "What are the titles for courses with two prerequisites?".
The SQL query for the sub-question "What are the titles for courses with two prerequisites?" is SELECT T1.title FROM course AS T1 JOIN prereq AS T2 ON T1.course_id  =  T2.course_id GROUP BY T2.course_id HAVING count(*)  =  2
So, the answer to the question "Find the title of courses that have two prerequisites?" is =
Intermediate_representation: select course.title from course  where  count ( prereq.* )  = 2  group by prereq.course_id
SQL: SELECT T1.title FROM course AS T1 JOIN prereq AS T2 ON T1.course_id  =  T2.course_id GROUP BY T2.course_id HAVING count(*)  =  2

Q: "Find the name and building of the department with the highest budget."
Schema_links: [department.dept_name,department.building,department.budget]
A: Let's think step by step. "Find the name and building of the department with the highest budget." can be solved by knowing the answer to the following sub-question "What is the department name and corresponding building for the department with the greatest budget?".
The SQL query for the sub-question "What is the department name and corresponding building for the department with the greatest budget?" is SELECT dept_name ,  building FROM department ORDER BY budget DESC LIMIT 1
So, the answer to the question "Find the name and building of the department with the highest budget." is =
Intermediate_representation: select department.dept_name , department.building from department  order by department.budget desc limit 1
SQL: SELECT dept_name ,  building FROM department ORDER BY budget DESC LIMIT 1

Q: "Find the salaries of all distinct instructors that are less than the largest salary."
Schema_links: [instructor.salary]
A: Let's think step by step. "Find the salaries of all distinct instructors that are less than the largest salary." can be solved by knowing the answer to the following sub-question "What is the largest salary of instructors".
The SQL query for the sub-question "What is the largest salary of instructors" is SELECT max(salary) FROM instructor
So, the answer to the question "Find the salaries of all distinct instructors that are less than the largest salary." is =
Intermediate_representation: select  distinct instructor.salary from instructor  where  @.@ < max ( instructor.salary )
SQL: SELECT DISTINCT salary FROM instructor WHERE salary  <  (SELECT max(salary) FROM instructor)

Q: "Find the names of students who have taken any course in the fall semester of year 2003."
Schema_links: [student.id,student.name,takes.id,takes.semester,fall,2003]
A: Let's think step by step. "Find the names of students who have taken any course in the fall semester of year 2003." can be solved by knowing the answer to the following sub-question "Find the students who have taken any course in the fall semester of year 2003.".
The SQL query for the sub-question "Find the students who have taken any course in the fall semester of year 2003." is SELECT id FROM takes WHERE semester  =  'Fall' AND YEAR  =  2003
So, the answer to the question "Find the names of students who have taken any course in the fall semester of year 2003." is =
Intermediate_representation: select student.name from student  where  takes.semester = \"Fall\"  and  takes.year = 2003
SQL: SELECT name FROM student WHERE id IN (SELECT id FROM takes WHERE semester  =  'Fall' AND YEAR  =  2003)

Q: "Give the title and credits for the course that is taught in the classroom with the greatest capacity."
Schema_links: [classroom.capacity,classroom.building = SECTION.building,classroom.room_number = SECTION.room_number,course.title,course.credits,course.course_id = SECTION.course_id]
A: Let's think step by step. "Give the title and credits for the course that is taught in the classroom with the greatest capacity." can be solved by knowing the answer to the following sub-question "What is the capacity of the largest room?".
The SQL query for the sub-question "What is the capacity of the largest room?" is (SELECT max(capacity) FROM classroom)
So, the answer to the question "Give the title and credits for the course that is taught in the classroom with the greatest capacity." is =
Intermediate_representation: select course.title , course.credits from classroom  order by classroom.capacity desc limit 1"
SQL: SELECT T3.title ,  T3.credits FROM classroom AS T1 JOIN SECTION AS T2 ON T1.building  =  T2.building AND T1.room_number  =  T2.room_number JOIN course AS T3 ON T2.course_id  =  T3.course_id WHERE T1.capacity  =  (SELECT max(capacity) FROM classroom)

'''
#----------------------------------------------------------------------------------------------------------

if sys.argv[1] == "--dataset" and sys.argv[3] == "--output":
    DATASET_SCHEMA = sys.argv[2]+"tables.json"
    DATASET = sys.argv[2]+"dev.json"
    OUTPUT_FILE = sys.argv[4]
else:
    raise Exception("Please use this format python CoT.py --dataset data/ --output predicted_sql.txt")

# API_KEY = #key
# os.environ["OPENAI_API_KEY"] = API_KEY
# openai.api_key = os.getenv("OPENAI_API_KEY")
# 设置 API 基础地址和密钥
openai.api_base = "https://api.wlai.vip/v1"
openai.api_key = "sk-MrL5ITPlkmI69SymwgYWgClrzKIIfu9evMvId1IlyKTCkmxC"

def load_data(DATASET):
    return pd.read_json(DATASET)

def hard_prompt_maker(test_sample_text,database,schema_links,sub_questions):
  instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  stepping = f'''\nA: Let's think step by step. "{test_sample_text}" can be solved by knowing the answer to the following sub-question "{sub_questions}".'''
  fields += "\n"
  prompt = instruction +fields + hard_prompt + 'Q: "' + test_sample_text + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question"'
  return prompt
def medium_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  prompt = instruction +fields + medium_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
  return prompt
def easy_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += find_fields_MYSQL_like(database)
  fields += "\n"
  prompt = instruction +fields + easy_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nSQL:'
  return prompt
def classification_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
  instruction += "\nif need nested queries: predict NESTED\n"
  instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
  instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  prompt = instruction + fields + classification_prompt + 'Q: "' + test_sample_text + '\nschema_links: ' + schema_links + '\nA: Let’s think step by step.'
  return prompt
def schema_linking_prompt_maker(test_sample_text,database):
  instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
  fields = find_fields_MYSQL_like(database)
  foreign_keys = "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  prompt = instruction + schema_linking_prompt + fields +foreign_keys+ 'Q: "' + test_sample_text + """"\nA: Let’s think step by step."""
  return prompt
def find_foreign_keys_MYSQL_like(db_name):
  df = spider_foreign[spider_foreign['Database name'] == db_name]
  output = "["
  for index, row in df.iterrows():
    output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row['Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
  output= output[:-1] + "]"
  return output
def find_fields_MYSQL_like(db_name):
  df = spider_schema[spider_schema['Database name'] == db_name]
  df = df.groupby(' Table Name')
  output = ""
  for name, group in df:
    output += "Table " +name+ ', columns = ['
    for index, row in group.iterrows():
      output += row[" Field Name"]+','
    output = output[:-1]
    output += "]\n"
  return output
def find_primary_keys_MYSQL_like(db_name):
  df = spider_primary[spider_primary['Database name'] == db_name]
  output = "["
  for index, row in df.iterrows():
    output += row['Table Name'] + '.' + row['Primary Key'] +','
  output = output[:-1]
  output += "]\n"
  return output
def creatiing_schema(DATASET_JSON):
    schema_df = pd.read_json(DATASET_JSON)
    schema_df = schema_df.drop(['column_names','table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index == -1:
                for table in tables:
                    schema.append([row['db_id'], table, '*', 'text'])
            else:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in primary_keys:
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
    spider_schema = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
    spider_primary = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    spider_foreign = pd.DataFrame(f_keys,
                        columns=['Database name', 'First Table Name', 'Second Table Name', 'First Table Foreign Key',
                                 'Second Table Foreign Key'])
    return spider_schema,spider_primary,spider_foreign
def debuger(test_sample_text,database,sql):
  instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.
#### Use the following instructions for fixing the SQL QUERY:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.

"""
  fields = find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "Primary_keys = " + find_primary_keys_MYSQL_like(database)
  prompt = instruction + fields+ '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY\nSELECT'
  return prompt
def GPT4_generation(prompt):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    n = 1,
    stream = False,
    temperature=0.0,
    max_tokens=600,
    top_p = 1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop = ["Q:"]
  )
  return response['choices'][0]['message']['content']

def GPT4_debug(prompt):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    n = 1,
    stream = False,
    temperature=0.0,
    max_tokens=350,
    top_p = 1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop = ["#", ";","\n\n"]
  )
  return response['choices'][0]['message']['content']


if __name__ == '__main__':
    spider_schema, spider_primary, spider_foreign = creatiing_schema(DATASET_SCHEMA)
    val_df = load_data(DATASET)
    # print(f"Number of data samples {val_df.shape[0]}")
    CODEX = []
    for index, row in val_df.iterrows():
        if index != 743:
            continue
        print(f"index is {index}")
        # print(row['query'])
        print(row['question'])

        # 获取 schema_links
        schema_links = None
        while schema_links is None:
            try:
                schema_links = GPT4_generation(
                    schema_linking_prompt_maker(row['question'], row['db_id'])
                )
            except:
                time.sleep(3)
                pass
        try:
            schema_links = schema_links.split("Schema_links: ")[1]
        except:
            print("Slicing error for the schema_linking module")
            schema_links = "[]"
        print("schema_links:",schema_links)
        classification = None
        while classification is None:
            try:
                classification = GPT4_generation(
                    classification_prompt_maker(row['question'], row['db_id'], schema_links[1:])
                )
            except:
                time.sleep(3)
                pass
        try:
            predicted_class = classification.split("Label: ")[1]
        except:
            print("Slicing error for the classification module")
            predicted_class = '"NESTED"'

        print("classification:",classification)

        # 判断分类类型
        if '"EASY"' in predicted_class:
            print("EASY")
            SQL = None
            while SQL is None:
                try:
                    SQL = GPT4_generation(easy_prompt_maker(row['question'], row['db_id'], schema_links))
                except:
                    time.sleep(3)
                    pass
        elif '"NON-NESTED"' in predicted_class:
            print("NON-NESTED")
            SQL = None
            while SQL is None:
                try:
                    SQL = GPT4_generation(medium_prompt_maker(row['question'], row['db_id'], schema_links))
                except:
                    time.sleep(3)
                    pass
            try:
                SQL = SQL.split("SQL: ")[1]
            except:
                print("SQL slicing error")
                SQL = "SELECT"
        else:
            # 如果无法匹配 'questions = ["'，直接将 SQL 设置为 "SELECT"
            if 'questions = ["' not in classification:
                print("questions not found in classification, setting SQL to SELECT")
                SQL = "SELECT"
                # 保存到 CODEX 中
                CODEX.append([row['question'], SQL, row['query'], row['db_id']])
                continue  # 跳过后续逻辑
            # 解析子问题
            sub_questions = classification.split('questions = ["')[1].split('"]')[0]
            print("NESTED")
            SQL = None
            while SQL is None:
                try:
                    SQL = GPT4_generation(
                        hard_prompt_maker(row['question'], row['db_id'], schema_links, sub_questions)
                    )
                except:
                    time.sleep(3)
                    pass
            try:
                SQL = SQL.split("SQL: ")[1]
            except:
                print("SQL slicing error")
                SQL = "SELECT"

        print(SQL)

        # 调试 SQL
        debugged_SQL = None
        while debugged_SQL is None:
            try:
                debugged_SQL = GPT4_debug(debuger(row['question'], row['db_id'], SQL)).replace("\n", " ")
            except:
                time.sleep(3)
                pass
        SQL = "SELECT " + debugged_SQL
        print(SQL)

        # 保存结果到 CODEX
        CODEX.append([row['question'], SQL, row['query'], row['db_id']])
        break  



    # 保存到 DataFrame 并写入文件
    df = pd.DataFrame(CODEX, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])
    results = df['PREDICTED SQL'].tolist()
    with open(OUTPUT_FILE, 'w') as f:
        for line in results:
            f.write(f"{line}\n")



# if __name__ == '__main__':
#     spider_schema,spider_primary,spider_foreign = creatiing_schema(DATASET_SCHEMA)
#     val_df = load_data(DATASET)
#     print(f"Number of data samples {val_df.shape[0]}")
#     CODEX = []
#     for index, row in val_df.iterrows():
#         #if index < 405: continue #for testing
#         # 只测试序号为6的数据
#         if index != 62:
#             continue
#         print(f"index is {index}")
#         print(row['query'])
#         print(row['question'])
#         schema_links = None
#         while schema_links is None:
#             try:
#                 schema_links = GPT4_generation(
#                     schema_linking_prompt_maker(row['question'], row['db_id']))
#             except:
#                 time.sleep(3)
#                 pass
#         try:
#             schema_links = schema_links.split("Schema_links: ")[1]
#         except:
#             print("Slicing error for the schema_linking module")
#             schema_links = "[]"
#         #print(schema_links)
#         classification = None
#         while classification is None:
#             try:
#                 classification = GPT4_generation(
#                     classification_prompt_maker(row['question'], row['db_id'], schema_links[1:]))
#             except:
#                 time.sleep(3)
#                 pass
#         try:
#             predicted_class = classification.split("Label: ")[1]
#         except:
#             print("Slicing error for the classification module")
#             predicted_class = '"NESTED"'
#         print(classification)
#         if '"EASY"' in predicted_class:
#             print("EASY")
#             SQL = None
#             while SQL is None:
#                 try:
#                     SQL = GPT4_generation(easy_prompt_maker(row['question'], row['db_id'], schema_links))
#                 except:
#                     time.sleep(3)
#                     pass
#         elif '"NON-NESTED"' in predicted_class:
#             print("NON-NESTED")
#             SQL = None
#             while SQL is None:
#                 try:
#                     SQL = GPT4_generation(medium_prompt_maker(row['question'], row['db_id'], schema_links))
#                 except:
#                     time.sleep(3)
#                     pass
#             try:
#                 SQL = SQL.split("SQL: ")[1]
#             except:
#                 print("SQL slicing error")
#                 SQL = "SELECT"
#         else:
#             sub_questions = classification.split('questions = ["')[1].split('"]')[0]
       

#             print("NESTED")
#             SQL = None
#             while SQL is None:
#                 try:
#                     SQL = GPT4_generation(
#                         hard_prompt_maker(row['question'], row['db_id'], schema_links, sub_questions))
#                 except:
#                     time.sleep(3)
#                     pass
#             try:
#                 SQL = SQL.split("SQL: ")[1]
#             except:
#                 print("SQL slicing error")
#                 SQL = "SELECT"
#         print(SQL)
#         debugged_SQL = None
#         while debugged_SQL is None:
#             try:
#                 debugged_SQL = GPT4_debug(debuger(row['question'], row['db_id'], SQL)).replace("\n", " ")
#             except:
#                 time.sleep(3)
#                 pass
#         SQL = "SELECT " + debugged_SQL
#         print(SQL)
#         CODEX.append([row['question'], SQL, row['query'], row['db_id']])
#         break
#     df = pd.DataFrame(CODEX, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE'])
#     results = df['PREDICTED SQL'].tolist()
#     with open(OUTPUT_FILE, 'w') as f:
#         for line in results:
#             f.write(f"{line}\n")

