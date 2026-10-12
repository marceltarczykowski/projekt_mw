import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI

app=FastAPI()


def get_conn():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)

