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


def get_reviews(isbn=None, limit=None, order=None):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    db_query = """
        SELECT 
            reviews.*, 
            users.id, 
            users.first_name, 
            users.last_name, 
            books.*, 
            COALESCE(COUNT(review_likes.like_id), 0) AS total_likes
        FROM reviews
        INNER JOIN users on reviews.user_id = users.id
        INNER JOIN books on reviews.book_reviewed = books.book_id
        LEFT JOIN review_likes ON reviews.review_id = review_likes.review_id
        """

    values = []
    if isbn:
        db_query += ' WHERE books.isbn = %s'
        values.append(isbn)
    
    db_query += ' GROUP BY reviews.review_id, users.id, books.book_id'

    if order:
        db_query += f' ORDER BY {order}'

    if limit:
        db_query += ' LIMIT %s'
        values.append(limit)

    cursor.execute(db_query, (*values,))
    
    colnames = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    combined_data = [dict(zip(colnames, row)) for row in results]
    return combined_data


def get_recent_reviews():
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = """
        SELECT 
            reviews.*, 
            users.id, 
            users.first_name, 
            users.last_name, 
            books.*, 
            COALESCE(COUNT(review_likes.like_id), 0) AS total_likes
        FROM reviews
        INNER JOIN users on reviews.user_id = users.id
        INNER JOIN books on reviews.book_reviewed = books.book_id
        LEFT JOIN review_likes ON reviews.review_id = review_likes.review_id
        GROUP BY reviews.review_id, users.id, books.book_id
        ORDER BY reviews.created_on DESC
        LIMIT 5
        """
    cursor.execute(db_query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


def check_if_exists(columns, table, condition1, value1, condition2=None, value2=None):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    db_query = "SELECT {} FROM {} WHERE {} = %s"

    if condition2:
        db_query += ' AND {} = %s'
        formatted_query = db_query.format(columns, table, condition1, condition2)
        cursor.execute(formatted_query, (value1, value2, ))
    else:
        formatted_query = db_query.format(columns, table, condition1)
        cursor.execute(formatted_query, (value1, ))   

    result = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return result


def get_book_id_by_isbn(isbn):
    connection = establish_connection()
    cursor = connection.cursor()

    db_query = "SELECT book_id FROM books WHERE isbn = %s;"
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


def save_like_to_db(user_id, review_id, liked=False):
    connection = establish_connection()
    cursor = connection.cursor()

    if liked:
        db_query = 'DELETE FROM review_likes WHERE user_id = %s AND review_id = %s'
        response = 'unliked'
    else:
        db_query = 'INSERT INTO review_likes (user_id, review_id) VALUES (%s, %s)'
        response = 'liked'
        
    cursor.execute(db_query, (user_id, review_id, ))
    connection.commit()
    close_connection(connection)

    return response