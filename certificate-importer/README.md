# Mass Certificate Insertion Script

This Python script allows you to **mass-insert certificates into a MongoDB database** from a CSV file and **export the certificate information** (name, email, and generated credential ID) to a CSV file.

## Requirements

Install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Dependencies include:**

* `pandas`
* `python-dotenv`
* `pymongo`

## Setup

### 1. Prepare `.env` file

Create a `.env` file in the project directory. Example:

```dotenv
# -------------------- MongoDB Configuration --------------------
MONGO_USERNAME=admin
MONGO_PASSWORD=secret
MONGO_HOST=localhost
MONGO_PORT=27017
DB_NAME=certify
COLLECTION_NAME=certificates

# -------------------- Certificate Details --------------------
CATEGORY_CODE=LC
CATEGORY_NAME=Leadership & Contribution
SIGNATURE_IDS=pmvodpn5,szoii2l2
COURSE=Club Member
ISSUER=Mozilla Campus Club SLIIT

# -------------------- CSV Configuration --------------------
CSV_INPUT_FILE=participants.csv      # Input CSV file with participant data
CSV_NAME_COL=name                    # Column in CSV containing participant names
CSV_EMAIL_COL=email                  # Column in CSV containing participant emails 
CSV_OUTPUT_FILE=certificates_export.csv  # CSV file to export name, email, and credentialId
```

**Notes:**

* CSV can have **any number of columns**, as long as you correctly specify the `name` and `email` columns inside ```.env``` file.

## Usage

Run the script:

```bash
python app.py
```

1. The script will **read the CSV** and display how many certificates will be inserted.
2. You will be asked to **confirm** before inserting:

```
Found 10 certificates to insert.
Do you want to continue? (y/n):
```

3. Certificates are **inserted into MongoDB**, and logs are displayed for each insertion.
4. After completion, an **export CSV** is generated containing:

| name         | email                                         | credentialId    |
| ------------ | --------------------------------------------- | --------------- |
| Saman Silva  | [saman@example.com](mailto:saman@example.com) | a9b7c8d6e5f4... |
| Nimal Perera | [nimal@example.com](mailto:nimal@example.com) | b8c7d6e5f4a3... |

