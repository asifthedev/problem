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

# HTML template for the main page with modern CSS
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --background: #f0f0f0;
            --text: #333;
            --primary: #3498db;
            --secondary: #2ecc71;
            --accent: #e74c3c;
        }
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--background);
            background-image: radial-gradient(circle, #222222 1px, var(--background) 1px);
            background-size: 20px 20px;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background-color: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
        h1, h2 {
            color: var(--primary);
            margin-bottom: 1rem;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        input {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }
        input[type="submit"] {
            background-color: var(--secondary);
            color: white;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        input[type="submit"]:hover {
            background-color: #27ae60;
        }
        .result {
            background-color: #e8f4fd;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        .error {
            color: var(--accent);
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>URL Shortener</h1>
        <form method="POST">
            <input type="url" name="url" placeholder="Enter URL to shorten" required>
            <input type="submit" value="Shorten">
        </form>
        {% if short_url %}
        <div class="result">
            <p>Shortened URL: <a href="{{ short_url }}">{{ short_url }}</a></p>
        </div>
        {% endif %}
        {% if error %}
        <p class="error">Error: {{ error }}</p>
        {% endif %}
        <h2>Update Existing Short Link</h2>
        <form method="POST" action="/update">
            <input type="text" name="short_code" placeholder="Enter short code" required>
            <input type="url" name="new_url" placeholder="Enter new URL" required>
            <input type="submit" value="Update">
        </form>
    </div>
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
            
            short_url = f"https://asifshort-itman.vercel.app/{short_code}"
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
