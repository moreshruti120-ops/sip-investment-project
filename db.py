import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="sipuser",
        password="sip123",
        database="sip_db"
    )
