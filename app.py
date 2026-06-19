import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from rop_scanner import check_rop_availability

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        origin = request.form.get('origin', 'BKK').upper()
        destination = request.form.get('destination', 'FRA').upper()
        departure_date = request.form.get('departure_date', '')
        cabin_class = request.form.get('cabin_class', 'Business')
        
        # Call the scanner function
        flights = check_rop_availability(origin, destination, departure_date, cabin_class)
        
        # Check if session is expired or error occurred
        if flights is None:
            error_message = "Session Expired or API Error. Please update the .env file with a fresh session."
            return render_template('index.html', error=error_message)
            
        return render_template('index.html', flights=flights, origin=origin, destination=destination, date=departure_date, cabin=cabin_class)
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
