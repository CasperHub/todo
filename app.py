import matplotlib.pyplot as plt
import os
import csv
import json
import requests
import jsonify
import datetime
import mysql.connector
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

"""
connecting to the weather api and getting a json file of the weather descriptions.
"""
API_key = "a2c69bee22d7797a8bd8966ac941a7af"
#these are the longitude and latitude values of Leiden
lon = 4.497010
lat = 52.160114

#This requests an API call to get information from the openweathermap api, with the lon and lat from above
response_API = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}")
#converts in to text
data = response_API.text
#makes a json file from the text that can be used further
parse_json = json.loads(data)
#To get the temperature do this: the temperature is in Kelvin.
temperature = parse_json['main']['temp']
#to put in Celsius: K - 273.15

mydb = mysql.connector.connect(
    user='root',
    password='root',
    port=3310,
    database='todo'
)

cursor = mydb.cursor()

app = Flask(__name__)

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/test', methods=['GET', 'POST'])
def test():
    cursor.execute("""select * from tasks""")
    data = cursor.fetchall()
    return render_template('template.html', data=data)

@app.route('/test-upload')
def index():
    return render_template('upload.html')

@app.route('/test-upload', methods=['POST'])
def upload():
    uploaded_file = request.files['task_file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        parseCSV(file_path)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))
    return redirect('test-upload')

def parseCSV(file_path):
    col_names = ['name', 'desc', 'deadline', 'duration']
    csvData = pd.read_csv(file_path, names=col_names, header=None)
    value = len(list(csvData))
    print(value)
    if value != 4:
        abort(400) # fix error if number of columns not equal to 4
    for i, row in csvData.iterrows():
        sql = """INSERT INTO tasks (`name`, `desc`, `deadline`, `duration`) values (%s, %s, %s, %s)"""
        value = (row['name'], row['desc'], row['deadline'], row['duration'])
        cursor.execute(sql, value)
        mydb.commit()
        print(i, row['name'], row['desc'], row['deadline'], row['duration'])



"""
I make a list with todos fill the table of tasks.
"""
todos = [
    {
        'name': 'Write a blog post',
        'duration': 90,
        'description': 'Compose an informative blog post',
        'deadline': '2023-07-10'
    },
    {
        'name': 'Attend a webinar',
        'duration': 120,
        'description': 'Participate in an educational webinar',
        'deadline': '2023-07-11'
    },
    {
        'name': 'Complete coding challenge',
        'duration': 30,
        'description': 'Solve a coding challenge',
        'deadline': '2023-07-12'
    },
    {
        'name': 'Organize files',
        'duration': 30,
        'description': 'Sort and declutter',
        'deadline': '2023-07-10'
    },
    {
        'name': 'Practice meditation',
        'duration': 20,
        'description': 'Meditate for relaxation and mindfulness',
        'deadline': '2023-07-13'
    },
    {
        'name': 'Learn a new language',
        'duration': 240,
        'description': 'Practicing german vocabulary',
        'deadline': '2023-07-14'
    }
]

"""
Create an empty list to hold the finished tasks for the 
finished.html page
"""
finished_tasks = []


def load_tasks_from_file(file):
    """
    Load tasks from a CSV file and add them to the todos list.

    Args:
        file (str): Name of the CSV file containing tasks.

    The uploaded csv file from home.html is opened and read with 'r'
    a for loop will go through each row in the uploaded file and append
    them to the todos list I created earlier
    """
    with open(file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            todos.append(row)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    This function works both POST and GET methods from the / or home
    route. First we check whether a POST or a GET request has been
    made. if  POST request has been made we check whether the task_file
    is present. It generates a secure filename to avoid hacks.
    Then we initialize task_name, duration, description and deadline.

    After this we check whether all fields are field in to make sure
    the button only accepts the input.

    in the todoo variable we grab the values from the input fields on
    home.html, these are put into the todos list.
    Render the home page and handle task creation and file upload.

    """
    # if request.method == 'POST':

    #     task_name = request.form['task_name']
    #     task_duration = request.form['task_duration']
    #     task_description = request.form['task_description']
    #     task_deadline = request.form['task_deadline']

        # Validate that all fields are filled for the "Add Task" button
        # if request.form['action'] == 'create' and (
        #         not task_name or not task_duration or not task_description
        #         or not task_deadline
        # ):
        #     return 'Please fill in all fields.'

        # todo = {
        #     'name': task_name,
        #     'duration': task_duration,
        #     'description': task_description,
        #     'deadline': task_deadline
        # }

        # todos.append(todo)  # Add the task to the list

    return render_template('home.html')


def process_uploaded_tasks(filename):
    """
    The uploaded csv file from home.html is opened and read with 'r'
    a for loop will go through each row in the uploaded file and append
    them to the todos

    Args:
        filename (str): Name of the uploaded CSV file.

    """
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            task_name = row[0]
            task_duration = row[1]
            task_description = row[2]
            task_deadline = row[3]
            todo = {
                'name': task_name,
                'duration': task_duration,
                'description': task_description,
                'deadline': task_deadline
            }
            todos.append(todo)


def sort_tasks(sort_by):
    """
    Sort the tasks in the todos list based on the specified sort
    criteria. This creates the functionality on the tasks.html page.
    There are 4 option for sorting. by duration and deadline.
    And by ascending and descending values.

    For the duration this is simply done with an integer. the deadline
    is checked with the datetime built-in python function.

    Args:
        sort_by (str): Sort criteria ('namea', 'named', 'durationa',
        'durationd', 'deadlinea', 'deadlined').

    """
    if sort_by == 'namea':
        todos.sort(key=lambda x: x['name'])
    elif sort_by == 'named':
        todos.sort(key=lambda x: x['name'], reverse=True)
    elif sort_by == 'durationa':
        todos.sort(key=lambda x: x['duration'])
    elif sort_by == 'durationd':
        todos.sort(key=lambda x: x['duration'], reverse=True)
    elif sort_by == 'deadlinea':
        todos.sort(key=lambda x: datetime.strptime(x['deadline'], '%Y-%m-%d'))
    elif sort_by == 'deadlined':
        todos.sort(key=lambda x: datetime.strptime(x['deadline'], '%Y-%m-%d'), reverse=True)


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    """
    Render the tasks page and handle sorting of tasks.

    This function handles both POST and GET methods from the /tasks
    route.
    If a POST request is made, the function retrieves the 'sort_by'
    value from the form data
    and sorts the tasks accordingly using the 'sort_tasks' function.

    Renders the 'tasks.html' template with the 'todos' list and the '
    sort_by' value as template variables.

    Returns:
        The rendered HTML content of the 'tasks.html' template.
    """
    sort_by = None
    if request.method == 'POST':
        sort_by = request.form['sort_by']
        sort_tasks(sort_by)

    return render_template('tasks.html', todos=todos, sort_by=sort_by)


@app.route('/finished')
def finished():
    """
    Render the finished tasks page and generate a pie chart showing
    task completion.

    Calculates the number of unfinished and finished tasks based on
    the 'todos' and 'finished_tasks' lists.
    Calculates the percentages of unfinished and finished tasks out
    of the total number of tasks.

    Generates a pie chart using matplotlib, representing the task
    completion percentages.
    The chart is saved as an image file.

    Renders the 'finished.html' template with the necessary data to
    display the finished tasks page,
    including the chart image file.

    Returns:
        The rendered HTML content of the 'finished.html' template.
    """
    unfinished_tasks = len(todos)
    num_finished_tasks = len(finished_tasks)
    total_tasks = unfinished_tasks + num_finished_tasks

    unfinished_percentage = 0
    finished_percentage = 0

    if total_tasks > 0:
        unfinished_percentage = (unfinished_tasks / total_tasks) * 100
        finished_percentage = (num_finished_tasks / total_tasks) * 100

    # Generate the pie chart
    labels = ['Finished', 'Unfinished']
    sizes = [finished_percentage, unfinished_percentage]
    colors = ['green', 'red']
    explode = (0.1, 0)  # Explode the 'Finished' slice

    plt.pie(sizes,
            explode=explode,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            shadow=True)

    plt.axis('equal')  # Equal aspect ratio ensures circular shape
    plt.title('Task Completion')

    # Save the chart to a file
    chart_filename = 'static/task_completion_chart.png'
    plt.savefig(chart_filename)
    plt.close()

    return render_template('finished.html',
                           tasks=finished_tasks,
                           unfinished_tasks=unfinished_tasks,
                           num_finished_tasks=num_finished_tasks,
                           total_tasks=total_tasks,
                           chart_filename=chart_filename)


@app.route('/remove', methods=['POST'])
def remove_task():
    """
    Remove a task from the todos list and move it to the
    finished_tasks list.

    This function is triggered by a POST request to the '/remove'
    route.
    It retrieves the 'task_name' value from the form data and searches
    for the task
    in the 'todos' list. If a match is found, the task is moved to the
    'finished_tasks'
    list and removed from the 'todos' list. Finally, the function
    redirects to the 'tasks'
    route to refresh the tasks page.

    Returns:
        A redirect response to the 'tasks' route.
    """
    task_name = request.form['task_name']

    # Find the task in the todos list
    for task in todos:
        if task['name'] == task_name:
            # Move the task to the finished_tasks list
            finished_tasks.append(task)
            # Remove the task from the todos list
            todos.remove(task)
            break

    return redirect(url_for('tasks'))


@app.route('/about')
def about():
    """
    Render the about page.

    This function is triggered when a GET request is made to the
    '/about' route.
    It simply renders the 'about.html' template, which displays
    the information
    about the application or any relevant details.

    Returns:
        A rendered template of the 'about.html' page.
    """
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
