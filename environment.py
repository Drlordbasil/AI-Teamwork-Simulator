import sqlite3
import os
import datetime
from config import DATABASE_DIR, WORKSPACE_DIR
import database
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
init()

AGENT_STYLES = {
    'Alice': f"{Fore.CYAN}{Style.BRIGHT}",
    'Bob': f"{Fore.GREEN}{Style.BRIGHT}",
    'Carol': f"{Fore.MAGENTA}{Style.BRIGHT}",
    'David': f"{Fore.YELLOW}{Style.BRIGHT}",
    'Eve': f"{Fore.RED}{Style.BRIGHT}",
    'Frank': f"{Fore.BLUE}{Style.BRIGHT}",
    'System': f"{Fore.WHITE}{Style.BRIGHT}",
    'User': f"{Fore.WHITE}{Style.BRIGHT}"
}

class Environment:
    def __init__(self):
        self.agents = []
        self.agent_emails = {}
        self.chat_history = []
        self.database = database
        self.browser = None

    def load_emails(self):
        database.load_emails(self.agent_emails)

    def add_agent(self, agent):
        self.agents.append(agent)
    
    async def send_message(self, sender, recipient, message):
        for agent in self.agents:
            if agent.name == recipient and agent.location == "office":
                self.print_formatted(recipient, f"{recipient} received a message from {sender}: '{message}'", border_style="-")
                agent.actions.append(f"Received message from {sender}: '{message}'")

        # Store the message in the chat history
        timestamp = datetime.datetime.now().isoformat()
        self.chat_history.append({
            "sender": sender,
            "recipients": [recipient],
            "message": message,
            "timestamp": timestamp
        })
        database.save_chat_history(chat_history=self.chat_history)

    async def broadcast_message(self, sender, recipients, message):
        for recipient in recipients:
            await self.send_message(sender, recipient, message)

    def check_email(self, agent_name):
        email_contents = database.check_email_inbox(agent_name, self.agent_emails)
        return email_contents

    def send_email(self, sender_name, recipient_names, subject, body, reply_to=None, forward_to=None, attachment=None):
        sender_email = f"{sender_name.lower()}@company.com"
        if sender_email not in self.agent_emails:
            raise ValueError(f"Invalid sender email: {sender_email}")

        for recipient_name in recipient_names:
            recipient_email = f"{recipient_name.lower()}@company.com"
            if recipient_email not in self.agent_emails:
                raise ValueError(f"Invalid recipient email: {recipient_email}")

            email = {
                "sender": sender_email,
                "agent_name": sender_name,
                "recipient": recipient_email,
                "subject": subject,
                "body": body,
                "timestamp": datetime.datetime.now().isoformat(),
                "reply_to": reply_to,
                "forward_to": forward_to,
                "attachment": attachment
            }
            self.agent_emails[recipient_email].append(email)
            self.print_formatted(sender_name, f"Email sent from {sender_email} to {recipient_email}: {subject}")

        # Save the email to the database
        database.save_email(sender_email, recipient_names, subject, body, email['timestamp'], reply_to, forward_to, attachment)

    def get_chat_history(self, participants=None, limit=None):
        return database.get_chat_history(participants, limit)

    def search_chat_history(self, keyword):
        return database.search_chat_history(keyword)

    def save_important_info(self, info):
        database.save_important_info(info)

    def get_important_info(self):
        return database.get_important_info()

    def print_formatted(self, agent_name, message, border_style="=", border_length=50):
        agent_style = AGENT_STYLES[agent_name]
        border = border_style * border_length
        print(f"\n{agent_style}{border}{Style.RESET_ALL}")
        print(f"{agent_style}{message}{Style.RESET_ALL}")
        print(f"{agent_style}{border}{Style.RESET_ALL}\n")

    def save_workspace_file(self, file_name, content):
        file_path = os.path.join(WORKSPACE_DIR, file_name)
        with open(file_path, 'w') as file:
            file.write(content)
        self.print_formatted('System', f"File saved to workspace: {file_name}")

    def load_workspace_file(self, file_name):
        file_path = os.path.join(WORKSPACE_DIR, file_name)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.print_formatted('System', f"File loaded from workspace: {file_name}")
            return content
        except FileNotFoundError:
            self.print_formatted('System', f"File not found in workspace: {file_name}")
            return None

    def list_workspace_files(self):
        files = os.listdir(WORKSPACE_DIR)
        self.print_formatted('System', f"Files in workspace: {', '.join(files)}")
        return files

    def open_browser(self):
        if not self.browser:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
            self.browser = webdriver.Chrome(options=chrome_options)
        self.print_formatted('System', "Browser opened.")

    def close_browser(self):
        if self.browser:
            self.browser.quit()
            self.browser = None
        self.print_formatted('System', "Browser closed.")

    def navigate_to_url(self, url):
        if self.browser:
            self.browser.get(url)
            self.print_formatted('System', f"Navigated to URL: {url}")
        else:
            self.print_formatted('System', "No browser instance found. Please open the browser first.")

    def get_browser_content(self):
        if self.browser:
            return self.browser.page_source
        else:
            self.print_formatted('System', "No browser instance found. Please open the browser first.")
            return None

    def edit_file(self, file_name):
        file_path = os.path.join(WORKSPACE_DIR, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            self.print_formatted('System', f"File opened for editing: {file_name}")
            return content
        else:
            self.print_formatted('System', f"File not found in workspace: {file_name}")
            return None

    def save_edited_file(self, file_name, content):
        file_path = os.path.join(WORKSPACE_DIR, file_name)
        with open(file_path, 'w') as file:
            file.write(content)
        self.print_formatted('System', f"Edited file saved: {file_name}")

    def run_python_file(self, file_name):
        file_path = os.path.join(WORKSPACE_DIR, file_name)
        if os.path.exists(file_path):
            try:
                exec(open(file_path).read())
                self.print_formatted('System', f"Python file executed: {file_name}")
            except Exception as e:
                self.print_formatted('System', f"Error occurred while executing Python file: {str(e)}")
        else:
            self.print_formatted('System', f"File not found in workspace: {file_name}")
