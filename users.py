import bcrypt
from database import *
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed


def save_user(email, password):
    # Save to db
    columns = ['email', 'password']
    data = [email, password]
    # Catch if email exists in db
    try:
        insert_into_db(columns, data, 'users')
    except psycopg2.errors.UniqueViolation:
        return False
    return True