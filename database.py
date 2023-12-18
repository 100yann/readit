import psycopg2
import os


db_config = {
    'user': os.environ.get('aws_user'),
    'password': os.environ.get('aws_password'),
    'host': os.environ.get('aws_host'),
    'port': os.environ.get('aws_port')
}

def insert_into_db(query, *args):
    connection = psycopg2.connect(**db_config)
    connection.autocommit = True

    db_query = query

    cursor = connection.cursor()
    cursor.execute(db_query, args)
    connection.close()


def get_posts():
    connection = psycopg2.connect(**db_config)
    db_query = """
    SELECT * FROM posts
    """
    cursor = connection.cursor()
    cursor.execute(db_query)
    return cursor.fetchall()