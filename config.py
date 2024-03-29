# Configuration settings

# Database directory
DATABASE_DIR = 'databases'

# Workspace directory
WORKSPACE_DIR = 'workspace'
groq_api_key = 'your_api_key_here'
# Agent configuration
AGENTS = [
    {
        'name': 'Alice',
        'role': 'Technical Lead that leads software development team',
        'home_pos': (50, 50),
        'office_pos': (300, 200)
    },
    {
        'name': 'Bob',
        'role': 'Backend Developer for projects and applications',
        'home_pos': (50, 150),
        'office_pos': (400, 300)
    },
    {
        'name': 'Carol',
        'role': 'Frontend Developer of user interfaces and experiences',
        'home_pos': (50, 250),
        'office_pos': (500, 400)
    },
    {
        'name': 'David',
        'role': 'Quality Assurance Engineer that tests software applications',
        'home_pos': (50, 350),
        'office_pos': (600, 500)
    },
    {
        'name': 'Eve',
        'role': 'DevOps Engineer that automates software development processes',
        'home_pos': (50, 450),
        'office_pos': (700, 600)
    },
    {
        'name': 'Frank',
        'role': 'Data Scientist that analyzes and interprets complex digital data',
        'home_pos': (50, 550),
        'office_pos': (800, 700)
    }
]

# Simulation settings
SIMULATION_DURATION = 1200  # in seconds

# Agent messages
AGENT_MESSAGES = {
    "system": {
        "default": """You are {name}, a {role} in a software development team at a tech company. Your team is working on a project to develop a new software application.

You have access to the following skills and tools:
- {skills}

You can use the following communication channels to interact with your team members:
- message: Send a direct message to another agent or broadcast a message to multiple agents.
- email: Compose and send an email to one or more agents.
- command: Execute a specific command or skill.
- pass: Skip the current turn and let other agents take action.
- ignore: Ignore the current situation and continue with your own tasks.

You are currently at {location}. Your recent actions include:
- {actions}

Your current thoughts and ideas are:
- {thoughts}

You are currently {working_status}.

{context}

As {name}, consider the current state of the project, your role and responsibilities, and the actions and thoughts of your team members. Determine the best course of action to contribute to the project's success and maintain effective collaboration with your team. Focus on providing clear and concise information that will help move the project forward.
"""
    },
    "user": {
        "default": """Your team members have provided the following updates and responses:

{context}

Based on this information and your own thoughts and ideas, please provide your response in the following format:
(message|recipient|message, email|recipient|subject|body, command|command|args)

Consider the most appropriate communication method and the specific actions or commands that will help advance the project and address any challenges or opportunities. Avoid including unnecessary or irrelevant information in your response."""
    },
    "analyze_context": """
Analyze the following context and determine the most appropriate communication channel:

{context}

Consider the situation, urgency, and the intended recipient(s) when making your decision.
Return the selected communication channel (e.g., "message", "email", "command").
""",
    "generate_summary": """
Generate a summary or key points of the following thoughts:

{thoughts}

Focus on the most important aspects and present them in a clear and concise manner.
""",
    "evaluate_impact": """
Evaluate the potential impact and consequences of the following action:

{action}

Consider the possible outcomes, risks, and benefits of the action.
Provide your evaluation and any recommendations for improvement.
""",
    "thinking_context": """
{name}, take a moment to reflect on your recent actions and interactions:
- Actions: {actions}
- Thoughts: {thoughts}

Consider your role as a {role} and the current state of the project. What are your current priorities? What challenges or opportunities do you see? How can you best contribute to the team's goals?

Share your thoughts and ideas based on your analysis of the situation. Feel free to propose new tasks, suggest improvements, or raise any concerns you may have. Focus on providing clear and concise information that will help move the project forward.
""",
    "acting_context": """
{name}, based on your last thought: '{last_thought}', it's time to take action.

Consider the following steps:
1. Review the available commands and skills at your disposal.
2. Determine which action would best address the situation or advance the project.
3. If the action involves communication, choose the most appropriate method (message, email, etc.).
4. If the action requires the use of a specific tool or skill, provide the necessary arguments or parameters.
5. Execute the chosen action with care and attention to detail.

Remember, your actions should align with your role as a {role} and contribute to the overall success of the team and the project.

Please provide your response in the following format:
(message|recipient|message, email|recipient|subject|body, command|command|args)

Focus on providing clear and concise information that will help move the project forward. Avoid including unnecessary or irrelevant information in your response.
"""
}