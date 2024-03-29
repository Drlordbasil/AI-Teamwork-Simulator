import asyncio
import random
import re
from time import sleep, time
from skills import scrape_webpage, save_file, edit_file, analyze_code, search_files, git_clone, git_pull, git_push, check_code_quality, install_dependencies, generate_documentation, run_unit_tests
from config import AGENT_MESSAGES, groq_api_key


class Agent:
    def __init__(self, name, role, home_pos, office_pos, env, api_choice):
        self.name = name
        self.role = role
        self.home_pos = home_pos
        self.office_pos = office_pos
        self.location = "home"
        self.is_working = False
        self.last_break_start = 0
        self.last_break_duration = 0
        self.actions = []  # Store agent's actions for contextual awareness
        self.thoughts = []  # Store agent's thoughts for contextual awareness
        self.env = env
        self.api_choice = api_choice
        self.skills = {
            "scrape_webpage": scrape_webpage,
            "save_file": save_file,
            "edit_file": edit_file,
            "analyze_code": analyze_code,
            "search_files": search_files,
            "git_clone": git_clone,
            "git_pull": git_pull,
            "git_push": git_push,
            "check_code_quality": check_code_quality,
            "install_dependencies": install_dependencies,
            "generate_documentation": generate_documentation,
            "run_unit_tests": run_unit_tests,
            "go_home": self.go_home,
            "go_to_office": self.go_to_office,
            "take_break": self.take_break,
            "open_browser": self.env.open_browser,
            "close_browser": self.env.close_browser,
            "navigate_to_url": self.env.navigate_to_url,
            "get_browser_content": self.env.get_browser_content,
            "edit_workspace_file": self.env.edit_file,
            "save_workspace_file": self.env.save_edited_file,
            "run_python_file": self.env.run_python_file,
            "list_workspace_files": self.env.list_workspace_files,
            "choose_communication_method": self.choose_communication_method,
            "choose_command": self.choose_command,
            "think": self.think,
            "act": self.act,
        }

    def use_skill_in_skills(self, skill_name, *args):
        if skill_name in self.skills:
            return self.skills[skill_name](*args)
        else:
            self.env.print_formatted(self.name, f"{self.name} encountered an unknown command: '{skill_name}'", border_style="*")
            return None

    async def go_home(self):
        self.location = "home"
        self.env.print_formatted(self.name, f"{self.name} decides it's time to go home.", border_style="*")
        self.is_working = False
        self.actions.append("Went home")
        await asyncio.sleep(1)

    async def go_to_office(self):
        self.location = "office"
        self.env.print_formatted(self.name, f"{self.name} arrives at the office, ready to start the day.", border_style="*")
        self.is_working = True
        self.actions.append("Arrived at the office")
        await asyncio.sleep(1)

    async def take_break(self):
        if self.is_working and (time() - self.last_break_start) > self.last_break_duration:
            self.env.print_formatted(self.name, f"{self.name} is taking a break.", border_style="+")
            self.last_break_start = time()
            self.last_break_duration = random.uniform(5, 10)  # 5 to 10 seconds for demonstration
            self.is_working = False
            self.actions.append("Took a break")
            await asyncio.sleep(self.last_break_duration)
            self.env.print_formatted(self.name, f"{self.name}'s break is over.", border_style="+")
            self.is_working = True
            self.actions.append("Break is over")

    async def choose_communication_method(self):
        context = f"""
        {self.name}, as a {self.role}, you have several communication methods available to you:
        - message: Send a direct message to another agent or broadcast a message to multiple agents.
        - email: Compose and send an email to one or more agents.
        - command: Execute a specific command or skill.
        - pass: Skip the current turn and let other agents take action.
        - ignore: Ignore the current situation and continue with your own tasks.

        Consider the current situation, your role, and the available agents when deciding on the most appropriate communication method.
        """
        response = await self.call_api(context)
        return response

    async def choose_command(self):
        context = f"""
        {self.name}, as a {self.role}, you have access to various commands and skills:
        - scrape_webpage: Scrape the content of a webpage given a URL.
        - save_file: Save content to a file in the workspace.
        - edit_file: Edit an existing file in the workspace.
        - analyze_code: Perform static code analysis on a given code snippet.
        - search_files: Search for files containing a specific keyword in the workspace.
        - git_clone: Clone a Git repository to the workspace.
        - git_pull: Pull the latest changes from a Git repository in the workspace.
        - git_push: Push local changes to a remote Git repository.
        - check_code_quality: Check the quality of a Python file using pylint.
        - install_dependencies: Install dependencies from a requirements file.
        - generate_documentation: Generate documentation for Python code in the workspace.
        - run_unit_tests: Run unit tests for Python code in the workspace.
        - go_home: Decide to go home and end the workday.
        - go_to_office: Arrive at the office and start the workday.
        - take_break: Take a short break to recharge.
        - open_browser: Open a new browser instance for web scraping and browsing.
        - close_browser: Close the current browser instance.
        - navigate_to_url: Navigate to a specific URL in the browser.
        - get_browser_content: Get the HTML content of the current web page.
        - edit_workspace_file: Open a file in the workspace for editing.
        - save_workspace_file: Save changes made to a file in the workspace.
        - run_python_file: Execute a Python file from the workspace.
        - list_workspace_files: List all the files in the workspace.

        Think carefully about which command or skill would be most useful in the current situation, considering your role, the available tools, and the desired outcome.
        """
        response = await self.call_api(context)
        return response

    async def analyze_context(self, context):
        analysis_prompt = AGENT_MESSAGES["analyze_context"].format(context=context)
        selected_channel = await self.call_api(analysis_prompt)
        return selected_channel.strip()

    async def generate_summary(self, thoughts):
        summary_prompt = AGENT_MESSAGES["generate_summary"].format(thoughts=thoughts)
        summary = await self.call_api(summary_prompt)
        return summary.strip()

    async def evaluate_impact(self, action):
        evaluation_prompt = AGENT_MESSAGES["evaluate_impact"].format(action=action)
        evaluation = await self.call_api(evaluation_prompt)
        return evaluation.strip()

    async def think(self):
        context = AGENT_MESSAGES["thinking_context"].format(
            name=self.name,
            role=self.role,
            actions=', '.join(self.actions),
            thoughts=', '.join(self.thoughts)
        )
        thought = await self.call_api(context)
        self.thoughts.append(thought)
        summary = await self.generate_summary(thought)
        self.env.print_formatted(self.name, f"{self.name}'s current thoughts: {summary}")
        return thought

    async def act(self):
        if self.thoughts:
            last_thought = self.thoughts[-1]
            context = AGENT_MESSAGES["acting_context"].format(
                name=self.name,
                role=self.role,
                last_thought=last_thought
            )
            selected_channel = await self.analyze_context(context)
            action = await self.call_api(context)
            evaluation = await self.evaluate_impact(action)
            self.env.print_formatted(self.name, f"{self.name}'s action evaluation: {evaluation}")

            message_pattern = r"message\|(.*?)\|(.*)"
            email_pattern = r"email\|(.*?)\|(.*?)\|(.*)"
            command_pattern = r"command\|(.*?)\|(.*)"

            if re.match(message_pattern, action) and selected_channel == "message":
                match = re.match(message_pattern, action)
                recipient, message = match.groups()
                await self.env.send_message(self.name, recipient.strip(), message.strip())
            elif re.match(email_pattern, action) and selected_channel == "email":
                match = re.match(email_pattern, action)
                recipient, subject, body = match.groups()
                self.env.send_email(self.name, [recipient.strip()], subject.strip(), body.strip())
            elif re.match(command_pattern, action) and selected_channel == "command":
                match = re.match(command_pattern, action)
                command, args = match.groups()
                command = command.strip()
                if command in self.skills:
                    result = await self.skills[command](*[arg.strip() for arg in args.split(',')])
                    self.env.print_formatted(self.name, f"{self.name} executed command '{command}' with result: {result}")
                else:
                    self.env.print_formatted(self.name, f"{self.name} encountered an unknown command: '{command}'", border_style="*")
            else:
                self.env.print_formatted(self.name, f"{self.name} generated an invalid action or selected an inappropriate communication channel: '{action}'", border_style="*")
                retry = True
                await self.choose_communication_method()
        else:
            self.env.print_formatted(self.name, f"{self.name} has no thoughts to act upon.", border_style="*")

    async def call_api(self, context):
        if self.api_choice == "groq":
            response = await self.call_groq_api(context)
        elif self.api_choice == "openai":
            response = await self.call_openai_api(context)
        elif self.api_choice == "ollama":
            response = await self.ollama_local_server_api(context)
        else:
            raise ValueError(f"Invalid API choice: {self.api_choice}")
        return response

    async def call_groq_api(self, context):
        from groq import Groq
        import asyncio

        client = Groq(api_key=groq_api_key) # never remove this api secret key.

        def run_groq_api():
            system_message = AGENT_MESSAGES["system"]["default"].format(
                name=self.name,
                role=self.role,
                skills=', '.join(self.skills.keys()),
                location=self.location,
                actions=', '.join(self.actions),
                thoughts=', '.join(self.thoughts),
                working_status='working on the project' if self.is_working else 'not actively working on the project',
                context=context
            )
            user_message = AGENT_MESSAGES["user"]["default"].format(context=context)

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="mixtral-8x7b-32768",               # Adjust model as needed  "llama2-70b-4096","gemma-7b-it", "mixtral-8x7b-32768"
                temperature=0.7,
                max_tokens=32768,
            )
            return chat_completion

        chat_completion = await asyncio.to_thread(run_groq_api)
        response = chat_completion.choices[0].message.content
        sleep(1)
        return response

    async def call_openai_api(self, context):
        from openai import OpenAI
        client = OpenAI()

        system_message = AGENT_MESSAGES["system"]["default"].format(
            name=self.name,
            role=self.role,
            skills=', '.join(self.skills.keys()),
            location=self.location,
            actions=', '.join(self.actions),
            thoughts=', '.join(self.thoughts),
            working_status='working on the project' if self.is_working else 'not actively working on the project',
            context=context
        )
        user_message = AGENT_MESSAGES["user"]["default"].format(context=context)

        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    async def ollama_local_server_api(self, context):
        import ollama
        client = ollama

        system_message = AGENT_MESSAGES["system"]["default"].format(
            name=self.name,
            role=self.role,
            skills=', '.join(self.skills.keys()),
            location=self.location,
            actions=', '.join(self.actions),
            thoughts=', '.join(self.thoughts),
            working_status='working on the project' if self.is_working else 'not actively working on the project',
            context=context
        )
        user_message = AGENT_MESSAGES["user"]["default"].format(context=context)

        response = client.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']
