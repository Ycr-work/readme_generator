from crewai import Agent,Crew,Process,Task
from crewai.project import CrewBase,agent,crew,task

from readme_generator.tools.model_search import ModelSearchTool
from readme_generator.tools.github_pr import GithubPRTool
from langchain_openai import ChatOpenAI

@CrewBase
class GithubCrew:
    agents_config="config/agents.yaml"
    tasks_config="config/tasks.yaml"
    llm=ChatOpenAI(model="gpt-4o")

    @agent
    def github_agent(self)->Agent:
        github_tool=GithubPRTool()
        return Agent(
            config=self.agents_config["github_agent"],
            tools=[github_tool],
            llm=self.llm,
            verbose=True
        )

    @agent
    def readme_generator_agent(self)->Agent:
        model_search_tool=ModelSearchTool()
        return Agent(
            config=self.agents_config["readme_generator_agent"],
            tools=[model_search_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )

    @agent 
    def run_code_agent(self)->Agent:
        pass

    @task 
    def github_pr(self)->Task:
        return Task(config=self.tasks_config["github_pr"])
    
    @task
    def readme_generate(self)->Task:
        return Task(config=self.tasks_config["readme_generate"])
    
    @task
    def run_code(self)->Task:
        return Task(config=self.tasks_config["run_code"])
    
    @crew
    def crew(self)->Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )