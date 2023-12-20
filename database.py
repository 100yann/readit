import psycopg2
from psycopg2.sql import Identifier

import os


db_config = {
    'user': os.environ.get('aws_user'),
    'password': os.environ.get('aws_password'),
    'host': os.environ.get('aws_host'),
    'port': os.environ.get('aws_port')
}

def insert_into_db(columns, values, table):
    connection = psycopg2.connect(**db_config)
    connection.autocommit = True
    cur = connection.cursor()

    query = "INSERT INTO {} ({}) VALUES ({});"
    
    column_str = ', '.join(map(str, columns))
    value_str = ', '.join(['%s' for col in columns])
    
    formatted_query = query.format(table, column_str, value_str)

    cur.execute(formatted_query, values)
    
    connection.close()


def get_reviews():
    connection = psycopg2.connect(**db_config)
    db_query = """
    SELECT * FROM reviews
    """
    cursor = connection.cursor()
    cursor.execute(db_query)
    return cursor.fetchall()