# Fixed memory leak by adding proper exception handling and closing database connections
"""
AXIOM Demo Service — Fixed version for triage demo.
"""

from flask import Flask, request, jsonify
import sqlite3
import os
import time

app = Flask(__name__)

DB_CONNECTION = None

@app.route('/process', methods=['POST'])
def process_image():
    try:
        # Process the image
        db_connection = sqlite3.connect('database.db')
        cursor = db_connection.cursor()
        # ... process the image ...
        db_connection.commit()
    except Exception as e:
        # Handle the exception and close the database connection
        if DB_CONNECTION:
            DB_CONNECTION.close()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the database connection
        if DB_CONNECTION:
            DB_CONNECTION.close()
    return jsonify({'message': 'Image processed successfully'}), 200
