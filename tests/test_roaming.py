#This file contains the test logic. 
#  db_conn fixture gets seen from conftest.py therefor no import is needed, we just inject it

#TO DO: json with testdata > use it as DB seed for setup and iterate over it with @pytest.mark.parametrize
#TO DO: use the setup_db.sql only to set the DB schema (table column names) not to insert data, json will take care of this

import pytest
from psycopg2.extras import RealDictCursor    #RealDictCursor returns row as dict, use column name as key to fetch the respective DB column.


@pytest.mark.usefixtures("db_conn")    
#connects the below class to the logic in the conftest.py where there is a fixture of CLASS SCOPE declared

class TestRoaming:   #classname SHOULD start with "Test" otherwise pytest ignores it and runs no auto fixture in the test functions inside it
    def test_verify_active_status(self,db_conn):       #no self needed for fixtures like db_conn
        cur=db_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT status FROM roaming_packages WHERE customer_id='CH-2024-001'")
        result=cur.fetchone()

        assert result is not None, "Test data 'CH-2024-001' not found!"
        assert result['status']=='active'

        def test_check_data_limit(self,db_conn):        #setup fixture from conftest.py: db connection and db table insert if not existing
            cur=db_conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT data_limit_mb FROM roaming_packages WHERE customer_id='CH-2024-001'")
            result=cur.fetchone()

            assert result['data_limit_mb']==2048,f"Expected 2048MB, got {result['data_limit_mb']}"



