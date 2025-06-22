# app.py
import requests
from db import init_db, SessionLocal
from models import Agreement

BASE_URL = "https://www.elmarknad.se/api/agreement/filter"
PAGINATION_URL = "https://www.elmarknad.se/api/agreement/paginationfilter"

CONTRACT_TYPES = ["Monthly", "Hourly", "Fast"]

PARAMS_TEMPLATE = {
    "Postnummer": 97231,
    "Typ": "",
    "ElområdeId": 1,
    "Förbrukning": 3750,
    "PaymentMethod": "E",
    "Property": "cabin",
    "IsEnvironmentFriendly": "false",
    "CampaignAgreements": "all",
    "IsCertifiedCompany": "false",
    "HasMobile": "false",
    "HasCreditScore": "false",
    "HasBlacklist": "false",
    "DealTime": "all",
    "ShowBest": "true",
    "Company": ""
}

def fetch_all_agreements():
    init_db()
    db = SessionLocal()

    for contract_type in CONTRACT_TYPES:
        print(f"\nFetching contract type: {contract_type}")
        params = PARAMS_TEMPLATE.copy()
        params["Typ"] = contract_type

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        total = data.get("AgreementsCount", 0)
        agreements = data.get("SearchResultViewModels", [])
        print(f"Total agreements for {contract_type}: {total}")
        print(f"Fetched {len(agreements)} agreements for {contract_type}")

        batch_size = 5
        for skip in range(batch_size, total, batch_size):
            pag_params = params.copy()
            pag_params["Skip"] = skip
            pag_response = requests.get(PAGINATION_URL, params=pag_params)
            pag_response.raise_for_status()
            pag_data = pag_response.json()
            batch = pag_data.get("SearchResultViewModels", [])
            print(f"Fetched {len(batch)} agreements for {contract_type}, skip={skip}")
            agreements.extend(batch)

        for ag in agreements:
            company = ag.get("Company", "Unknown")
            price = ag.get("Price", 0.0)
            print(f"[{contract_type}] Company: {company} | Price: {price}")

            agreement = Agreement(
                company=company,
                contract_type=contract_type,
                price=float(price)
            )
            db.add(agreement)

    db.commit()
    db.close()
    print("✅ All data saved to database.")

if __name__ == "__main__":
    fetch_all_agreements()
