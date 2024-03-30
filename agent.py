import asyncio
from api_integrations import APIIntegrations
from bs4 import BeautifulSoup
import os

class Agent:
    def __init__(self, name, role, responsibilities, skills, env, api_choice):
        self.name = name
        self.role = role
        self.responsibilities = responsibilities
        self.skills = skills
        self.actions = []
        self.thoughts = []
        self.env = env
        self.api_choice = api_choice
        self.api_integrations = APIIntegrations(api_choice, self.get_agent_data())

    def get_agent_data(self):
        return {
            "name": self.name,
            "role": self.role,
            "responsibilities": self.responsibilities,
            "skills": self.skills,
            "actions": self.actions,
            "thoughts": self.thoughts,
            "location": "home",
            "is_working": False,
        }

    async def go_to_office(self):
        self.get_agent_data()["location"] = "office"
        self.get_agent_data()["is_working"] = True
        self.env.print_formatted(self.name, f"{self.name} has arrived at the office.")

    async def go_home(self):
        self.get_agent_data()["location"] = "home"
        self.get_agent_data()["is_working"] = False
        self.env.print_formatted(self.name, f"{self.name} has left the office and gone home.")

    async def check_email(self):
        emails = self.env.check_email(self.name)
        if emails:
            self.env.print_formatted(self.name, f"{self.name} has {len(emails)} unread email(s).")
        else:
            self.env.print_formatted(self.name, f"{self.name} has no unread emails.")

    async def review_tasks(self):
        self.env.print_formatted(self.name, f"{self.name} is reviewing their tasks for the day.")

    async def wrap_up_tasks(self):
        self.env.print_formatted(self.name, f"{self.name} is wrapping up their tasks for the day.")

    async def attend_meeting(self):
        self.env.print_formatted(self.name, f"{self.name} is attending a meeting.")
        await asyncio.sleep(1)

    async def collaborate_with_team(self):
        self.env.print_formatted(self.name, f"{self.name} is collaborating with their team.")
        await asyncio.sleep(1)

    async def work_on_projects(self):
        self.env.print_formatted(self.name, f"{self.name} is working on their projects.")
        await asyncio.sleep(1)

    def should_take_break(self):
        return self.get_agent_data()["is_working"] and len(self.actions) % 5 == 0

    async def take_break(self):
        self.env.print_formatted(self.name, f"{self.name} is taking a break.")
        await asyncio.sleep(1)

    async def generate_message(self, recipient):
        context = f"{self.name} needs to send a message to {recipient.name}."
        message = await self.call_api(context)
        return message

    def should_share_file(self, recipient):
        return self.get_agent_data()["is_working"] and len(self.actions) % 3 == 0

    async def generate_file(self, recipient):
        context = f"{self.name} needs to generate a file to share with {recipient.name}."
        file_content = await self.call_api(context)
        file_name = f"{self.name}_file_for_{recipient.name}.txt"
        return file_name, file_content

    async def generate_important_info(self):
        context = f"{self.name} needs to generate important information based on their current context and responsibilities."
        important_info = await self.call_api(context)
        return important_info

    async def think(self):
        context = f"""
        {self.name}, reflect on your recent actions and interactions:
        - Actions: {', '.join(self.actions)} 
        - Thoughts: {', '.join(self.thoughts)}

        Based on your responsibilities as a {self.role} and the current project status, consider:
        - What are the most pressing priorities and challenges?
        - How can you use your skills and expertise to address them?  
        - What information or input do you need from your team members?
        - Are there any process improvements or optimizations you can suggest?

        Analyze the situation and share your ideas and recommendations. Provide specific next steps and explain your reasoning.
        """
        thought = await self.call_api(context)
        self.thoughts.append(thought)
        summary = await self.generate_summary(thought)
        self.env.print_formatted(self.name, f"{self.name}'s current thoughts: {summary}")
        return thought

    async def act(self):
        if self.thoughts:
            last_thought = self.thoughts[-1]
            context = f"""
            {self.name}, based on your recent thought: '{last_thought}', it's time to act.

            Consider the available actions and skills relevant to your role as a {self.role}. Determine the best course of action to address the current situation and advance the project goals.

            Remember to:
            - Be specific and provide all necessary details and context
            - Anticipate any questions or concerns others may have
            - Clarify any assumptions or uncertainties 
            - Break down complex actions into step-by-step instructions
            - Coordinate with team members on cross-functional tasks

            Your action should demonstrate your expertise as a {self.role} and help drive the project forward. Focus on delivering value and enabling effective collaboration.
            """
            action = await self.call_api(context)
            self.actions.append(action)
            evaluation = await self.evaluate_impact(action)
            self.env.print_formatted(self.name, f"{self.name}'s action: {action}")
            self.env.print_formatted(self.name, f"{self.name}'s action evaluation: {evaluation}")
        else:
            self.env.print_formatted(self.name, f"{self.name} has no thoughts to act upon.", border_style="*")

    async def guide(self, task):
        context = f"""
        {self.name}, your team member needs guidance on the following task:
        {task}

        As a {self.role}, break down the task into clear, step-by-step instructions. Provide explanations and examples where necessary.

        Consider:
        - What are the key objectives and desired outcomes of the task?
        - What skills, tools, or resources are required?
        - What are the potential challenges or roadblocks, and how can they be overcome?
        - How can the task be efficiently executed while maintaining high quality?

        Your guidance should empower your team member to successfully complete the task and contribute to the project's progress.
        """
        guidance = await self.call_api(context)
        self.env.print_formatted(self.name, f"{self.name}'s guidance for the task: {guidance}")

    async def analyze_context(self, context):
        analysis_prompt = f"""
        Analyze the following context:

        {context}

        Consider the situation, urgency, intended recipient(s), and the nature of the information when providing your analysis.
        Identify the key points, potential issues, and opportunities for collaboration or improvement.
        """
        analysis = await self.call_api(analysis_prompt)
        return analysis.strip()

    async def generate_summary(self, thoughts):
        summary_prompt = f"""
        Generate a concise summary or key points from the following thoughts:

        {thoughts}

        Focus on the most important aspects that are directly relevant to advancing the project. Prioritize information that helps with decision making, problem solving, or collaboration.
        """
        summary = await self.call_api(summary_prompt)
        return summary.strip()

    async def evaluate_impact(self, action):
        evaluation_prompt = f"""
        Evaluate the potential impact and consequences of the following action:

        {action}

        Consider how the action aligns with the project goals, its feasibility, and its effect on the work of other team members. Identify any risks or uncertainties.
        Provide your evaluation along with any suggestions for improvement or alternative approaches.
        """
        evaluation = await self.call_api(evaluation_prompt)
        return evaluation.strip()

    async def call_api(self, context):
        return await self.api_integrations.call_api(context)

    def create_file(self, file_name, content):
        self.env.create_file(self.name, file_name, content)
    
    def read_file(self, file_name):
        return self.env.read_file(self.name, file_name)

    def update_file(self, file_name, content):
        self.env.update_file(self.name, file_name, content)

    def delete_file(self, file_name):
        self.env.delete_file(self.name, file_name)
    
    def create_folder(self, folder_name):
        self.env.create_folder(self.name, folder_name)

    def list_folder_contents(self, folder_name):
        return self.env.list_folder_contents(self.name, folder_name)
    
    async def scrape_webpage(self, url):
        scraped_data = self.env.scrape_webpage(url)
        if scraped_data:
            file_name = f"{self.name}_scraped_data.txt"
            content = self.format_scraped_data(scraped_data)
            self.env.save_workspace_file(self.name, file_name, content)
            self.env.print_formatted(self.name, f"Scraped data saved to {file_name}")
        else:
            self.env.print_formatted(self.name, "Failed to scrape webpage.")

    def format_scraped_data(self, scraped_data):
        formatted_data = f"Title: {scraped_data['title']}\n\n"
        formatted_data += "Headers:\n"
        for header in scraped_data['headers']:
            formatted_data += f"- {header}\n"
        formatted_data += "\nParagraphs:\n"
        for paragraph in scraped_data['paragraphs']:
            formatted_data += f"{paragraph}\n\n"
        formatted_data += "Links:\n"
        for link in scraped_data['links']:
            formatted_data += f"- {link}\n"
        return formatted_data
