from flask import Flask, request, redirect, render_template_string
import string
import random
import os
from dotenv import load_dotenv
import logging

app = Flask(__name__)

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# In-memory storage (Note: This will reset on each function invocation)
url_storage = {}

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
    {% if error %}
    <p style="color: red;">Error: {{ error }}</p>
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
    error = None
    short_url = None
    if request.method == 'POST':
        try:
            long_url = request.form['url']
            short_code = generate_short_code()
            
            url_storage[short_code] = long_url
            
            short_url = f"https://problem-7kwxyny1o-asifthedevs-projects.vercel.app/{short_code}"
        except Exception as e:
            logging.error(f"Error in home route: {str(e)}")
            error = "An error occurred while shortening the URL. Please try again."
    
    return render_template_string(HTML_TEMPLATE, short_url=short_url, error=error)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    try:
        long_url = url_storage.get(short_code)
        
        if long_url:
            return redirect(long_url)
        else:
            return "Short link not found", 404
    except Exception as e:
        logging.error(f"Error in redirect route: {str(e)}")
        return "An error occurred", 500

@app.route('/update', methods=['POST'])
def update_link():
    try:
        short_code = request.form['short_code']
        new_url = request.form['new_url']
        
        if short_code in url_storage:
            url_storage[short_code] = new_url
            return f"Short link {short_code} updated successfully!", 200
        else:
            return "Short link not found", 404
    except Exception as e:
        logging.error(f"Error in update route: {str(e)}")
        return "An error occurred", 500

@app.route('/debug')
def debug():
    return "Debug route is working!", 200
