import sqlite3
import os
from config import DATABASE_DIR, WORKSPACE_DIR

def create_databases_and_folders():
    os.makedirs(DATABASE_DIR, exist_ok=True)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)

    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'agent_emails.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (sender TEXT, recipient TEXT, subject TEXT, body TEXT, timestamp TEXT, reply_to TEXT, forward_to TEXT, attachment TEXT)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (sender TEXT, recipients TEXT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'knowledge_base.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'important_info.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS info
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)''')
    conn.commit()
    conn.close()

def load_emails(agent_emails):
    create_databases_and_folders()
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'agent_emails.db'))
    c = conn.cursor()
    c.execute('SELECT * FROM emails ORDER BY timestamp')
    rows = c.fetchall()
    conn.close()

    for row in rows:
        sender, recipient, subject, body, timestamp, reply_to, forward_to, attachment = row
        email_data = {
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "timestamp": timestamp,
            "reply_to": reply_to,
            "forward_to": forward_to,
            "attachment": attachment
        }
        agent_emails.setdefault(recipient, []).append(email_data)

def save_chat_history(chat_history):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    c.executemany("INSERT INTO messages VALUES (?, ?, ?, ?)", [(msg['sender'], ', '.join(msg['recipients']), msg['message'], msg['timestamp']) for msg in chat_history])
    conn.commit()
    conn.close()

def recall_steps():
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    c.execute('SELECT * FROM messages ORDER BY timestamp')
    rows = c.fetchall()
    conn.close()

    for row in rows:
        sender, recipients, message, timestamp = row
        print(f"{timestamp} - {sender} to {recipients}: {message}")

def save_email(sender_email, recipient_names, subject, body, timestamp, reply_to=None, forward_to=None, attachment=None):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'agent_emails.db'))
    c = conn.cursor()
    recipient_emails = [f"{name.lower()}@company.com" for name in recipient_names]
    email_data = [(sender_email, recipient_email, subject, body, timestamp, reply_to, forward_to, attachment) for recipient_email in recipient_emails]
    c.executemany("INSERT INTO emails VALUES (?, ?, ?, ?, ?, ?, ?, ?)", email_data)
    conn.commit()
    conn.close()

def check_email_inbox(agent_name, agent_emails):
    agent_email = f"{agent_name.lower()}@company.com"
    if agent_email in agent_emails:
        print(f"Checking inbox for {agent_name}...")
        for email in agent_emails[agent_email]:
            print(f"From: {email['sender']}\nSubject: {email['subject']}\nBody: {email['body']}\n")
    else:
        print(f"No emails found for {agent_name}.")

def save_knowledge(key, value):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'knowledge_base.db'))
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO knowledge (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_knowledge(key):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'knowledge_base.db'))
    c = conn.cursor()
    c.execute("SELECT value FROM knowledge WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_chat_history(participants=None, limit=None):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    
    if participants:
        query = "SELECT * FROM messages WHERE sender IN ({}) OR recipients LIKE '%{}%' ORDER BY timestamp DESC".format(','.join(['?'] * len(participants)), ','.join(participants))
        c.execute(query, participants)
    else:
        c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    
    rows = c.fetchmany(limit) if limit else c.fetchall()
    conn.close()
    
    chat_history = []
    for row in rows:
        sender, recipients, message, timestamp = row
        chat_history.append({
            "sender": sender,
            "recipients": recipients.split(', '),
            "message": message,
            "timestamp": timestamp
        })
    
    return chat_history

def search_chat_history(keyword):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE message LIKE ? ORDER BY timestamp DESC", (f'%{keyword}%',))
    rows = c.fetchall()
    conn.close()
    
    search_results = []
    for row in rows:
        sender, recipients, message, timestamp = row
        search_results.append({
            "sender": sender,
            "recipients": recipients.split(', '),
            "message": message,
            "timestamp": timestamp
        })
    
    return search_results

def save_important_info(info):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'important_info.db'))
    c = conn.cursor()
    c.execute("INSERT INTO info (content) VALUES (?)", (info,))
    conn.commit()
    conn.close()

def get_important_info():
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'important_info.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM info")
    rows = c.fetchall()
    conn.close()
    
    important_info = [{"id": row[0], "content": row[1]} for row in rows]
    return important_info
