--IDEMPOTENT DATABASE SEED DATA

--TO DO: json with testdata > use it as DB seed for setup and iterate over it with @pytest.mark.parametrize
--TO DO: use the setup_db.sql only to set the DB schema (table column names) not to insert data, json will take care of this


-- 1. Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name TEXT,
    phone_number VARCHAR(20),
    account_status VARCHAR(20)
);

-- 2. Roaming packages table
CREATE TABLE IF NOT EXISTS roaming_packages (
    package_id     SERIAL PRIMARY KEY,
    customer_id    VARCHAR(50) REFERENCES customers(customer_id),
    phone_number   VARCHAR(20),
    status         VARCHAR(20) DEFAULT 'active',
    data_limit_mb  INT,
    data_used_mb   INT DEFAULT 0,
    price_chf      DECIMAL(10,2),
    expiry_date    TIMESTAMP
);

-- 3. UNIQUE constraint (simple + idempotent)
ALTER TABLE roaming_packages
DROP CONSTRAINT IF EXISTS roaming_package_number;

ALTER TABLE roaming_packages
ADD CONSTRAINT roaming_package_number UNIQUE (
    customer_id,
    phone_number,
    data_limit_mb,
    price_chf
);

-- 4. Seed data
INSERT INTO customers(customer_id, name, phone_number, account_status)
VALUES ('CH-2024-001', 'Hans Müller', '+41761213234', 'active')
ON CONFLICT (customer_id) DO NOTHING;

INSERT INTO roaming_packages(
    customer_id,
    phone_number,
    status,
    data_limit_mb,
    data_used_mb,
    price_chf
)
VALUES (
    'CH-2024-001',
    '+41761213234',
    'active',
    2048,
    1014,
    19.90
)
ON CONFLICT ON CONSTRAINT roaming_package_number DO NOTHING;


-- 3. TESTER MANIPULATION SNIPPETS (Manual Test Triggers)
-- Trigger a status failure:
-- UPDATE roaming_packages SET status = 'expired' WHERE customer_id = 'CH-2024-001';


/*
API UPDATE LOGIC  (Python Requests Lib)

import requests

url = "https://your-api.com/rest/v1/roaming_packages?customer_id=eq.CH-2024-001"
payload={"status":"expired"}
headers={"apikey":"YOUR_KEY","Content-Type":"application/json"}

response=requests.patch(url,json=payload,headers=headers)
print(f"API update status: {response.status_code}")


*/
