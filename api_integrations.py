import asyncio
import random
from time import sleep
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from groq import Groq
from openai import OpenAI
import ollama
import anthropic
from config import AGENT_MESSAGES, groq_api_key, claude_api_key

class GroqLLM(LLM):
    def __init__(self, api_key):
        self.api_key = api_key

    def _call(self, prompt, stop=None):
        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=32768,
        )
        return response.choices[0].message.content

    @property
    def _identifying_params(self):
        return {"api_key": self.api_key}
    
    @property
    def _llm_type(self):
        return "groq"

class APIIntegrations:
    def __init__(self, api_choice, agent_data):
        self.api_choice = api_choice
        self.agent_data = agent_data
       
        if api_choice == "groq":
            self.client = Groq(api_key=groq_api_key)
        elif api_choice == "openai":
            self.client = OpenAI()
        elif api_choice == "ollama":
            self.client = ollama
        elif api_choice == "langchain":
            self.client = None
        elif api_choice == "claude":
            self.client = anthropic.Anthropic(api_key=claude_api_key)
        else:
            raise ValueError(f"Invalid API choice: {api_choice}")

    async def call_api(self, context):
        if self.api_choice == "groq":
            response = await self.call_groq_api(context)
            sleep(3)
        elif self.api_choice == "openai":
            response = await self.call_openai_api(context)
        elif self.api_choice == "ollama":
            response = await self.ollama_local_server_api(context)
        elif self.api_choice == "langchain":
            response = await self.call_langchain_api(context)
        elif self.api_choice == "claude":
            response = await self.call_claude_api(context)
        else:
            raise ValueError(f"Invalid API choice: {self.api_choice}")
        sleep(3)
        return response

    async def call_groq_api(self, context):
        def run_groq_api():
            system_message = AGENT_MESSAGES["system"]["default"].format(
                name=self.agent_data["name"],
                role=self.agent_data["role"],
                responsibilities=self.agent_data["responsibilities"],
                skills=', '.join(self.agent_data["skills"]),
                location=self.agent_data["location"],
                actions=', '.join(self.agent_data["actions"]),
                thoughts=' '.join(map(str, self.agent_data["thoughts"])),
                working_status='working on the project' if self.agent_data["is_working"] else 'not actively working on the project',
                context=context
            )
            user_message = AGENT_MESSAGES["user"]["default"].format(context=context)
            model = random.choice(["llama2-70b-4096", "gemma-7b-it", "mixtral-8x7b-32768"])
            temp = random.uniform(0.1, 0.9)
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                model="mixtral-8x7b-32768",
                temperature=temp,
                max_tokens=32768,
            )
            return chat_completion
        chat_completion = await asyncio.to_thread(run_groq_api)
        response = chat_completion.choices[0].message.content
        sleep(5)
        return response

    async def call_openai_api(self, context):
        system_message = AGENT_MESSAGES["system"]["default"].format(
            name=self.agent_data["name"],
            role=self.agent_data["role"],
            responsibilities=self.agent_data["responsibilities"],
            skills=', '.join(self.agent_data["skills"]),
            location=self.agent_data["location"],
            actions=', '.join(self.agent_data["actions"]),
            thoughts=' '.join(map(str, self.agent_data["thoughts"])),
            working_status='working on the project' if self.agent_data["is_working"] else 'not actively working on the project',
            context=context
        )
        user_message = AGENT_MESSAGES["user"]["default"].format(context=context)
        response = self.client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content

    async def ollama_local_server_api(self, context):
        system_message = AGENT_MESSAGES["system"]["default"].format(
            name=self.agent_data["name"],
            role=self.agent_data["role"],
            responsibilities=self.agent_data["responsibilities"],
            skills=', '.join(self.agent_data["skills"]),
            location=self.agent_data["location"],
            actions=', '.join(self.agent_data["actions"]),
            thoughts=' '.join(map(str, self.agent_data["thoughts"])),
            working_status='working on the project' if self.agent_data["is_working"] else 'not actively working on the project',
            context=context
        )
        user_message = AGENT_MESSAGES["user"]["default"].format(context=context)
        response = self.client.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']

    async def call_langchain_api(self, context):
        prompt_template = PromptTemplate(
            input_variables=["context", "name", "role", "responsibilities", "skills", "location", "actions", "thoughts", "working_status"],
            template=AGENT_MESSAGES["system"]["default"] + "\n\n" + AGENT_MESSAGES["user"]["default"],
        )
        groq_llm = GroqLLM(api_key=groq_api_key)
        chain = LLMChain(llm=groq_llm, prompt=prompt_template)
        response = chain.run(
            context=context,
            name=self.agent_data["name"],
            role=self.agent_data["role"],
            responsibilities=self.agent_data["responsibilities"],
            skills=', '.join(self.agent_data["skills"]),
            location=self.agent_data["location"],
            actions=', '.join(self.agent_data["actions"]),
            thoughts=' '.join(map(str, self.agent_data["thoughts"])),
            working_status='working on the project' if self.agent_data["is_working"] else 'not actively working on the project'
        )
        return response
    async def call_claude_api(self, context):
        system_message = AGENT_MESSAGES["system"]["default"].format(
            name=self.agent_data["name"],
            role=self.agent_data["role"],
            responsibilities=self.agent_data["responsibilities"],
            skills=', '.join(self.agent_data["skills"]),
            location=self.agent_data["location"],
            actions=', '.join(self.agent_data["actions"]),
            thoughts=' '.join(map(str, self.agent_data["thoughts"])),
            working_status='working on the project' if self.agent_data["is_working"] else 'not actively working on the project',
            context=context
        )
        user_message = AGENT_MESSAGES["user"]["default"].format(context=context)
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=0.7,
            system=system_message,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        
        return response.content[0].text
