from flask import Flask, render_template, request, redirect, url_for
from models import Session, Agreement

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('region_view', region_id=1))

@app.route('/region/<int:region_id>')
def region_view(region_id):
    session = Session()
    agreements = session.query(Agreement).filter_by(elomrade_id=region_id).all()
    session.close()
    return render_template("index.html", agreements=agreements, selected_region=region_id)

if __name__ == '__main__':
    app.run(debug=True)
