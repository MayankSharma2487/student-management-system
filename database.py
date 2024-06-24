from multiprocessing import connection
from flask import g
import sqlite3

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    admin BOOLEAN NOT NULL DEFAULT '0'
);
"""

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    empid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone INTEGER,
    address TEXT,      
    joining_date DATE DEFAULT CURRENT_TIMESTAMP,
    total_attendence INTEGER DEFAULT '1',
    total_fees_paid INTEGER DEFAULT '1',
    total_fees_pending INTEGER DEFAULT '1',
    total_assignment_submitted INTEGER DEFAULT '1'
);
"""
def get_database():
    if not hasattr(g, 'studentdatabase_db'):
        g.studentdatabase_db = connect_to_database()
        with g.studentdatabase_db as connection:
            cursor = connection.cursor()
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(CREATE_STUDENTS_TABLE)
            connection.commit()  # Commit changes to persist the tables
    return g.studentdatabase_db

# Existing connect_to_database function (assuming it handles connection)
def connect_to_database():
    sql = sqlite3.connect('D:/COLLAGE ERP MODEL FLASK/studentdata.db')
    sql.row_factory = sqlite3.Row
    return sql

import sqlite3

# Connect to your database
conn = sqlite3.connect('studentdata.db')
# Replace 'studentdata.db' with your actual database filename

# Prepare the update statement
update_statement = """
    UPDATE users
    SET admin = 1
    WHERE name = ?
"""

# User name to update (replace with the actual name)
user_to_update = 'Mayank Sharma'

# Execute the update with the user name as a parameter
try:
    cursor = conn.cursor()
    cursor.execute(update_statement, (user_to_update,))
    conn.commit()
    print("Admin field updated successfully for", user_to_update)
except sqlite3.Error as e:
    print("Error updating admin:", e)
finally:
    # Always close the connection
    if conn:
        conn.close()