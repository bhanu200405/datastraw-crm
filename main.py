from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Add this import
from pydantic import BaseModel
from database import setup_database
import sqlite3
import uuid
from datetime import datetime

setup_database()

app = FastAPI()

# Add this CORS setup right under app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you'd restrict this, but for now, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Define what information we expect from the user to create a ticket
class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str

# 2. Build the POST endpoint to create a ticket
@app.post("/api/tickets")
def create_ticket(ticket: TicketCreate):
    # Generate a random ticket ID (e.g., TKT-A1B2C3)
    ticket_id = f"TKT-{str(uuid.uuid4())[:6].upper()}"
    
    # Connect to the database
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    try:
        # Execute the INSERT INTO statement
        cursor.execute('''
            INSERT INTO tickets (ticket_id, customer_name, customer_email, subject, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, ticket.customer_name, ticket.customer_email, ticket.subject, ticket.description))
        
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Database error occurred.")
        
    conn.close()
    
    # Return the required format per the assessment
    return {
        "ticket_id": ticket_id,
        "created_at": datetime.now().isoformat()
    }
    
    # ... (your existing create_ticket code is up here) ...

# 3. Build the GET endpoint to list all tickets (with optional search and status filters)
@app.get("/api/tickets")
def get_tickets(status: str = None, search: str = None):
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row # This makes SQLite return dictionaries instead of plain tuples
    cursor = conn.cursor()
    
    # Start our base SELECT query
    query = "SELECT ticket_id, customer_name, subject, status, created_at FROM tickets WHERE 1=1"
    params = []
    
    # Add filters if the user provided them
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND customer_name LIKE ?"
        params.append(f"%{search}%")
        
    cursor.execute(query, params)
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return tickets

# 4. Build the GET endpoint to view a single ticket's details
@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    return dict(ticket)

# ... (your existing get_ticket code is up here) ...

# 5. Define what information we expect when updating a ticket
class TicketUpdate(BaseModel):
    status: str
    notes: str = "" # We'll include this to match the assignment specs

# 6. Build the PUT endpoint to update a ticket
@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, ticket_update: TicketUpdate):
    conn = sqlite3.connect('crm.db')
    cursor = conn.cursor()
    
    # Update the status and the updated_at timestamp
    cursor.execute('''
        UPDATE tickets 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE ticket_id = ?
    ''', (ticket_update.status, ticket_id))
    
    # If the user provided a note, insert it into the notes table (Optional extra feature)
    if ticket_update.notes:
        cursor.execute('''
            INSERT INTO notes (ticket_id, note_text)
            VALUES (?, ?)
        ''', (ticket_id, ticket_update.notes))
        
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    # If no rows were changed, the ticket ID must be wrong
    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    return {
        "success": True,
        "updated_at": datetime.now().isoformat()
    }