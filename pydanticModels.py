from pydantic import BaseModel, Field #type: ignore
import json
import re

def process_models(json_data, database_name):
    script =  f"""from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from decimal import Decimal\n"""
    data = json.loads(json_data)
    
    #print(data)
    
    #MYSQL types -> python types
    def convert_mysql_type(mysql_type):
        if "varchar" in mysql_type:
            return "str"
        elif "timestamp" in mysql_type:
            return "datetime"
        elif "decimal" in mysql_type:
            return "Decimal"
        elif "text" in mysql_type:
            return "str"
        elif "char" in mysql_type:
            return "chr"
        else:
            return mysql_type

    #Convert into pydantic-like models
    for key, value in data.items():
        script += f"class {key}(BaseModel):\n"
        primary_key_field = None
        other_fields = []
        for sublist in value:
            field_name = re.sub(r'\(.*?\)', '', sublist[0])     #Var name
            field_type = re.sub(r'\(.*?\)', '', sublist[1])     #Var type
            field_type = convert_mysql_type(field_type)

            #Check for Primary Key, adding custom Field
            if sublist[3] == 'PRI':                             #Var mod (PRI)
                primary_key_field = f"\t{field_name}: {field_type} = Field(..., primary_key=True)\n"
                script += primary_key_field
            else:
                other_fields.append(f"\t{field_name}: {field_type}\n")
            
        script += ''.join(other_fields)
        script += "\n"
    
    script_name = database_name + "_pydantic_models.py"

    with open(script_name, "w") as file:
        file.write(script)

    print(f'Pydantic models "{script_name}" successfully created.')

    return script_name
    #print(script)