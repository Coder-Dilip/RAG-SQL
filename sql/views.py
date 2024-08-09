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

def upload_db(request):
    if request.method == 'POST':
        db_file = request.FILES['db_file']
        db_path = os.path.join(settings.MEDIA_ROOT, db_file.name)

        # Save the uploaded file
        with open(db_path, 'wb+') as destination:
            for chunk in db_file.chunks():
                destination.write(chunk)

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Create a list of table names
        table_names = [table[0] for table in tables]
        print('table names',table_names)
        # Close the connection
        conn.close()

        # Return the list of table names
        return render(request, 'table_list.html', {'table_names': table_names, 'db_path': db_file.name})

    return render(request, 'index.html')



def get_table_data(request):
    table_name = request.GET.get('table_name')
    db_path = request.GET.get('db_path')
    print(db_path)
    db_path=os.path.join(settings.MEDIA_ROOT, db_path)
    
    print("path after",db_path)
    print('table_name',table_name)
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

        # Create a list of table names
    table_names = [table[0] for table in tables]
    print('table names after',table_names)
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

    
   



        




