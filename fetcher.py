import requests
from models import Session, Agreement

BASE_URL = "https://www.elmarknad.se/api/agreement/filter"
PAGINATION_URL = "https://www.elmarknad.se/api/agreement/paginationfilter"

CONTRACT_TYPE_TO_COLUMN = {
    "Monthly": "price_monthly",
    # "Hourly": "price_hourly",
    "Fast": "price_fast"
}

REGIONS = [
    {"ElområdeId": 1, "Postnummer": 97231},
    # {"ElområdeId": 2, "Postnummer": 85102},
    # {"ElområdeId": 3, "Postnummer": 11120},
    # {"ElområdeId": 4, "Postnummer": 21119},
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

def map_avtalstid_to_column(avtalstid: str):
    avtalstid = avtalstid.lower()
    if "3 mån" in avtalstid:
        return "price_fast_3m"
    elif "6 mån" in avtalstid:
        return "price_fast_6m"
    elif "1 år" in avtalstid or "12 mån" in avtalstid:
        return "price_fast_1y"
    elif "2 år" in avtalstid:
        return "price_fast_2y"
    elif "3 år" in avtalstid:
        return "price_fast_3y"
    elif "4 år" in avtalstid:
        return "price_fast_4y"
    elif "5 år" in avtalstid:
        return "price_fast_5y"
    elif "10 år" in avtalstid:
        return "price_fast_10y"
    return None

def fetch_all_agreements():
    session = Session()

    for contract_type, base_column in CONTRACT_TYPE_TO_COLUMN.items():
        for region in REGIONS:
            print(f"\nFetching {contract_type} contracts for ElområdeId={region['ElområdeId']}, Postnummer={region['Postnummer']}")

            params = PARAMS_TEMPLATE.copy()
            params["Typ"] = contract_type
            params["ElområdeId"] = region["ElområdeId"]
            params["Postnummer"] = region["Postnummer"]

            try:
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Main request failed: {e}")
                continue

            data = response.json()
            total = data.get("AgreementsCount", 0)
            agreements = data.get("SearchResultViewModels", [])

            # Pagination
            for skip in range(5, total, 5):
                pag_params = params.copy()
                pag_params["Skip"] = skip
                try:
                    pag_response = requests.get(PAGINATION_URL, params=pag_params)
                    pag_response.raise_for_status()
                except requests.RequestException as e:
                    print(f"Pagination request failed at skip={skip}: {e}")
                    continue

                pag_data = pag_response.json()
                agreements.extend(pag_data.get("SearchResultViewModels", []))

            for ag in agreements:
                company = ag.get("Company", "Unknown")
                price = ag.get("Price")

                if price is not None:
                    try:
                        price = float(price)
                    except:
                        price = None

                db_ag = session.query(Agreement).filter_by(
                    company=company,
                    elomrade_id=region["ElområdeId"],
                    postnummer=region["Postnummer"]
                ).first()

                if not db_ag:
                    db_ag = Agreement(
                        company=company,
                        elomrade_id=region["ElområdeId"],
                        postnummer=region["Postnummer"]
                    )

                # Store base contract price
                setattr(db_ag, base_column, price)

                # For Fast contracts, map Avtalstid
                if contract_type == "Fast":
                    avtalstid = ag.get("Avtalstid", "")

                    yearly_price = ag.get("YearlyPrice")
                    taxes = ag.get("Taxes")
                    # Convert to float
                    try:
                        yearly_price = float(yearly_price)
                    except:
                        yearly_price = None

                    try:
                        taxes = float(taxes)
                    except:
                        taxes = None
                    db_ag.price_fast_monthly_fee = yearly_price
                    db_ag.price_fast_vat = taxes

                    avtalstid_column = map_avtalstid_to_column(avtalstid)
                    if avtalstid_column:
                        setattr(db_ag, avtalstid_column, price)
                        print(f"→ [{contract_type}] {company} | {avtalstid_column} = {price}")
                    else:
                        print(f"→ [{contract_type}] {company} | Unrecognized Avtalstid: {avtalstid}")
                elif contract_type == "Monthly":
                    extra_fee = ag.get("ExtraFee")
                    taxes = ag.get("Taxes")

                    try:
                        extra_fee = float(extra_fee)
                    except:
                        extra_fee = None

                    try:
                        taxes = float(taxes)
                    except:
                        taxes = None

                    db_ag.rorligt_spotpaslag = extra_fee
                    db_ag.monthly_vat = taxes
                    db_ag.rorligt_price = price

                    print(f"→ [Monthly] {company} | Price={price}, Spotpåslag={extra_fee}, VAT={taxes}")

                else:
                    print(f"→ [{contract_type}] {company} = {price}")

                session.add(db_ag)

            session.commit()
    session.close()

if __name__ == "__main__":
    fetch_all_agreements()
