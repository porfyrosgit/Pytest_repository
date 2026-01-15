#This is for sharing "fixtures" (setup/teardown code). Pytest reads it, but it doesn't count as a test itself.
#This file acts as the central hub for Pytest. 
# The fixtures here are automatically discovered by any test file in the same directory.

import pytest       # [PYTEST] Framework for decorators and fixtures
import os           # [STANDARD] To fetch DATABASE_URL from environment
import psycopg2     # [IMPORTED LIB] PostgreSQL driver for Python
from psycopg2.extras import RealDictCursor

# FIXTURE DEFINITIONS (Centralized in conftest.py)
 
@pytest.fixture(scope="class")    
# [PYTEST]:  scope="class" - setup executed once for the whole class and is available for all test functions inside it
#     PURPOSE: here Opens the DB connection ONCE for the whole class.
#     This is high-performance: it prevents opening/closing sockets for every test.

# --- SETUP STEP ---
def db_conn():                                  #Created once per class for Speed and efficiency.
    connection_uri=os.getenv("DATABASE_URL")  #pull DB connection info from .env file
    conn=psycopg2.connect(connection_uri)  #connect to postgresDB

    yield conn                              # [PYTEST]: 'yield' separates SETUP from TEARDOWN

# --- TEARDOWN STEP ---
    # This runs ONLY after all tests in the class are finished.
    # It deletes only the data created by our test suite using the CH-2024-% pattern, so DB doesnt get cluttered with test records
    cur=conn.cursor()
    cur.execute("DELETE FROM roaming_packages WHERE customer_id LIKE 'CH-2024-%';")
    cur.execute("DELETE FROM customers WHERE customer_id LIKE 'CH-2024-%';")
    conn.commit()   #commit whatever the query did to the DB
    cur.close()   #we close the cursor that provides access to the requested data like a pointer
    conn.close()   #we close the connection to the DB

@pytest.fixture(autouse=True)   #pytest fixture decorator
def refresh_database (db_conn):         
    
    #[PYTEST]: autouse=True automatically runs this method before EVERY test function for consistency.
    #Method: Even though the connection stays open, we ensure the data is 'active'.
    
 cur=db_conn.cursor()     
#.execute sends the SQL string to Postgres
 cur.execute(""""                                  
            UPDATE roaming_packages
            SET status='active',data_used_mb=0,expiry_date=NOW()+INTERNAL'7 days'
            WHERE customer_id LIKE 'CH-2024-%';
            """)
 db_conn.commit()     #commit changes to DB permanently
 cur.close


