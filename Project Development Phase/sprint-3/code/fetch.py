from dotenv import load_dotenv
import os
import ibm_db



def fetch_home(conn):
    sql = "SELECT COUNT(*) , (SELECT COUNT(*) FROM DONORS WHERE blood_type= 'A Positive'),"
    sql += "(SELECT COUNT(*) FROM DONORS WHERE blood_type='A Negative'), (SELECT COUNT(*) FROM DONORS WHERE blood_type='B Positive'),"
    sql += "(SELECT COUNT(*) FROM DONORS WHERE blood_type='B Negative'), (SELECT COUNT(*) FROM DONORS WHERE blood_type='O Positive'),"
    sql += "(SELECT COUNT(*) FROM DONORS WHERE blood_type='O Negative'), (SELECT COUNT(*) FROM DONORS WHERE blood_type='AB Positive'),"
    sql += "(SELECT COUNT(*) FROM DONORS WHERE blood_type='AB Negative') from donors"

    req_sql = "SELECT COUNT(*) FROM REQUESTS WHERE REQUEST_STATUS != 'ACCEPTED'"
    req_stmt = ibm_db.prepare(conn,req_sql)
    ibm_db.execute(req_stmt)
    req = ibm_db.fetch_assoc(req_stmt)
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    res = ibm_db.fetch_assoc(stmt)
    return req,res
