from bs4 import BeautifulSoup
import json
import requests
import time
import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.exceptions import ResourceExhausted

# Initialize Firebase
cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define the API URLs
api_url = 'https://shop.anthem.com/medicare/accessgateway/getPlanSummary'
token_url = 'https://shop.anthem.com/medicare/accessgateway/generatetoken'

# Function to refresh the auth token
def refresh_auth_token():
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': '',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'shop.anthem.com',
        'Origin': 'https://shop.anthem.com',
        'Content-Length': '32',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
        'Referer': 'https://shop.anthem.com/medicare/quote/view-all-plans-ma?state=NY&brand=ABCBS&role=consumer&locale=en_US',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'senderApp': 'OLS'
    }

    data = '{"input":["test","test","test"]}'
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        try:
            token = response.json().get('token')
            if token:
                return f'Bearer {token}'
            else:
                raise Exception('Token not found in response.')
        except json.JSONDecodeError:
            raise Exception('Failed to parse JSON response for token.')
    else:
        raise Exception(f'Failed to refresh token. Status code: {response.status_code}, Response: {response.text}')

# Initial token fetch
try:
    auth_token = refresh_auth_token()
except Exception as e:
    print(f'Error refreshing token: {e}')
    exit(1)

# Define the headers for the plan summary request
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Authorization': auth_token
}

# Full path to the JSON file
json_file_path = './final_zip_mapping.json'

# Load ZIP codes and details from JSON file
with open(json_file_path) as f:
    zip_details = json.load(f)

all_plans = []
zip_with_plans = [] 
request_counter = 0
zip_counter = 0

def get_plan_summary(payload, headers):
    retries = 3
    for i in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()
            time.sleep(2)
        except requests.exceptions.RequestException:
            time.sleep(2)
    return None

def check_documents_url(brand, plan_id, state_abbreviation):
    documents_url = f'https://shop.anthem.com/medicare/cs/quote/ma-plan-documents?brand={brand}&state={state_abbreviation}&product=MA&planId={plan_id}&reqEffDate=2024-07-01&role=consumer&locale=en_US&year=2024&currentDate=2024-06-17&moduleType=quote'
    try:
        documents_response = requests.get(documents_url)
        documents_soup = BeautifulSoup(documents_response.content, 'lxml')
        for link in documents_soup.find_all('a', class_='title'):
            if 'Evidence of Coverage' in link.get_text():
                return link.get('href')
    except requests.exceptions.RequestException as e:
        pass
    return None

def save_to_firebase(plans, zips):
    max_retries = 5

    def commit_batch(batch):
        for attempt in range(max_retries):
            try:
                batch.commit()
                break
            except ResourceExhausted as e:
                print(f"Resource exhausted, retrying... {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

    # Save plans
    batch_size = 500  # Increased batch size
    for i in range(0, len(plans), batch_size):
        batch = db.batch()
        for plan in plans[i:i + batch_size]:
            doc_ref = db.collection('plans').document(plan['ProductContractCode'])
            batch.set(doc_ref, plan)
        commit_batch(batch)

    # Save zip codes with plans
    for i in range(0, len(zips), batch_size):
        batch = db.batch()
        for zip_code in zips[i:i + batch_size]:
            doc_ref = db.collection('zipcodes').document(zip_code)
            batch.set(doc_ref, {'ZipCode': zip_code})
        commit_batch(batch)

def get_good_zip_codes():
    good_zip_codes = []
    zip_ref = db.collection('zipcodes')
    docs = zip_ref.stream()
    for doc in docs:
        good_zip_codes.append(doc.id)
    return good_zip_codes

# Fetch all ZIP codes that were good
good_zip_codes = get_good_zip_codes()

# Get the list of all ZIP codes and sort them
all_zip_codes = sorted(zip_details.keys())

# Subtract good ZIP codes from all ZIP codes
remaining_zip_codes = [zip_code for zip_code in all_zip_codes if zip_code not in good_zip_codes]

# Process each remaining ZIP code
for zip_code in remaining_zip_codes:
    print(f"Checking ZIP code: {zip_code}")
    zip_counter += 1
    zip_has_plans = False
    
    for fips_code in zip_details[zip_code]["fips_codes"]:
        request_counter += 1
        if request_counter % 1500 == 0:
            try:
                auth_token = refresh_auth_token()
                headers['Authorization'] = auth_token
            except Exception as e:
                print(f"Error refreshing token: {e}")
                time.sleep(5)
                try:
                    auth_token = refresh_auth_token()
                    headers['Authorization'] = auth_token
                except Exception as e:
                    print(f"Failed to refresh token after retry: {e}")
                    continue

        # Update the payload for the current ZIP code and FIPS code
        payload = {
            "planSummaryRequest": {
                "brand": "ANTHEM",
                "productTypes": {
                    "productType": [
                        "MEDICAL",
                        "DRUG"
                    ]
                },
                "marketSegment": "SENIOR",
                "zipCode": zip_code,
                "county": zip_details[zip_code]["county_name"],
                "state": zip_details[zip_code]["state_abbreviation"],
                "coverageTypes": {
                    "coverageType": [
                        "ALL"
                    ]
                },
                "coverageEffectiveDate": "2024-07-01",
                "applicants": {
                    "applicant": [
                        {
                            "applicantType": "PRIMARY",
                            "date_of_birth": "1952-01-01",
                            "gender": "MALE"
                        }
                    ]
                },
                "benefitsRequest": "YES",
                "rateRequest": "YES",
                "countyCode": fips_code,
                "event": "Cart",
                "channel": "OLS"
            }
        }

        data = get_plan_summary(payload, headers)

        if data is None:
            print(f"Skipping ZIP code {zip_code} due to failed plan summary retrieval.")
            continue

        try:
            plans = data['planSummaryResponse']['plans']['plan']
        except KeyError:
            print(f"No plans found for ZIP code {zip_code}.")
            continue

        for plan in plans:
            product_contract_code = plan.get('productContractCode')
            if not product_contract_code or product_contract_code.startswith('S'):
                continue

            rating = plan.get('rating', 'N/A')  # Assuming rating can be missing
            plan_name = plan.get('planDisplayName')
            plan_id = plan.get('planID')

            # Try with brand=ABCBS
            evidence_of_coverage_link = check_documents_url('ABCBS', plan_id, zip_details[zip_code]["state_abbreviation"])
            if not evidence_of_coverage_link:
                # Try with brand=ABC
                evidence_of_coverage_link = check_documents_url('ABC', plan_id, zip_details[zip_code]["state_abbreviation"])

            plan_info = {
                "ProductContractCode": product_contract_code,
                "ZipCode": zip_code,
                "Rating": rating,
                "PlanName": plan_name,
                "PlanID": plan_id,
                "EvidenceOfCoverageURL": evidence_of_coverage_link if evidence_of_coverage_link else "Not found"
            }

            all_plans.append(plan_info)
            zip_has_plans = True

    if zip_has_plans:
        zip_with_plans.append(zip_code)

    # Batch to Firebase every 100 ZIP codes with plans
    if len(zip_with_plans) >= 100:
        save_to_firebase(all_plans, zip_with_plans)
        all_plans = []
        zip_with_plans = []
        print("Save")

# Save any remaining plans and ZIP codes to Firebase
if all_plans or zip_with_plans:
    save_to_firebase(all_plans, zip_with_plans)

print(f"Plan information has been saved to Firebase")


