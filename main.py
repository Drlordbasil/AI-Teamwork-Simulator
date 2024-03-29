import asyncio
import random
from time import time
from agent import Agent
from environment import Environment
import config
import database

async def run_simulation():
    # Initialize the environment and add agents
    env = Environment()
    agents = []
    
    api_choice = input("Enter the API choice (groq/openai): ")
    
    for agent_config in config.AGENTS:
        agent = Agent(agent_config['name'], agent_config['role'], agent_config['home_pos'], agent_config['office_pos'], env, api_choice)
        agents.append(agent)
        env.add_agent(agent)

    await asyncio.gather(*[agent.go_to_office() for agent in agents])
    list_of_agents = [a.name for a in agents]

    # Development Phase
    start_time = time()
    while True: 
        if time() - start_time > config.SIMULATION_DURATION:
            break
        
        # Agents work on their assigned tasks
        for agent in agents:
            await agent.think()  # Generate thoughts
            await agent.act()    # Take actions based on thoughts

if __name__ == "__main__":
    asyncio.run(run_simulation())