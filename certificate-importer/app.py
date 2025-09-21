import os
import logging
import random
import string
from uuid import uuid4
from datetime import date
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
host = os.getenv("MONGO_HOST")
port = int(os.getenv("MONGO_PORT", 27017))
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")

category_code = os.getenv("CATEGORY_CODE")
category_name = os.getenv("CATEGORY_NAME")
signatures_list = os.getenv("SIGNATURE_IDS", "").split(",")
course = os.getenv("COURSE")
issuer = os.getenv("ISSUER")

csv_input_file = os.getenv("CSV_INPUT_FILE")  
csv_name_col = os.getenv("CSV_NAME_COL")      
csv_email_col = os.getenv("CSV_EMAIL_COL")    
csv_output_file = os.getenv("CSV_OUTPUT_FILE", "certificates_export.csv")  

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

uri = f"mongodb://{username}:{password}@{host}:{port}/"

try:
    client = MongoClient(uri)
    client.server_info()
    logging.info("Connected to MongoDB successfully!")
except Exception as e:
    logging.error(f"Could not connect to MongoDB: {e}")
    exit(1)

db = client[db_name]
collection = db[collection_name]

def generate_credential_id() -> str:
    """Generate a unique credential ID."""
    prefix = random.choice(string.ascii_lowercase)
    raw_uuid = str(uuid4()).replace("-", "")
    credential_id = f"{prefix}{raw_uuid}"
    logging.info(f"Generated credential ID: {credential_id}")
    return credential_id

try:
    df = pd.read_csv(csv_input_file)
    logging.info(f"Read {len(df)} rows from {csv_input_file}")
except Exception as e:
    logging.error(f"Failed to read CSV file: {e}")
    exit(1)

if len(df) == 0:
    logging.warning("No data found in the CSV. Exiting.")
    exit(0)

print(f"Found {len(df)} certificates to insert.")
confirmation = input("Do you want to continue? (y/n): ").strip().lower()
if confirmation != "y":
    logging.info("Operation cancelled by user.")
    exit(0)

export_data = []

for _, row in df.iterrows():
    try:
        name = str(row[csv_name_col]).strip()
        email = str(row[csv_email_col]).strip() if csv_email_col else ""  

        if not name:
            logging.warning(f"Skipping row with missing name: {row}")
            continue

        credential_id = generate_credential_id()

        certificate = {
            "credentialId": credential_id,
            "name": name,
            "course": course,
            "categoryCode": category_code,
            "categoryName": category_name,
            "dateIssued": date.today().isoformat(),
            "issuer": issuer,
            "signatures": signatures_list
        }

        collection.insert_one(certificate)
        logging.info(f"Inserted certificate for {name}")

        export_data.append({"name": name, "email": email, "credentialId": credential_id})

    except Exception as e:
        logging.error(f"Failed to insert certificate for row {row}: {e}")

if export_data:
    try:
        export_df = pd.DataFrame(export_data)
        export_df.to_csv(csv_output_file, index=False)
        logging.info(f"Exported credentials to {csv_output_file}")
    except Exception as e:
        logging.error(f"Failed to export CSV: {e}")
