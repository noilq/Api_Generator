from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from decimal import Decimal
class categories(BaseModel):
	category_id: int = Field(..., primary_key=True)
	name: str
	IsActive: int

class comments(BaseModel):
	comment_id: int = Field(..., primary_key=True)
	post_id: int
	user_id: int
	comment: str
	created_at: datetime
	IsActive: int

class postcategories(BaseModel):
	post_id: int = Field(..., primary_key=True)
	category_id: int = Field(..., primary_key=True)
	IsActive: int

class posts(BaseModel):
	post_id: int = Field(..., primary_key=True)
	user_id: int
	title: str
	content: str
	created_at: datetime
	IsActive: int

class tags(BaseModel):
	tag_id: int = Field(..., primary_key=True)
	post_id: int
	tag_name: str
	IsActive: int

class users(BaseModel):
	user_id: int = Field(..., primary_key=True)
	username: str
	email: str
	password: str
	created_at: datetime
	IsActive: int

