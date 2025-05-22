from pydantic import BaseModel, Field
from typing import Optional
from tinydb import TinyDB, Query
from uuid import uuid4
from datetime import datetime
import os


from pydantic_ai import Agent

from dotenv import load_dotenv
from framework.handlers import call_ended

from utility.email_manager import EmailManager


load_dotenv()  # Load environment variables from .env file


call_ended({})