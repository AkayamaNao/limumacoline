from os import environ
from pathlib import Path
import psycopg2
import subprocess

testmode=0

# LINEbot
access_token = 'gJFfTcuSz5NYUkYp+eozfhul/5gwvi3TVVYzefFUMt8jasTl1vbX06IGkOdmWLnbQ5rmBSTO67TbYWc73XW0WXFR7VrnCDQImQFBWb9tLI6I+peMLY40BEcgu7LFmUUdIC1TwNWtW8mrfTOLwxLMJAdB04t89/1O/w1cDnyilFU='
secret_key = '0c2ca89194fe8a2178d8f25c2da15730'

root_password = '88248075a3514f106c0c16ee16aa06a22b56670b7b01ee56da49772218b1b289'

if testmode==1:
    db_info = 'postgres://xaqmiseiftraat:1f2af75031b9c5f8ad5e4d232bad8c3a0dbc27d69cee97949fbba48bc35a0b66@ec2-107-22-160-185.compute-1.amazonaws.com:5432/d7ldiibuihtqds'
    DEBUG = True
else:
    proc = subprocess.Popen('printenv DATABASE_URL', stdout=subprocess.PIPE, shell=True)
    db_info = proc.stdout.read().decode('utf-8').strip()
    DEBUG = False

SQLALCHEMY_DATABASE_URI = db_info
SQLALCHEMY_TRACK_MODIFICATIONS = True
SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
JSON_AS_ASCII = False
UPLOADED_CONTENT_DIR = Path("upload")