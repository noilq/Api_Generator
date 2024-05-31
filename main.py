import mysql.connector # type: ignore 
from pydantic import BaseModel, Field # type: ignore 
from typing import List 
import time 
import json 
from pydanticModels import process_models 
from apiCreator import create_api
import server
import subprocess
import os
import shutil
import asyncio

if __name__ == "__main__":
    server.start_server()
def create_database(host, user, password, database_name, sql_code: str): 
    """ 
    Creates database. 
 
    Arguments: 
        host (str): Db host. 
        user (str): Db user. 
        password (str): User password. 
        database_name (str): Name of database. 
        sql_code (str): Code for database creation. 
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
        #print(type(sql_code))
        #create db 
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name}") 
        cursor.execute(f"CREATE DATABASE {database_name}") 
        cursor.execute(f"USE {database_name}") 
 
        #instead of multi=True execute each command one by one 
        sql_commands = sql_code.strip().split(';') 
        for command in sql_commands: 
            if command.strip(): 
                cursor.execute(command + ';') 
        #cursor.execute(sql_code, multi=True) 
        #cursor.execute(f"USE {database_name}") 
 
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
        host (str): Db host. 
        user (str): Db user. 
        password (str): User password. 
        database_name (str): Database name. 
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
        #get info about table
        cursor.execute(f"DESCRIBE {table_name}")
        description = cursor.fetchall()
        table_descriptions[table_name] = description
 
    cursor.close() 
    connection.close() 
 
    return table_descriptions, table_count 
 
def format_database(host, user, password, database_name): 
    """ 
    Adds into db IsActive column. 
 
    Arguments: 
        host (str): Db host. 
        user (str): Db user. 
        password (str): User password. 
        database_name (str): Database name. 
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
        #add IsActive column to tables
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN IsActive BOOLEAN DEFAULT TRUE")
 
    cursor.close() 
    connection.close() 
 
    return
 
def format_sql_code(database_name, sql_code_body): 
    """ 
    Returns formated sql code. 
 
    Arguments: 
        database_name (str): Name of db. 
        sql_code_body (str): Db code. 
    Returns: 
        Str: Formated sql code. 
    """ 
    if any(line.strip().startswith(("CREATE DATABASE", "USE")) for line in sql_code_body.strip().split('\n')): 
        sql_code_body = [line for line in sql_code_body.strip().split('\n') if not line.strip().startswith(("CREATE DATABASE", "USE"))] 
        sql_code_body = '\n'.join(sql_code_body) 
     
    return sql_code_body
 
host = 'localhost' 
user = 'root' 
password = '' 
database_name = 'newdb' 
 
sql_code_body = """ 
 
 
 
-- Create the Manufacturers table 
CREATE TABLE Manufacturers ( 
    ManufacturerID INT AUTO_INCREMENT PRIMARY KEY, 
    Name VARCHAR(255) NOT NULL, 
    Country VARCHAR(255) NOT NULL, 
    FoundedYear INT 
); 
 
-- Create the Models table 
CREATE TABLE Models ( 
    ModelID INT AUTO_INCREMENT PRIMARY KEY, 
    ManufacturerID INT NOT NULL, 
    Name VARCHAR(255) NOT NULL, 
    Year INT NOT NULL, 
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID) 
); 
 
-- Create the Dealerships table 
CREATE TABLE Dealerships ( 
    DealershipID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL, 
    Location VARCHAR(255) NOT NULL, 
    ContactNumber VARCHAR(20) 
); 
 
-- Create the Cars table 
CREATE TABLE Cars ( 
    CarID INT AUTO_INCREMENT PRIMARY KEY, 
    ModelID INT NOT NULL, 
    DealershipID INT NOT NULL, 
    VIN VARCHAR(17) NOT NULL UNIQUE, 
    Price DECIMAL(10, 2) NOT NULL, 
    Status ENUM('Available', 'Sold', 'Servicing') NOT NULL, 
    FOREIGN KEY (ModelID) REFERENCES Models(ModelID), 
    FOREIGN KEY (DealershipID) REFERENCES Dealerships(DealershipID) 
); 
 
-- Create the Customers table 
CREATE TABLE Customers ( 
    CustomerID INT AUTO_INCREMENT PRIMARY KEY, 
    FirstName VARCHAR(255) NOT NULL, 
    LastName VARCHAR(255) NOT NULL, 
    Email VARCHAR(255) NOT NULL UNIQUE, 
    PhoneNumber VARCHAR(20), 
    Address TEXT 
); 
 
-- Create the Sales table 
CREATE TABLE Sales ( 
    SaleID INT AUTO_INCREMENT PRIMARY KEY, 
    CarID INT NOT NULL, 
    CustomerID INT NOT NULL, 
    SaleDate DATE NOT NULL, 
    SalePrice DECIMAL(10, 2) NOT NULL, 
    FOREIGN KEY (CarID) REFERENCES Cars(CarID), 
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) 
); 
 
-- Create the ServiceRecords table 
CREATE TABLE ServiceRecords ( 
    ServiceID INT AUTO_INCREMENT PRIMARY KEY, 
    CarID INT NOT NULL, 
    ServiceDate DATE NOT NULL, 
    Description TEXT NOT NULL, 
    Cost DECIMAL(10, 2), 
    FOREIGN KEY (CarID) REFERENCES Cars(CarID) 
); 
 
""" 
 
def main(host, user, password, database_name, sql_code_body: str): 
    #db creation 
    sql_code = sql_code_body#= format_sql_code(database_name, sql_code_body)
    
    create_database(host, user, password, database_name, sql_code) 
 
    #get db info + format into json 

    format_database(host, user, password, database_name)
    db_info, depth = get_database_info(host, user, password, database_name) 
    db_info_json = json.dumps(db_info, indent=depth) 
    #print(db_info_json) 
 
    pydantic_script = process_models(db_info_json, database_name)
    enpoints_script = create_api(pydantic_script, database_name)

    return enpoints_script

def start_api_on_port(database_name, sql_code, api_script, api_port, mariadb_port, count):
    """
    Start API on a specified port.

    Argumens:
        `database_name` (str): The name of the database to be created.
        `sql_code` (str): The SQL code to be executed for database initialization.
        `api_script` (str): The path to the API script.
        `api_port` (int): The port on which the API will run.
        `mariadb_port` (int): The port on which MariaDB will run.
        `count` (int): A numeric identifier for this instance.
    """

    #os.environ['API_SCRIPT'] = api_script.replace('/', '.').replace('.py', '') + ':app'
    #os.environ['API_PORT'] = str(api_port)
    #os.environ['MARIADB_PORT'] = str(mariadb_port)
    
    #command = ['docker-compose', 'up', '--build']
    #subprocess.run(command, check=True)

    #Create fastapiN folder
    fastapi_folder = f"fastapi{count}"
    os.makedirs(fastapi_folder, exist_ok=True)

    #Create Dockerfile in fastapiN folder
    with open(os.path.join(fastapi_folder, "Dockerfile"), "w") as dockerfile:
        dockerfile.write(f"""FROM python:3.9
                         
WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]""")
    
    #Create requirements.txt file in fastapiN folder
    with open(os.path.join(fastapi_folder, "requirements.txt"), "w") as requirements:
        requirements.write("""fastapi\nmysql-connector-python""")

    #Create main.py file in fastapiN folder, copy everything from generated crud_api.py script
    shutil.copy(api_script, os.path.join(fastapi_folder, "main.py"))

    #Test
    api_script_dest = os.path.join(fastapi_folder, "main.py")
    shutil.copy(api_script, api_script_dest)
    with open(api_script_dest, "r") as main_file:
        lines = main_file.readlines()

    with open(api_script_dest, "w") as main_file:
        for line in lines:
            line = line.replace("localhost", f"mariadb{count}")
            main_file.write(line)

    with open(api_script_dest, "a") as main_file:
        main_file.write("""
if __name__ == "__main__":
    import uvicorn
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")

    #Create pydantic_models file in fastapiN folder, copy everything from generated pydantic_models
    pydantic_models_source = f"pydantic_models/{database_name}_pydantic_models.py"
    pydantic_models_dest = os.path.join(fastapi_folder, "pydantic_models.py")
    shutil.copy(pydantic_models_source, pydantic_models_dest)

    #Create mariadb_data and sql folders
    mariadb_data_folder = f"mariadb_data{count}"
    sql_folder = f"sql{count}"
    os.makedirs(mariadb_data_folder, exist_ok=True)
    os.makedirs(sql_folder, exist_ok=True)
    
    #Copy into sql folder user given sql code
    sql_file_path = os.path.join(sql_folder, "init.sql")
    with open(sql_file_path, "w") as sql_file:
        sql_file.write(sql_code)

    #Create docker-composeN.yaml file
    with open(f"docker-compose{count}.yaml", "w") as f:
        f.write(f"""version: '3'

services:
  mariadb{count}:
    image: mariadb
    container_name: mariadb{count}
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: {database_name}
      MYSQL_USER: gooner
      MYSQL_PASSWORD: brainrot 
    ports:
      - "{mariadb_port}:3306"
    volumes:
      - ./mariadb_data{count}:/var/lib/mysql
      - ./sql{count}:/docker-entrypoint-initdb.d

  fastapi{count}:
    build:
      context: ./{fastapi_folder}
      dockerfile: Dockerfile
    container_name: fastapi{count}
    restart: always
    ports:
      - "{api_port}:8000"
    depends_on:
      - mariadb{count}
""")

    print(f"Setup on port api:{api_port} db:{mariadb_port} completed successfully.")

    #Init docker file
    command = ['docker-compose', '-f', f'docker-compose{count}.yaml', '-p', f'apigenerator{count}', 'up', '--build']
    #subprocess.run(command, check=True)
    subprocess.Popen(command)

    return f"http://localhost:{api_port}/docs"
'''
main(host, user, password, database_name, sql_code_body)
start_api_on_port('newdb', sql_code_body, 'crud_api/newdb_crud_api.py', 8001, 3311, 1)
#start_api_on_port('newdb', sql_code_body, 'crud_api/newdb_crud_api.py', 8002, 3312, 2)
#start_api_on_port('newdb', sql_code_body, 'crud_api/newdb_crud_api.py', 8003, 3313, 3)
'''