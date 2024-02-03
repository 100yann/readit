import psycopg2
from psycopg2.sql import Identifier
import os
import bcrypt


db_config = {
    'dbname': 'readit',
    'user': 'postgres',
    'password': os.environ.get('db_password'),
    'host': os.environ.get('host'),
    'port': os.environ.get('port')
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


def get_reviews(isbn=None):
    connection = psycopg2.connect(**db_config)
    db_query = """
    SELECT reviews.*, users.id, users.first_name, users.last_name
    FROM reviews
    INNER JOIN users on reviews.user_id = users.id
    """

    cursor = connection.cursor()

    if isbn:
        db_query += 'WHERE book_reviewed = %s'
        cursor.execute(db_query, (isbn,))
    else:
        cursor.execute(db_query)
        
    colnames = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    combined_data = [dict(zip(colnames, row)) for row in results]
    return combined_data


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


def save_user(email, password, first_name, last_name):
    # Save to db
    columns = ['email', 'password', 'first_name', 'last_name']
    data = [email, password, first_name, last_name]
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


def get_user_data(id):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = 'SELECT first_name, last_name, email FROM users WHERE id = %s'
    cursor.execute(db_query, (id,))
    user_data = cursor.fetchone()

    close_connection(connection)
    return user_data