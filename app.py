from flask import Flask, render_template, jsonify
from models import init_db, get_all_agreements

app = Flask(__name__)

@app.route("/")
def home():
    data = get_all_agreements()
    return render_template("index.html", data=data)

@app.route("/api/data")
def api_data():
    return jsonify(get_all_agreements())

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
