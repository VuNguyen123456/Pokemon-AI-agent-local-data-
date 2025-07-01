from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser # define a simple pythonclass that wil specify type of content that we want our LLM to generate
from typing import List, Optional, Dict
from langchain.agents import create_tool_calling_agent, AgentExecutor # to create and run test the agent
from langchain_core.output_parsers import PydanticOutputParser
from pprint import pprint
import re  
from langchain.memory import ConversationBufferMemory

from tools import ddgo_tool, save_tool, clean_smogon_tool, team_search_tool, fix_markdown_headers_spacing, ALL_SPECIES, extract_species_tier_gen
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon 
from utils import general_prompt, strat_prompt_single, strat_prompt_team, strat_prompt_multi, format_strategy_team_output, format_multiple_teams_output 
# TODO:
# Still have some problem with generation assumption mainly when compareing pokemon / vs


load_dotenv() #load the env file

llm = ChatOpenAI(model = "gpt-3.5-turbo") 


tools = [ddgo_tool, save_tool, clean_smogon_tool, team_search_tool] # list of tools that we want to use in the agent, in this case we are using the search tool


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, input_key="query")

while True:
    query = input("\nHow can I help with Pokémon? (Type 'quit' or 'exit' to stop): ").strip()
    if re.search(r"\b(quit|exit)\b", query.lower()):
        print("👋 Goodbye! Happy battling!")
        break

    # Choose prompt type
    if re.search(r"\bteam(s|ing)?\b", query, re.IGNORECASE):
        prompt = strat_prompt_team

    # Detect multiple Pokémon for comparison (e.g., "Charizard and Garchomp", or comma-separated)
    elif (
        re.search(r"\b(strategy|build|moveset|compare|vs)\b", query, re.IGNORECASE)
        and (" and " in query.lower() or "," in query)
    ):
        prompt = strat_prompt_multi  # <-- use your new multi-strategy prompt

    # Single Pokémon strategy
    elif re.search(r"\b(strategy|build|weakness|strength|moves|items|abilities)\b", query, re.IGNORECASE):
        prompt = strat_prompt_single

    # Default to general prompt
    else:
        prompt = general_prompt

    # Recreate agent in case prompt changes
    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory,verbose=True)

    # Invoke
    response = agent_executor.invoke({
        "query": query,
        "name": "Pokemon Research Assistant"
    })

    # Display response
    if isinstance(response, AllTeamSearchResult):
        print(format_multiple_teams_output(response.teams))
    else:
        output_text = str(response)
        output_text = fix_markdown_headers_spacing(output_text)
        print(output_text)


# query = input("How can I help with Pokemon? ")

# #or "build" in query.lower() or "weakness" in query.lower() or "strength" in query.lower() or "moves" in query.lower() or "items" in query.lower() or "abilities" in query.lower()

# if re.search(r"\bteam(s|ing)?\b", query, re.IGNORECASE):
#     prompt = strat_prompt_team
# elif re.search(r"\b(strategy|build|weakness|strength|moves|items|abilities)\b", query, re.IGNORECASE):
#     prompt = strat_prompt_single
# else:
#     prompt = general_prompt

# agent = create_tool_calling_agent(
#     llm = llm,
#     prompt=prompt,
#     tools=tools
# )

# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # create an agent executor to run the agent
# response = agent_executor.invoke({"query": query, "chat_history": [], "name": "Pokemon Research Assistant"}) # run the agent executor with the query

# if isinstance(response, AllTeamSearchResult):
#     print(format_multiple_teams_output(response.teams))
# else:
#     output_text = str(response)
#     output_text = fix_markdown_headers_spacing(output_text)
#     print(output_text)

