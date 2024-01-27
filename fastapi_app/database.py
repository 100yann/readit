import psycopg2
from psycopg2.sql import Identifier
import os
import bcrypt


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
    print('starting')
    connection = psycopg2.connect(**db_config)
    connection.autocommit = True
    cur = connection.cursor()

    print('query')
    query = "INSERT INTO {} ({}) VALUES ({});"
    
    column_str = ', '.join(map(str, columns))
    value_str = ', '.join(['%s' for col in columns])
    
    formatted_query = query.format(table, column_str, value_str)
    print('executing')
    cur.execute(formatted_query, values)
    print('executed')
    connection.close()


def get_reviews():
    connection = psycopg2.connect(**db_config)
    db_query = """
    SELECT reviews.*, book_details.title, book_details.author, book_details.thumbnail
    FROM reviews
    INNER JOIN book_details ON reviews.book_reviewed = book_details.id
    """
    cursor = connection.cursor()
    cursor.execute(db_query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def check_if_exists(columns, table, column, value):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    db_query = "SELECT {} FROM {} WHERE {} = %s;"
    formatted_query = db_query.format(columns, table, column)
    cursor.execute(formatted_query, (value,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return result


def get_book_id_by_isbn(isbn):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = "SELECT id FROM book_details WHERE isbn = %s;"
    cursor.execute(db_query, (isbn,))
    result = cursor.fetchone()

    close_connection(connection)
    return result


def delete_row(table, column, value):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = "DELETE FROM {} WHERE {} = %s;"
    formatted_query = db_query.format(table, column)
    cursor.execute(formatted_query, (value,))
    connection.commit()
    
    close_connection(connection)
    return


def update_data(table, column, value, condition, condition_value):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = "UPDATE {} SET {} = %s WHERE {} = %s;"
    formatted_query = db_query.format(table, column, condition)
    
    cursor.execute(formatted_query, (value, condition_value, ))
    connection.commit()
    close_connection(connection)
    return



def verify_password(password, email):
    hashed_password = bytes(check_if_exists('password', 'users', 'email', email)[0])
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password


def save_user(email, password):
    # Save to db
    columns = ['email', 'password']
    data = [email, password]
    # Catch if email exists in db
    insert_into_db(columns, data, 'users')

    return True


def get_user_id(email):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = "SELECT id FROM users WHERE email= %s"
    cursor.execute(db_query, (email,))
    # returns tuple so access first element
    user_id = cursor.fetchone()[0]

    close_connection(connection)
    return user_id
