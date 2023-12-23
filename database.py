import psycopg2
from psycopg2.sql import Identifier

import os


db_config = {
    'user': os.environ.get('aws_user'),
    'password': os.environ.get('aws_password'),
    'host': os.environ.get('aws_host'),
    'port': os.environ.get('aws_port')
}


def establish_connection():
    connection = psycopg2.connect(**db_config)
    return connection


def close_connection(connection):
    connection.close()
    return


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
    SELECT reviews.*, book_details.title, book_details.author, book_details.thumbnail
    FROM reviews
    INNER JOIN book_details ON reviews.book_reviewed = book_details.book_id
    """
    cursor = connection.cursor()
    cursor.execute(db_query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def check_existing(amount, table, column, value):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    db_query = "SELECT {} FROM {} WHERE {} = %s;"
    formatted_query = db_query.format(amount, table, column)
    
    result = cursor.execute(formatted_query, (value,))
    cursor.close()
    connection.close()
    return result is None


def get_book_id_by_isbn(isbn):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = "SELECT book_id FROM book_details WHERE isbn = %s;"
    cursor.execute(db_query, (isbn,))
    result = cursor.fetchone()

    close_connection(connection)
    return result
