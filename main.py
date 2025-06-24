from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser # define a simple pythonclass that wil specify type of content that we want our LLM to generate
from typing import List, Optional, Dict
from langchain.agents import create_tool_calling_agent, AgentExecutor # to create and run test the agent
from tools import ddgo_tool, save_tool, smogon_tool, team_search_tool # import the tools that we will use in the agent
from langchain_core.output_parsers import PydanticOutputParser
from pprint import pprint
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon # import the models that we will use to parse the output of the LLM
import re  
# TODO:
# look into not having to download all the data from smogon but rather just use it throuhg github API


load_dotenv() #load the env file


llm = ChatOpenAI(model = "gpt-3.5-turbo") 
general_format = (
    "Use bullet points, markdown, and emoji where helpful.\n"
    "Keep your explanation clear and concise.\n"
    "Avoid JSON formatting unless explicitly asked."
)
general_prompt = ChatPromptTemplate.from_messages([
    ("system", 
    """
        You are a Pokémon research assistant that helps generate general information in pokemon.

        Answer the user query, recommend some additional information surrounding it and use necessary tools.

        Use readable formatting like bullet points, emoji, or markdown if appropriate.
        
        Correct any typos in Pokémon names, tier labels, or generation numbers where possible.\n{format_instructions}
    """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query} {name}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions=general_format)

# This will be changed or split into multiple prompts, 1 for team(pydantic), 1  for strategy (normal format)
strat_parser = PydanticOutputParser(pydantic_object=AllTeamSearchResult)
strat_format_team = strat_parser.get_format_instructions()
strat_prompt_team = ChatPromptTemplate.from_messages([
    ("system", 
    """
       You are a Pokémon research assistant helping with competitive teams.

        When a user asks for teams featuring specific Pokémon (e.g. 'teams with Umbreon and Chansey'), 
        you must use the `team_search_tool` to retrieve full team data.

        Return the result as structured output, using markdown format.
        Do not summarize unless instructed to.

        {format_instructions}
    """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query} {name}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions=strat_format_team)

strat_format_single = (
    "Use bullet points, markdown, and emoji where helpful.\n"

    "Summarize, expand the data given into a clear readable format for user.\n"

    "Avoid JSON formatting unless explicitly asked."
)
strat_prompt_single = ChatPromptTemplate.from_messages([
    ("system", 
    """
        You are a Pokémon research assistant that helps generate competitive strategies.

        Summarize key team roles, highlight synergy, explain strengths/weaknesses, and use natural language formatting.

        Avoid raw JSON. Use readable formatting like bullet points, emoji, or markdown if appropriate.

        Correct any typos in Pokémon names, tier labels, or generation numbers where possible.\n{format_instructions}
    """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query} {name}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions=strat_format_single)

tools = [ddgo_tool, save_tool, smogon_tool, team_search_tool] # list of tools that we want to use in the agent, in this case we are using the search tool

def format_strategy_team_output(resp: TeamSearchResult) -> str:
    output = [f"🔍 **Team Name:** {resp.team_name}\n👤 **Author:** {resp.author}\n"]

    for pokemon in resp.team:
        output.append(f"---\n**{pokemon.species}**")
        if pokemon.item:
            output.append(f"- **Item:** {pokemon.item}")
        if pokemon.ability:
            output.append(f"- **Ability:** {pokemon.ability}")
        if pokemon.nature:
            output.append(f"- **Nature:** {pokemon.nature}")
        if pokemon.evs:
            evs_str = " / ".join(f"{v} {k}" for k, v in pokemon.evs.items())
            output.append(f"- **EVs:** {evs_str}")
        if pokemon.ivs:
            ivs_str = " / ".join(f"{v} {k}" for k, v in pokemon.ivs.items())
            output.append(f"- **IVs:** {ivs_str}")
        output.append(f"- **Moves:** {', '.join(pokemon.moves)}")

    if resp.pokemonShowdownExport:
        output.append("\n📋 **Showdown Export**:\n```\n" + resp.pokemonShowdownExport + "\n```")

    return "\n".join(output)

def format_multiple_teams_output(teams: List[TeamSearchResult]) -> str:
    outputs = []
    for i, team in enumerate(teams, 1):
        outputs.append(f"### Team #{i}\n")
        outputs.append(format_strategy_team_output(team))
        outputs.append("\n" + "-"*30 + "\n")
    return "\n".join(outputs)


query = input("How can I help with Pokemon? ")

#or "build" in query.lower() or "weakness" in query.lower() or "strength" in query.lower() or "moves" in query.lower() or "items" in query.lower() or "abilities" in query.lower()

if re.search(r"\bteam(s|ing)?\b", query, re.IGNORECASE):
    prompt = strat_prompt_team
elif re.search(r"\b(strategy|build|weakness|strength|moves|items|abilities)\b", query, re.IGNORECASE):
    prompt = strat_prompt_single
else:
    prompt = general_prompt

agent = create_tool_calling_agent(
    llm = llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # create an agent executor to run the agent
response = agent_executor.invoke({"query": query, "chat_history": [], "name": "Pokemon Research Assistant"}) # run the agent executor with the query

if isinstance(response, AllTeamSearchResult):
    print(format_multiple_teams_output(response.teams))
else:
    print("⚠️ Response is not a TeamSearchResult. Dumping raw output for inspection:\n")
    pprint(response)  # Pretty print for readability
    # Optional: print raw type
    print(f"\n📦 Actual response type: {type(response)}")

