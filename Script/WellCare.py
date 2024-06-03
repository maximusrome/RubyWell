import requests
from bs4 import BeautifulSoup
import json
import time
import firebase_admin
from firebase_admin import credentials, firestore
from urllib.parse import urlencode, urljoin

# Initialize Firebase
cred = credentials.Certificate('./wellCareKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to fetch a new cookie
def fetch_new_cookie():
    session = requests.Session()
    session.get('https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Quote/GetQuotePartial')
    return session.cookies.get_dict()

# Function to fetch request verification token
def fetch_request_verification_token(cookie):
    headers = {
        'Accept': 'text/html',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie
    }
    response = requests.get('https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Quote/GetQuotePartial', headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
    return token

# Initialize cookie and token
cookie_dict = fetch_new_cookie()
cookie = '; '.join([f'{key}={value}' for key, value in cookie_dict.items()])
token = fetch_request_verification_token(cookie)

# Function to get plan data
def get_plan_data(zip_code, county_name, state_abbreviation, fips_code):
    global cookie, token  # Make sure to use the updated cookie and token
    state_fips_code = fips_code[:2]

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie
    }

    payload = {
        'quote.Location.Zip': zip_code,
        'quote.Location.County': county_name,
        'quote.Location.State': state_abbreviation,
        'quote.Location.CountyFipsCode': fips_code,
        'quote.Location.StateFipsCode': state_fips_code,
        '__RequestVerificationToken': token
    }

    response = requests.post('https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Quote/GetQuotePartial', headers=headers, data=urlencode(payload))
    
    # Refresh token and cookie if needed
    if response.status_code == 403:  # Forbidden, possibly due to expired token
        cookie_dict = fetch_new_cookie()
        cookie = '; '.join([f'{key}={value}' for key, value in cookie_dict.items()])
        token = fetch_request_verification_token(cookie)
        headers['Cookie'] = cookie
        payload['__RequestVerificationToken'] = token
        response = requests.post('https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Quote/GetQuotePartial', headers=headers, data=urlencode(payload))

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tags = soup.find_all('script')
    plans_json_string = None

    for script in script_tags:
        if script.string and 'var plans =' in script.string:
            plans_json_string = script.string.split('var plans = ')[1].split(';')[0]

    if not plans_json_string:
        print(f"No plans data found in response for Zip Code: {zip_code}")
        return []

    plans = json.loads(plans_json_string)
    plan_elements = soup.select('.list-col')
    plan_details = [{'name': el.find('h3').text.strip(), 'contractId': el.select_one('.section-block p').text.strip()} for el in plan_elements]

    if not plan_details:
        print(f"No plan details found in response for Zip Code: {zip_code}")
        return []

    plan_data = [
        {
            'productContractCode': f"{plan['Contract']}-{plan['PbpId']}-{plan['SegmentId']}",
            'zipCode': zip_code,
            'rating': None if plan['StarRating'] == 0 else plan['StarRating'],
            'planName': detail['name'],
            'planID': plan['PlanId']
        }
        for detail in plan_details
        for plan in plans
        if f"{plan['Contract']}-{plan['PbpId']}" == detail['contractId']
    ]

    if not plan_data:
        print(f"No matching plans found for Zip Code: {zip_code}")
        return []

    for plan in plan_data:
        try:
            detail_response = requests.get(f"https://wellcare.isf.io/2024/g/f010acf28d0e468cb2aa59e0e68d694b/Plan/Index?PlanId={plan['planID']}", headers=headers)
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
            evidence_link_element = next((a for a in detail_soup.find_all('a') if 'Evidence of Coverage' in a.text), None)
            if evidence_link_element:
                evidence_link = evidence_link_element['href']
                plan['evidenceOfCoverageLink'] = evidence_link if evidence_link.startswith('http') else urljoin('https://wellcare.isf.io', evidence_link)
            else:
                plan['evidenceOfCoverageLink'] = None
        except Exception as detail_error:
            print(f"Error fetching plan details for PlanID {plan['planID']}: {detail_error}")
            plan['evidenceOfCoverageLink'] = None

    return plan_data

# Function to save data to Firebase
def save_to_firebase(plans):
    max_retries = 5

    def commit_batch(batch):
        for attempt in range(max_retries):
            try:
                batch.commit()
                break
            except Exception as e:
                print(f"Resource exhausted, retrying... {e}")
                time.sleep(2 ** attempt)

    batch_size = 500  # Increased batch size to reduce the number of writes

    plans_collection = db.collection('WellCarePlans')
    for i in range(0, len(plans), batch_size):
        batch = db.batch()
        plan_chunk = plans[i:i + batch_size]
        for plan in plan_chunk:
            plan_ref = plans_collection.document(f"{plan['productContractCode']}-{plan['zipCode']}")
            batch.set(plan_ref, plan)
        commit_batch(batch)
        print(f"Saved {len(plan_chunk)} plans to Firebase.")

def main(start_zip_code=None):
    try:
        with open('./final_zip_mapping.json', 'r') as f:
            zip_mapping = json.load(f)
        all_plans = {}

        sorted_zip_codes = sorted(zip_mapping.keys(), key=lambda x: (len(x), x))

        if start_zip_code:
            if start_zip_code in sorted_zip_codes:
                start_index = sorted_zip_codes.index(start_zip_code)
                sorted_zip_codes = sorted_zip_codes[start_index:]
            else:
                print(f"Start ZIP code {start_zip_code} not found in the ZIP code mapping.")
                return

        for zip_code in sorted_zip_codes:
            print(f"Checking ZIP code: {zip_code}")

            county_name = zip_mapping[zip_code]['county_name']
            state_abbreviation = zip_mapping[zip_code]['state_abbreviation']
            fips_codes = zip_mapping[zip_code]['fips_codes']

            for fips_code in fips_codes:
                plans = get_plan_data(zip_code, county_name, state_abbreviation, fips_code)

                if plans:
                    for plan in plans:
                        all_plans[f"{plan['productContractCode']}-{plan['zipCode']}"] = plan

                if len(all_plans) >= 100:
                    save_to_firebase(list(all_plans.values()))
                    all_plans.clear()

        if all_plans:
            save_to_firebase(list(all_plans.values()))

        print('Plan information has been saved to Firebase')
    except Exception as error:
        print('Error:', error)

if __name__ == "__main__":
    start_zip = "15455"  # Specify the starting ZIP code here
    main(start_zip_code=start_zip)
