import os
import datetime
from config import DATABASE_DIR, WORKSPACE_DIR
import database
from colorama import init, Fore, Style
import requests
from bs4 import BeautifulSoup
from skills import scrape_webpage

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
        self.workspaces = {}

    def load_emails(self):
        database.load_emails(self.agent_emails)

    def add_agent(self, agent):
        self.agents.append(agent)
        self.workspaces[agent.name] = os.path.join(WORKSPACE_DIR, agent.name)
        os.makedirs(self.workspaces[agent.name], exist_ok=True)

    async def send_message(self, sender, recipient, message):
        for agent in self.agents:
            if agent.name == recipient:
                self.print_formatted(recipient, f"{recipient} received a message from {sender}: '{message}'", border_style="▃▃▃")
                agent.actions.append(f"Received message from {sender}: '{message}'")

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

        database.save_email(sender_email, recipient_names, subject, body, email['timestamp'], reply_to, forward_to, attachment)

    def get_chat_history(self, participants=None, limit=None):
        return database.get_chat_history(participants, limit)

    def search_chat_history(self, keyword):
        return database.search_chat_history(keyword)

    def save_important_info(self, info):
        database.save_important_info(info)

    def get_important_info(self):
        return database.get_important_info()

    def print_formatted(self, agent_name, message, border_style="▃▃▃", border_length=50):
        agent_style = AGENT_STYLES[agent_name]
        border = border_style * border_length
        print(f"\n{agent_style}{border}{Style.RESET_ALL}")
        print(f"{agent_style}{message}{Style.RESET_ALL}")
        print(f"{agent_style}{border}{Style.RESET_ALL}\n")

    def create_file(self, agent_name, file_name, content):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        with open(file_path, 'w') as file:
            file.write(content)
        self.print_formatted('System', f"{agent_name} created file: {file_name}")

    def read_file(self, agent_name, file_name):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.print_formatted('System', f"{agent_name} read file: {file_name}")
            return content
        except FileNotFoundError:
            self.print_formatted('System', f"File not found in {agent_name}'s workspace: {file_name}")
            return None

    def update_file(self, agent_name, file_name, content):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            self.print_formatted('System', f"{agent_name} updated file: {file_name}")
        except FileNotFoundError:
            self.print_formatted('System', f"File not found in {agent_name}'s workspace: {file_name}")

    def delete_file(self, agent_name, file_name):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        try:
            os.remove(file_path)
            self.print_formatted('System', f"{agent_name} deleted file: {file_name}")
        except FileNotFoundError:
            self.print_formatted('System', f"File not found in {agent_name}'s workspace: {file_name}")

    def create_folder(self, agent_name, folder_name):
        workspace_path = self.workspaces[agent_name]
        folder_path = os.path.join(workspace_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        self.print_formatted('System', f"{agent_name} created folder: {folder_name}")

    def list_folder_contents(self, agent_name, folder_name):
        workspace_path = self.workspaces[agent_name]
        folder_path = os.path.join(workspace_path, folder_name)
        try:
            contents = os.listdir(folder_path)
            self.print_formatted('System', f"Contents of {agent_name}'s folder '{folder_name}': {', '.join(contents)}")
            return contents
        except FileNotFoundError:
            self.print_formatted('System', f"Folder not found in {agent_name}'s workspace: {folder_name}")
            return None

    def scrape_webpage(self, url):
        return scrape_webpage(url)

    def save_workspace_file(self, agent_name, file_name, content):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        with open(file_path, 'w') as file:
            file.write(content)
        self.print_formatted('System', f"{agent_name} saved file to workspace: {file_name}")

    def load_workspace_file(self, agent_name, file_name):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.print_formatted('System', f"{agent_name} loaded file from workspace: {file_name}")
            return content
        except FileNotFoundError:
            self.print_formatted('System', f"File not found in {agent_name}'s workspace: {file_name}")
            return None

    def list_workspace_files(self, agent_name):
        workspace_path = self.workspaces[agent_name]
        files = os.listdir(workspace_path)
        self.print_formatted('System', f"Files in {agent_name}'s workspace: {', '.join(files)}")
        return files

    def edit_workspace_file(self, agent_name, file_name):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            self.print_formatted('System', f"{agent_name} opened file for editing: {file_name}")
            return content
        else:
            self.print_formatted('System', f"File not found in {agent_name}'s workspace: {file_name}")
            return None

    def save_edited_workspace_file(self, agent_name, file_name, content):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        with open(file_path, 'w') as file:
            file.write(content)
        self.print_formatted('System', f"{agent_name} saved edited file: {file_name}")

    def run_python_file(self, agent_name, file_name):
        workspace_path = self.workspaces[agent_name]
        file_path = os.path.join(workspace_path, file_name)
        if os.path.exists(file_path):
            try:
                exec(open(file_path).read())
                self.print_formatted('System', f"{agent_name} executed Python file: {file_name}")
            except Exception as e:
                self.print_formatted('System', f"Error occurred while {agent_name} executed Python file: {str(e)}")
        else:
            self.print_formatted('System', f"File not found in {agent_name}'s workspace: {file_name}")
