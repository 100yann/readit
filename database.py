import psycopg2
import os

db_config = {
    'user': os.environ.get('aws_user')
    'password': os.environ.get('aws_password'),
    'host': os.environ.get('aws_host'),
    'port': os.environ.get('aws_port')
}


connection = psycopg2.connect(**db_config)
connection.autocommit = True

db_create_query = """

"""

cursor = connection.cursor()
cursor.execute(db_create_query)
connection.close()