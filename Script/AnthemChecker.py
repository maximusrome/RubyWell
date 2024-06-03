import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_plans_zip_codes():
    plans_zip_codes = set()
    plans_ref = db.collection('plans')
    docs = plans_ref.stream()
    for doc in docs:
        zip_code = doc.to_dict().get('ZipCode')
        if zip_code:
            plans_zip_codes.add(zip_code)
    return plans_zip_codes

def get_existing_zip_codes():
    existing_zip_codes = set()
    zip_ref = db.collection('zipcodes_with_plans')
    docs = zip_ref.stream()
    for doc in docs:
        existing_zip_codes.add(doc.id)
    return existing_zip_codes

def populate_zipcodes2(new_zip_codes):
    batch_size = 500
    new_zip_codes_list = list(new_zip_codes)
    for i in range(0, len(new_zip_codes_list), batch_size):
        batch = db.batch()
        for zip_code in new_zip_codes_list[i:i + batch_size]:
            doc_ref = db.collection('zipcodes_with_plans').document(zip_code)
            batch.set(doc_ref, {'ZipCode': zip_code})
        batch.commit()
        print(f"Batch {i // batch_size + 1} committed.")

# Get all ZIP codes from the plans collection
plans_zip_codes = get_plans_zip_codes()

# Get existing ZIP codes in zipcodes2 collection
existing_zip_codes = get_existing_zip_codes()

# Determine new ZIP codes to add (no overlap)
new_zip_codes = plans_zip_codes - existing_zip_codes

# Populate the new zipcodes2 collection with the new ZIP codes
populate_zipcodes2(new_zip_codes)

print(f"zipcodes_with_plans collection has been populated with {len(new_zip_codes)} new ZIP codes.")
