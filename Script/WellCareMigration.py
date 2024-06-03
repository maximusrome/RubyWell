import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.exceptions import ResourceExhausted

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models import Base, Plan, PlanZipcode  # Ensure you import your Base and Plan classes

import os
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Function to get environment variables with optional default values
def get_env_variable(var_name, default=None):
    value = os.getenv(var_name)
    if value is None:
        if default is None:
            raise ValueError(f"Environment variable {var_name} is not set and no default value is provided")
        else:
            value = default
    return value

# Get environment variables
PG_USER = get_env_variable('PG_USER')
PG_PASS = get_env_variable('PG_PASS')
PG_HOST = get_env_variable('PG_HOST')
PG_PORT = get_env_variable('PG_PORT', '5432')  # Default to 5432 if not set
PG_DB = get_env_variable('PG_DB')

# Debug prints to check if environment variables are loaded correctly
print(f"PG_USER: {PG_USER}")
print(f"PG_PASS: {PG_PASS}")
print(f"PG_HOST: {PG_HOST}")
print(f"PG_PORT: {PG_PORT}")
print(f"PG_DB: {PG_DB}")

# Initialize Firebase with the credentials
cred = credentials.Certificate('./wellCareKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Setup the PostgreSQL database connection using environment variables
connection_string = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
print(f"Connection String: {connection_string}")  # Debug print for the connection string

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()

def insert_plan(plan_data):
    # Check if a plan with the given product contract code already exists in the PostgreSQL database
    exists_query = session.query(exists().where(Plan.full_plan_id == plan_data['productContractCode'])).scalar()
    if not exists_query:
        # If the plan does not exist, create a new Plan instance and add it to the session
        new_plan = Plan(
            bid_id = plan_data['productContractCode'][6:9],
            segment_number = plan_data['productContractCode'][10:13],
            contract_id = plan_data['productContractCode'][0:5],
            eoc_url = plan_data['evidenceOfCoverageLink'],
            full_plan_id = plan_data['productContractCode'],
            plan_market = '',
            plan_name = plan_data['planName'],
            source = 'WellCare Scraper',
            company = 'WellCare',
        )
        session.add(new_plan)
        session.commit()  # Commit the session to save the new plan to the database
        print(f"Inserted plan with ProductContractCode {plan_data['productContractCode']}.")
        return new_plan.id  # Return the ID of the newly inserted plan
    else:
        # If the plan already exists, fetch its ID
        print(f"Plan with ProductContractCode {plan_data['productContractCode']} already exists.")
        return session.query(Plan).filter_by(full_plan_id=plan_data['productContractCode']).first().id

def insert_plan_zipcode(plan_id, zipcode_id):
    # Check if the plan-zipcode relationship already exists in the PostgreSQL database
    exists_query = session.query(
        exists().where(
            PlanZipcode.plan_id == plan_id,
            PlanZipcode.zipcode_id == zipcode_id
        )
    ).scalar()
    if not exists_query:
        # If the relationship does not exist, create a new PlanZipcode instance and add it to the session
        new_record = PlanZipcode(plan_id=plan_id, zipcode_id=zipcode_id)
        session.add(new_record)
        session.commit()  # Commit the session to save the new plan-zipcode relationship to the database
        print(f"Inserted plan_zipcode record for plan_id {plan_id} and zip_code {zipcode_id}.")
    else:
        # If the relationship already exists, print a message
        print(f"Record for plan_id {plan_id} and zip_code {zipcode_id} already exists.")

def migrate_plans():
    try:
        # Fetch all plans from the 'WellCarePlans' collection in Firestore
        plans_ref = db.collection('WellCarePlans')
        plans = [doc.to_dict() for doc in plans_ref.stream()]
        print(f"Downloaded {len(plans)} plans from Firestore.")

        for plan_data in plans:
            plan_id = insert_plan(plan_data)  # Insert the plan into PostgreSQL and get its ID
            insert_plan_zipcode(plan_id, plan_data['zipCode'])  # Insert the plan-zipcode relationship into PostgreSQL

    except ResourceExhausted as e:
        print(f"Resource exhausted during Firestore read: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        migrate_plans()  # Start the migration process
    except Exception as e:
        print(f"An error occurred during migration: {e}")  # Print any errors that occur during migration
    finally:
        session.close()  # Ensure the session is closed after the migration process
