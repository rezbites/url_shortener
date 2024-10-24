from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from validators import url as validate_url
import string
import random
from datetime import datetime

app = Flask(__name__)

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://shank:rezathome@localhost:3306/url_shortener_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the URL Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(2048), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<URL {self.short_url} -> {self.long_url}>'

# Function to Generate Short URL
def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Home Route
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        long_url = request.form.get('long_url')

        # Validate the URL
        if not validate_url(long_url):
            return render_template("index.html", error="Invalid URL. Please enter a valid URL."), 400

        # Check if the URL already exists
        existing_url = URL.query.filter_by(long_url=long_url).first()
        if existing_url:
            short_url = existing_url.short_url
        else:
            # Generate a unique short URL
            short_url = generate_short_url()
            while URL.query.filter_by(short_url=short_url).first():
                short_url = generate_short_url()

            # Create a new URL entry
            new_url = URL(long_url=long_url, short_url=short_url)
            db.session.add(new_url)
            db.session.commit()

        short_url_full = request.host_url + short_url
        return render_template("index.html", short_url=short_url_full)

    return render_template("index.html")

# Redirect Route
@app.route("/<short_url>")
def redirect_url(short_url):
    url_entry = URL.query.filter_by(short_url=short_url).first()
    if url_entry:
        return redirect(url_entry.long_url)
    else:
        return render_template("404.html"), 404

# Automatic table creation using app context
with app.app_context():
    db.create_all()

# Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
