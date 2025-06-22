import requests
from models import Agreement, Session
from datetime import datetime

def fetch_and_store():
    url = "https://www.elmarknad.se/api/agreement/filter?Postnummer=21119&Typ=Rörligt&ElområdeId=4&Förbrukning=3750&PaymentMethod=E&Property=cabin&IsEnvironmentFriendly=false&CampaignAgreements=all&IsCertifiedCompany=false&HasMobile=false&HasCreditScore=false&HasBlacklist=false&DealTime=all&ShowBest=true&Company="
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        agreements = data.get("SearchResultViewModels", [])
        session = Session()

        for item in agreements:
            agreement = Agreement(
                id = item.get("Id"),
                company = item.get("Company"),
                price = float(item.get("Price", 0)),
                contract = item.get("Contract", ""),
                avtalstid = item.get("Avtalstid", ""),
                monthly_price = float(item.get("MonthlyPrice") or 0),
                dynamic_purchase_fee = float(item.get("DynamicPurchaseFee") or 0),
                taxes = float(item.get("Taxes") or 0),
                fetched_at = datetime.utcnow()
            )
            session.merge(agreement)  # Insert or update based on primary key
        session.commit()
        session.close()
        print(f"✅ Stored {len(agreements)} agreements at {datetime.utcnow()}")
    else:
        print("❌ API fetch failed:", response.status_code)

if __name__ == "__main__":
    fetch_and_store()
