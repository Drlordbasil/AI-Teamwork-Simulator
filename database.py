import sqlite3
import os
from config import DATABASE_DIR

def create_databases():
    # Create agent_emails database
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'agent_emails.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (sender TEXT, recipient TEXT, subject TEXT, body TEXT, timestamp TEXT, reply_to TEXT, forward_to TEXT, attachment TEXT)''')
    conn.commit()
    conn.close()

    # Create chat_history database
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (sender TEXT, recipients TEXT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

    # Create knowledge_base database
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'knowledge_base.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge
                 (key TEXT, value TEXT)''')
    conn.commit()
    conn.close()

    # Create important_info database
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'important_info.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS info
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)''')
    conn.commit()
    conn.close()

def load_emails(agent_emails):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'agent_emails.db'))
    c = conn.cursor()
    for row in c.execute('SELECT * FROM emails ORDER BY timestamp'):
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
        if recipient not in agent_emails:
            agent_emails[recipient] = []
        agent_emails[recipient].append(email_data)
    conn.close()

def save_chat_history(chat_history):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    for message in chat_history:
        # Flatten the list of recipients
        recipients = [recipient for sublist in message['recipients'] for recipient in sublist]
        c.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (message['sender'], ', '.join(recipients), message['message'], message['timestamp']))
    conn.commit()
    conn.close()

def recall_steps():
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    for row in c.execute('SELECT * FROM messages ORDER BY timestamp'):
        sender, recipients, message, timestamp = row
        print(f"{timestamp} - {sender} to {recipients}: {message}")
    conn.close()

def save_email(sender_email, recipient_names, subject, body, timestamp, reply_to=None, forward_to=None, attachment=None):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'agent_emails.db'))
    c = conn.cursor()
    for recipient_name in recipient_names:
        recipient_email = f"{recipient_name.lower()}@company.com"
        c.execute("INSERT INTO emails VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (sender_email, recipient_email, subject, body, timestamp, reply_to, forward_to, attachment))
    conn.commit()
    conn.close()

def check_email_inbox(agent_name, agent_emails):
    if agent_name in agent_emails:
        print(f"Checking inbox for {agent_name}...")
        for email in agent_emails[agent_name]:
            print(f"From: {email['sender']}\nSubject: {email['subject']}\nBody: {email['body']}\n")
    else:
        print(f"No emails found for {agent_name}.")

def save_knowledge(key, value):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'knowledge_base.db'))
    c = conn.cursor()
    c.execute("INSERT INTO knowledge VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_chat_history(participants=None, limit=None):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    if participants:
        query = "SELECT * FROM messages WHERE sender IN ({}) OR recipients LIKE '%{}%' ORDER BY timestamp DESC".format(','.join(['?'] * len(participants)), ','.join(participants))
        c.execute(query, participants)
    else:
        c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    
    if limit:
        rows = c.fetchmany(limit)
    else:
        rows = c.fetchall()
    
    chat_history = []
    for row in rows:
        sender, recipients, message, timestamp = row
        chat_history.append({
            "sender": sender,
            "recipients": recipients.split(', '),
            "message": message,
            "timestamp": timestamp
        })
    
    conn.close()
    return chat_history

def search_chat_history(keyword):
    conn = sqlite3.connect(os.path.join(DATABASE_DIR, 'chat_history.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE message LIKE ? ORDER BY timestamp DESC", (f'%{keyword}%',))
    rows = c.fetchall()
    
    search_results = []
    for row in rows:
        sender, recipients, message, timestamp = row
        search_results.append({
            "sender": sender,
            "recipients": recipients.split(', '),
            "message": message,
            "timestamp": timestamp
        })
    
    conn.close()
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
    
    important_info = []
    for row in rows:
        info_id, content = row
        important_info.append({
            "id": info_id,
            "content": content
        })
    
    conn.close()
    return important_info
