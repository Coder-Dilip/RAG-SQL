from django.shortcuts import redirect, render
import google.generativeai as genai
from decouple import config
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



# Configure the SDK with your API key
genai.configure(api_key=config('GOOGLE_API_KEY'))


import json

@csrf_exempt
def classify_query(request):
    prompt1 = """
    I want you to only provide me a list of table names in string format, separated by commas, which can be associated with the user query provided.
    table_descriptions = [
        {
            "Users": "The 'Users' table stores information about the customers using the food delivery service."
        },
        {
            "Restaurants": "The 'Restaurants' table holds details about the restaurants partnered with the service."
        },
        {
            "MenuItems": "The 'MenuItems' table stores information about the food items offered by each restaurant."
        },
        {
            "Orders": "The 'Orders' table captures the details of each order placed by users."
        },
        {
            "OrderItems": "The 'OrderItems' table records the specific items included in each order."
        }
    ]
    user_query = "I want names of the users who have ordered more than 100 items from my restaurant named 'dilip kitchen'. I want to provide them discount vouchers"
    """

    if prompt1:
        model_name = 'gemini-1.0-pro'
 

        # Initialize the Generative Model
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt1)

        # Extract and process the response
        result_text = response.text.strip()
        table_names = [name.strip() for name in result_text.split(',')]
        print("First Response", table_names)


        return JsonResponse({'table_names': table_names})

    return JsonResponse({'error': 'No query provided'}, status=400)







import os
import sqlite3
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
import uuid
def upload_db(request):
    if request.method == 'POST':
        unique_id = uuid.uuid4().hex
        file_name = f"{unique_id}"
        db_file = request.FILES['db_file']
        _, file_extension = os.path.splitext(db_file.name)

        db_path = os.path.join(settings.MEDIA_ROOT, file_name+file_extension)
        # Generate a unique file name


        # Save the uploaded file
        with open(db_path, 'wb+') as destination:
            for chunk in db_file.chunks():
                destination.write(chunk)

        # Determine the file extension
        file_extension = os.path.splitext(db_file.name)[1].lower()

        if file_extension == '.sql':
            # Convert .sql to .sqlite3
            sqlite_db_path = os.path.join(settings.MEDIA_ROOT, file_name + '.sqlite3')
            with open(db_path, 'r') as sql_file:
                sql_script = sql_file.read()
            
            # Create a new SQLite database
            conn = sqlite3.connect(sqlite_db_path)
            cursor = conn.cursor()
            
       
            
            try:
                # Execute SQL script to create tables and populate data
                cursor.executescript(sql_script)
                conn.commit()
            except sqlite3.OperationalError as e:
                print("SQLite OperationalError:", e)
                
            conn.commit()
            conn.close()

            # Remove the original .sql file
            os.remove(db_path)

            # Update db_path to the new .sqlite3 file
            db_path = sqlite_db_path

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Create a list of table names
        table_names = [table[0] for table in tables if table[0]!='sqlite_sequence']

        table_info = {}

        # Retrieve column information for each table
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                column_info = [{col[1]: col[2]} for col in columns]
                table_info[table_name] = column_info
        table_info_json = json.dumps(table_info, indent=4)

        # Close the connection
        conn.close()

        prompt1 = f"""
   I want you to generate me only a json in which the key should be table name and the value should be in text format telling about details of the what the table data is about. These are the tables i have: {table_info_json}
    """

        
        model_name = 'gemini-1.0-pro'


    # Initialize the Generative Model
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt1)

    # Extract and process the response
        result_text = response.text.strip()
        print(result_text)
       


        # Return the list of table names
        return render(request, 'table_list.html', {'table_names': table_names, 'db_path': file_name + '.sqlite3','table_info':result_text})

    return render(request, 'index.html')


from urllib.parse import unquote

def get_table_data(request):
    table_name = request.GET.get('table_name')
    db_path = request.GET.get('db_path')

    db_path=os.path.join(settings.MEDIA_ROOT, db_path)
    

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Fetch data from the selected table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Format the data as a list of dictionaries
    table_data = [dict(zip(column_names, row)) for row in rows]

    # Close the connection
    conn.close()

    return JsonResponse(table_data, safe=False)



import re
# filtering useful table names according to the user query and then genrerating sql query based on that
@csrf_exempt
def get_table_overview(request):


    # For filtering the table names
    query = request.GET.get('query')
    tableinfo = request.GET.get('table_info')
    decoded_data = unquote(tableinfo)
    print('lol',decoded_data)

    # Use the data as needed
    print("table info",decoded_data)
    prompt1 = f"""
    I want you to only provide me a list of table names in string format, separated by commas, which can be associated with the user query provided.
    table_descriptions = {decoded_data}
    user_query = '{query}'
    """
        
    model_name = 'gemini-1.0-pro'

    
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt1)

   
    result_text = response.text.strip()
    table_names = [name.strip() for name in result_text.split(',')]
    print(table_names)
    cleaned_response = []
    for item in table_names:
        # Remove double quotes if they are surrounding the item
        if item.startswith('"') and item.endswith('"'):
            cleaned_item = item[1:-1]  # Remove the surrounding quotes
        else:
            cleaned_item = item
        cleaned_response.append(cleaned_item)
    print("First Response", cleaned_response)

  
    db_name=request.GET.get('table_name')
    db_path = os.path.join(settings.MEDIA_ROOT, db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
 
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

   
    table_names = [table[0] for table in tables]

    table_info = {}

  
    for table in tables:
        table_name = table[0]
        if table_name in cleaned_response or len(tables)<=5:
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_info = [{col[1]: col[2]} for col in columns]
            table_info[table_name] = column_info

    table_info_json = json.dumps(table_info, indent=4)
    print(table_info_json)

    prompt2=f'''I want you to provide me only clean SQL query based on the user query provided. This is the user query {query} and the database table we have is {table_info_json} '''
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt2)

   
    result_text = response.text.strip()
    print(result_text)
    result_text=result_text.replace('sql', '').replace('SQL','')
    cleaned_query = re.sub(r'```', '', result_text)
    
    cursor.execute(cleaned_query)
    results = cursor.fetchall()  # List of tuples containing results

    # Convert results to a list of dictionaries for easier JSON serialization
    column_names = [col[0] for col in cursor.description]  # Get column names
    data = [{column: value for column, value in zip(column_names, row)} for row in results]
    
    return JsonResponse({'data': data,'query':cleaned_query})  # Return JSON response

    

    
   



        




