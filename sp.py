import pymssql
from imports.lol import connection_string
def call_chatbot_stored_procedure(query_type, application_no, dl_rc_type):
    try:
        conn = pymssql.connect(**connection_string)
        cursor = conn.cursor()
        cursor.callproc('BrchatBot', (query_type, application_no, dl_rc_type))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    
    except Exception as e:
        print("Error:", e)
        return None
