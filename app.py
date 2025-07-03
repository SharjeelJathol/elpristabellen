from flask import Flask, render_template, request
from models import Session, Agreement

app = Flask(__name__)

@app.route('/')
def index():
    session = Session()
    query = session.query(Agreement)

    # Get filters from URL query parameters
    company_filter = request.args.get('company', type=str)
    elomrade_filter = request.args.get('elomrade_id', type=int)
    postnummer_filter = request.args.get('postnummer', type=str)
    contract_type = request.args.get('contract_type', type=str)

    # Filter by company name (case-insensitive contains)
    if company_filter:
        query = query.filter(Agreement.company.ilike(f"%{company_filter}%"))

    # Filter by ElområdeId
    if elomrade_filter:
        query = query.filter(Agreement.elomrade_id == elomrade_filter)

    # Filter by Postnummer (exact match)
    if postnummer_filter:
        query = query.filter(Agreement.postnummer == postnummer_filter)

    # Filter by contract type with price > 0
    if contract_type:
        # Map contract type to column names
        contract_map = {
            "rorligt": Agreement.rorligt_price,
            "fast_3m": Agreement.price_fast_3m,
            "fast_6m": Agreement.price_fast_6m,
            "fast_1y": Agreement.price_fast_1y,
            "fast_2y": Agreement.price_fast_2y,
            "fast_3y": Agreement.price_fast_3y,
            "fast_4y": Agreement.price_fast_4y,
            "fast_5y": Agreement.price_fast_5y,
            "fast_10y": Agreement.price_fast_10y,
            "hourly": Agreement.timpris_price
        }
        col = contract_map.get(contract_type.lower())
        if col is not None:
            query = query.filter(col.isnot(None))

    agreements = query.all()
    session.close()
    return render_template("index.html", agreements=agreements, filters=request.args)

if __name__ == '__main__':
    app.run(debug=True)
