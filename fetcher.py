import requests
from models import Session, Agreement

BASE_URL = "https://www.elmarknad.se/api/agreement/filter"
PAGINATION_URL = "https://www.elmarknad.se/api/agreement/paginationfilter"

CONTRACT_TYPES = ["Monthly", "Hourly", "Fast"]

REGIONS = [
    {"ElområdeId": 1, "Postnummer": 97231},
    {"ElområdeId": 2, "Postnummer": 85102},
    {"ElområdeId": 3, "Postnummer": 11120},
    {"ElområdeId": 4, "Postnummer": 21119},
]

PARAMS_TEMPLATE = {
    "Postnummer": None,
    "Typ": None,
    "ElområdeId": None,
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
    "Company": "",
}

def fetch_all_agreements():
    session = Session()
    for contract_type in CONTRACT_TYPES:
        for region in REGIONS:
            print(f"\nFetching contract type: {contract_type} for region ElområdeId={region['ElområdeId']} Postnummer={region['Postnummer']}")
            
            params = PARAMS_TEMPLATE.copy()
            params["Typ"] = contract_type
            params["ElområdeId"] = region["ElområdeId"]
            params["Postnummer"] = region["Postnummer"]
            
            try:
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to fetch main page: {e}")
                continue
            
            data = response.json()
            total = data.get("AgreementsCount", 0)
            agreements = data.get("SearchResultViewModels", [])
            print(f"Total agreements: {total}, initially fetched: {len(agreements)}")

            batch_size = 5
            for skip in range(batch_size, total, batch_size):
                pag_params = params.copy()
                pag_params["Skip"] = skip
                
                try:
                    pag_response = requests.get(PAGINATION_URL, params=pag_params)
                    pag_response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Failed to fetch page with skip={skip}: {e}")
                    continue
                
                pag_data = pag_response.json()
                batch = pag_data.get("SearchResultViewModels", [])
                print(f"Fetched {len(batch)} agreements at skip={skip}")
                agreements.extend(batch)

            for ag in agreements:
                company = ag.get("Company", "Unknown")
                price = ag.get("Price")
                if price is not None:
                    try:
                        price = float(price)
                    except:
                        price = None

                # Create or update existing agreement for same company, type, region, postcode
                existing = session.query(Agreement).filter_by(
                    company=company,
                    contract_type=contract_type,
                    elomrade_id=region["ElområdeId"],
                    postnummer=region["Postnummer"],
                ).first()

                if existing:
                    existing.price = price
                else:
                    new_agreement = Agreement(
                        company=company,
                        contract_type=contract_type,
                        price=price,
                        elomrade_id=region["ElområdeId"],
                        postnummer=region["Postnummer"],
                    )
                    session.add(new_agreement)

                print(f"Saved: [{contract_type}] {company} | Price: {price}")

            session.commit()
    session.close()

if __name__ == "__main__":
    fetch_all_agreements()
