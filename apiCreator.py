from pydantic import BaseModel, Field #type: ignore
from fastapi import FastAPI, HTTPException #type: ignore
import importlib.util
from typing import List

def create_api(pydantic_script):
    models = load_pydantic_models(pydantic_script)

    models_names = ", ".join([model.__name__ for model in models])

    script = f"""from fastapi import FastAPI, HTTPException\nfrom datetime import datetime, timedelta\nfrom decimal import Decimal\nfrom {pydantic_script} import {models_names}\napp = FastAPI()\n\n"""

    for model in models:
        script += create(model)
        script += read(model)
        script += update(model)
        script += delete(model)
    
    api_script_name = "crud_api.py"

    with open(api_script_name, "w") as file:
        file.write(script)

    print(f'Endpoints "{api_script_name}" successfully created.')

    return api_script_name

def load_pydantic_models(pydantic_script) -> List[BaseModel]:
    spec = importlib.util.spec_from_file_location("module_name", pydantic_script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    models = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj != BaseModel:
            models.append(obj)
    return models

def create(model):
    #Route + function
    string = f"""@app.post("/{model.__name__}/") \nasync def create_{model.__name__}({model.__name__}: {model.__name__}):\n"""
    #Comments
    string += f"""\t'''\n\tCreate {model.__name__} \n\tArgument: \n\t\t{model.__name__}: {model.__name__}: An object, representing model.\n\t'''\n"""
    #Function body
    string += f"""\n"""

    #for field_name, field_type in model.__annotations__.items():
    #    type_name = field_type.__name__
    #    string += f"""{field_name}: {type_name}, """

    #print(string)

    return string

def read(model):
    #Get Primary Key
    primary_key_name = None
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break

    #Check for Primary Key
    if primary_key_name is not None:
        primary_key_name_str = '{' + primary_key_name + '}'
        string = f"""@app.get("/{model.__name__}/{primary_key_name_str}") \nasync def read_{model.__name__}("""
        string += f"""{primary_key_name}: int = None"""  
    else: 
        string = f"""@app.get("/{model.__name__}/None") \nasync def read_{model.__name__}("""

    string += """):\n"""

    #Comments
    string += f"""\t'''\n\tReturn {model.__name__} \n\tArgument: \n\t\t{primary_key_name}: int: Model id.\n\t'''\n\n"""

    #print(string)

    return string

def update(model):
    #Get Primary Key
    primary_key_name = ''
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break
    
    #Check for Primary Key
    if primary_key_name is not None:
        primary_key_name_str = '{' + primary_key_name + '}'
        string = f"""@app.put("/{model.__name__}/{primary_key_name_str}") \nasync def update_{model.__name__}("""
    else: 
        string = f"""@app.put("/{model.__name__}/None") \nasync def update_{model.__name__}("""
    
    #Check for all variables
    variables = []
    for field_name, field_type in model.__annotations__.items():
        if field_name != primary_key_name:
            type_name = field_type.__name__
            variables.append(f"{field_name}: {type_name}")

    string += ", ".join(variables)
    string += """):\n"""

    #Comments
    string += f"""\t'''\n\tEdit {model.__name__} \n\tArgument: \n\t\t{',\n\t\t'.join(variables)}.\n\t'''\n\n"""

    #print(string)

    return string
    
def delete(model):
    #Get Primary Key
    primary_key_name = None
    for field_name, field in model.__fields__.items():
        if field.json_schema_extra == {'primary_key': True}:
            primary_key_name = field_name
            break

    #Check for Primary Key
    if primary_key_name is not None:
        primary_key_name_str = '{' + primary_key_name + '}'
        string = f"""@app.delete("/{model.__name__}/{primary_key_name_str}") \nasync def delete_{model.__name__}("""
        string += f"""{primary_key_name}: int"""  
    else: 
        string = f"""@app.delete("/{model.__name__}/None") \nasync def delete_{model.__name__}("""

    string += """):\n"""

    #Comments
    string += f"""\t'''\n\tDeactivate {model.__name__} \n\tArgument: \n\t\t{primary_key_name}: int: Model id.\n\t'''\n\n"""

    #print(string)

    return string