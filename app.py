from flask import Flask, request, redirect, render_template_string
import string
import random
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Use Vercel KV for storage
from vercel_kv import VercelKV
kv = VercelKV()

# Generate a random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# HTML template for the main page
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener</title>
</head>
<body>
    <h1>URL Shortener</h1>
    <form method="POST">
        <input type="url" name="url" placeholder="Enter URL to shorten" required>
        <input type="submit" value="Shorten">
    </form>
    {% if short_url %}
    <p>Shortened URL: <a href="{{ short_url }}">{{ short_url }}</a></p>
    {% endif %}
    <h2>Update Existing Short Link</h2>
    <form method="POST" action="/update">
        <input type="text" name="short_code" placeholder="Enter short code" required>
        <input type="url" name="new_url" placeholder="Enter new URL" required>
        <input type="submit" value="Update">
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        long_url = request.form['url']
        short_code = generate_short_code()
        
        kv.set(short_code, long_url)
        
        short_url = request.url_root + short_code
        return render_template_string(HTML_TEMPLATE, short_url=short_url)
    return render_template_string(HTML_TEMPLATE)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    long_url = kv.get(short_code)
    
    if long_url:
        return redirect(long_url)
    else:
        return "Short link not found", 404

@app.route('/update', methods=['POST'])
def update_link():
    short_code = request.form['short_code']
    new_url = request.form['new_url']
    
    if kv.exists(short_code):
        kv.set(short_code, new_url)
        return f"Short link {short_code} updated successfully!", 200
    else:
        return "Short link not found", 404