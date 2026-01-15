#This is for sharing "fixtures" (setup/teardown code). Pytest reads it, but it doesn't count as a test itself.
#This file acts as the central hub for Pytest. 
# The fixtures here are automatically discovered by any test file in the same directory.

from dotenv import load_dotenv
load_dotenv()

import pytest       # [PYTEST] Framework for decorators and fixtures
import os           # [STANDARD] To fetch DATABASE_URL from environment
import psycopg2     # [IMPORTED LIB] PostgreSQL driver for Python
from psycopg2.extras import RealDictCursor


# FIXTURE DEFINITIONS (Centralized in conftest.py)
 
@pytest.fixture(scope="class")  
# [PYTEST]:  scope="class" - setup executed once for the whole class and is available for all test functions inside it (not testfunction needs to inject it)
#auto=True NOT needed here,that would run db_conn fixture also for other Testclasses which are unrelated to the DB
#     PURPOSE: here Opens the DB connection ONCE for the whole class.
#     This is high-performance: it prevents opening/closing sockets for every test.

# --- SETUP STEP ---
def db_conn():                                  #Created once per class for Speed and efficiency.
    connection_uri=os.getenv("DATABASE_URL")  #pull DB connection info from .env file
    try:
        conn=psycopg2.connect(connection_uri)  #connect to postgresDB
    except psycopg2.OperationalError as e:
        raise RuntimeError(f"DB connection failed: {e}")
    
    # FOR CICD TO FIND THE setup_db.sql : 
    #os.path.dirname(__file__) → the folder where conftest.py lives
    #"setup_db.sql" → the SQL file
    #join → glue them together into a full path
    sql_path = os.path.join(os.path.dirname(__file__), "setup_db.sql")

    with open(sql_path, "r", encoding="utf-8") as f:          #setup:create table with customer roaming package, pulling query from setup_db.sql

       sql_script=f.read()

       cur=conn.cursor()
       cur.execute(sql_script)
       conn.commit()
       cur.close()

# --- HAND CONTROL TO THE TESTS ---
    yield conn                              # [PYTEST]: 'yield' separates SETUP from TEARDOWN

# --- TEARDOWN STEP ---(REMOVE the two hashes below to release the teardown logic and clean the tables!!)
    # This runs ONLY after all tests in the class are finished.
    # It deletes only the data created by our test suite (ID pattern CH-2024).
    cur=conn.cursor()
    # cur.execute("DELETE FROM roaming_packages WHERE customer_id LIKE 'CH-2024-%';")
    # cur.execute("DELETE FROM customers WHERE customer_id LIKE 'CH-2024-%';")
    conn.commit()   #commit whatever the query did to the DB
    cur.close()   #we close the cursor that provides access to the requested data like a pointer
    conn.close()   #we close the connection to the DB

@pytest.fixture(scope="function",autouse=True)   
#pytest fixture decorator, scope=function to run before every test function (scope=function by default even when not written)
#autouse=True: Run this fixture for every test function, even if the test does NOT inject the fixture.
#autouse=True here ensures DB state is reset before every test function, guarantees state isolation
def db_refresh (db_conn):         
    
    #Method: Even though the connection stays open, we ensure the data is 'active' and usable.
    
 cur=db_conn.cursor()     
#.execute sends the SQL string to Postgres
 cur.execute("""                                  
            UPDATE roaming_packages
            SET status='active',
                 data_used_mb=0,
                 expiry_date=NOW()+INTERVAL'7 days'
            WHERE customer_id LIKE 'CH-2024-%';
 """)
 db_conn.commit()     #commit changes to DB permanently
 cur.close


