prompt1="""
I want you to only provide me list of the table names in string format which can be associated with the user query provided
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
user_query = "top menuitems where high number of orders are done"
"""