from flask import Flask, render_template
from models import Session, Agreement

app = Flask(__name__)

@app.route('/')
def index():
    session = Session()
    agreements = session.query(Agreement).all()
    session.close()
    return render_template("index.html", agreements=agreements)

if __name__ == '__main__':
    app.run(debug=True)
