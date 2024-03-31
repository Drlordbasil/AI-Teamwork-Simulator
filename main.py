import asyncio
from agent import Agent
from environment import Environment
import config
import database

async def start_workday(agent):
    await agent.go_to_office()
    await agent.check_email()
    await agent.review_tasks()

async def end_workday(agent):
    await agent.wrap_up_tasks()
    await agent.go_home()

async def run_simulation():
    env = Environment()
    agents = []

    api_choice = "groq" #input("Enter the API choice (groq/openai/ollama/langchain/claude): ") # claude isnt working due to rate limiting error(fixing) and i prefer groq for testing.

    for agent_config in config.AGENTS:
        agent = Agent(agent_config['name'], agent_config['role'], agent_config['responsibilities'], agent_config['skills'], env, api_choice)
        agents.append(agent)
        env.add_agent(agent)

    env.load_emails()

    workday_tasks = [start_workday(agent) for agent in agents]
    await asyncio.gather(*workday_tasks)

    collaboration_tasks = []
    for agent in agents:
        collaboration_tasks.extend([
            agent.attend_meeting(),
            agent.collaborate_with_team(),
            agent.work_on_projects(),
        ])
    await asyncio.gather(*collaboration_tasks)

    while True:
        for agent in agents:
            await agent.think()
            await agent.act()

            if agent.should_take_break():
                await agent.take_break()

            for other_agent in agents:
                if other_agent != agent:
                    message = await agent.generate_message(other_agent)
                    await env.send_message(agent.name, other_agent.name, message)

                    if agent.should_share_file(other_agent):
                        file_name, file_content = await agent.generate_file(other_agent)
                        env.save_workspace_file(agent.name, file_name, file_content)
                        env.print_formatted(agent.name, f"Shared file '{file_name}' with {other_agent.name}")

            important_info = await agent.generate_important_info()
            env.save_important_info(important_info)

        await asyncio.sleep(1)

    end_of_day_tasks = [end_workday(agent) for agent in agents]
    await asyncio.gather(*end_of_day_tasks)

if __name__ == "__main__":
    asyncio.run(run_simulation())
