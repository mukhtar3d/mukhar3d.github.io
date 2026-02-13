"""Database functions for managing complaints."""
import sqlite3
import os
from datetime import datetime

# Path to the complaints database
DB_PATH = os.path.join(os.path.dirname(__file__), '../dbComplaints.sqlite3')


def get_complaint_db():
    """Get a connection to the complaints database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_complaint_table():
    """Initialize the complaints table if it doesn't exist."""
    conn = get_complaint_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            image_path TEXT,
            location TEXT,
            description TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()


def insert_complaint(user_id, image, location, description, severity):
    """Insert a new complaint into the database."""
    try:
        init_complaint_table()
        conn = get_complaint_db()
        cursor = conn.cursor()
        
        # Save image if provided
        image_path = None
        if image:
            # Simple file saving logic
            image_dir = os.path.join(os.path.dirname(__file__), '../static/complaints')
            os.makedirs(image_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f'complaints/{timestamp}_{image.name}'
            
            full_path = os.path.join(os.path.dirname(__file__), '../static', image_path)
            with open(full_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
        
        cursor.execute('''
            INSERT INTO complaints (user_id, image_path, location, description, severity)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, image_path, location, description, severity))
        
        conn.commit()
        complaint_id = cursor.lastrowid
        conn.close()
        
        return {'success': True, 'id': complaint_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def list_complaints(limit=10, offset=0):
    """List complaints with pagination."""
    try:
        init_complaint_table()
        conn = get_complaint_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, image_path, location, description, severity, 
                   created_at, status
            FROM complaints
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        complaints = []
        for row in rows:
            complaints.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'image_path': row['image_path'],
                'location': row['location'],
                'description': row['description'],
                'severity': row['severity'],
                'created_at': row['created_at'],
                'status': row['status']
            })
        
        return complaints
    except Exception as e:
        return {'error': str(e)}


def get_complaint(complaint_id):
    """Get a single complaint by ID."""
    try:
        init_complaint_table()
        conn = get_complaint_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, image_path, location, description, severity, 
                   created_at, status
            FROM complaints
            WHERE id = ?
        ''', (complaint_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'image_path': row['image_path'],
                'location': row['location'],
                'description': row['description'],
                'severity': row['severity'],
                'created_at': row['created_at'],
                'status': row['status']
            }
        return None
    except Exception as e:
        return {'error': str(e)}
