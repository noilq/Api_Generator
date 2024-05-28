import mysql.connector # type: ignore
from pydantic import BaseModel, Field # type: ignore
from typing import List
import time
import json
from pydanticModels import process_models
from apiCreator import create_api

def create_database(host, user, password, database_name, sql_code):
    """
    Creates database.

    Arguments:
        `host` (str): Db host.
        `user` (str): Db user.
        `password` (str): User password.
        `database_name` (str): Name of database.
        `sql_code` (str): Code for database creation.
    Returns:
        1: Success.
        0: Fail.
    """
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password
        )

    if connection.is_connected():
        cursor = connection.cursor()
        #create db
        cursor.execute(sql_code, multi=True)  
        print(f'Database "{database_name}" successfully created.')
        cursor.close()
        connection.close()
        return 1
    else:
        print('Unable to connect to db.')
        return 0

def get_database_info(host, user, password, database_name):
    """
    Returns information about all tables in database.

    Arguments:
        `host` (str): Db host.
        `user` (str): Db user.
        `password` (str): User password.
        `database_name` (str): Database name.
    Return:
        Dics/List: List of strings with database descriptions.
        Int: Count of tables.
    """
    time.sleep(0.1)
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database_name  
    )
    
    cursor = connection.cursor()
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_count = len(tables)
    table_descriptions = {}
    
    for (table_name,) in tables:
        cursor.execute(f"DESCRIBE {table_name}")
        description = cursor.fetchall()
        table_descriptions[table_name] = description

    cursor.close()
    connection.close()

    return table_descriptions, table_count

    #get info about db

def format_sql_code(database_name, sql_code_body):
    """
    Returns formated sql code.

    Arguments:
        `database_name` (str): Name of db.
        `sql_code_body` (str): Db code.
    Returns:
        Str: Formated sql code.
    """
    sql_code_base = f"""
    DROP DATABASE IF EXISTS {database_name};
    CREATE DATABASE IF NOT EXISTS {database_name};
    USE {database_name};    
    """

    sql_code_body = [line for line in sql_code_body.strip().split('\n') if not line.strip().startswith(("CREATE DATABASE", "USE"))]
    sql_code_body = '\n'.join(sql_code_body)

    return sql_code_base + sql_code_body

host = 'localhost'
user = 'root'
password = ''
database_name = 'newdb'

sql_code_body = """
CREATE DATABASE BlogPlatform;

USE BlogPlatform;

-- Create Users table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Posts table
CREATE TABLE Posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Create Comments table
CREATE TABLE Comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Create Categories table
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create PostCategories table (many-to-many relationship between Posts and Categories)
CREATE TABLE PostCategories (
    post_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (post_id, category_id),
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- Create Tags table
CREATE TABLE Tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (post_id) REFERENCES Posts(post_id)
);
"""

def main(host, user, password, database_name, sql_code_body):
    #db creation
    sql_code = format_sql_code(database_name, sql_code_body)
    create_database(host, user, password, database_name, sql_code)

    #get db info + format into json
    db_info, depth = get_database_info(host, user, password, database_name)
    db_info_json = json.dumps(db_info, indent=depth)
    #print(db_info_json)

    pydantic_script = process_models(db_info_json, database_name)

    enpoints_script = create_api(pydantic_script)

main(host, user, password, database_name, sql_code_body)