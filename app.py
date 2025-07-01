import gradio as gr
import re
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import List
from dotenv import load_dotenv

# tools:
from tools import ddgo_tool, save_tool, clean_smogon_tool, team_search_tool
from models import AllTeamSearchResult
from tools import fix_markdown_headers_spacing 
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon 

load_dotenv()

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

tools = [ddgo_tool, save_tool, clean_smogon_tool, team_search_tool]
llm = ChatOpenAI(model = "gpt-3.5-turbo") 
  # or gpt-3.5-turbo

#prompts !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!PROMBLEM IS HERE 
from main import general_prompt, strat_prompt_single, strat_prompt_team, strat_prompt_multi

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, input_key="query")

def chat_with_agent(query, chat_history):
    # Determine the right prompt
    if re.search(r"\bteam(s|ing)?\b", query, re.IGNORECASE):
        prompt = strat_prompt_team
    elif re.search(r"\b(strategy|build|moveset|compare|vs)\b", query, re.IGNORECASE) and (" and " in query.lower() or "," in query):
        prompt = strat_prompt_multi
    elif re.search(r"\b(strategy|build|weakness|strength|moves|items|abilities)\b", query, re.IGNORECASE):
        prompt = strat_prompt_single
    else:
        prompt = general_prompt

    # Create agent with prompt + memory
    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False)

    # Run agent
    response = agent_executor.invoke({"query": query, "name": "Pokemon Research Assistant"})

    # Format output
    if isinstance(response, AllTeamSearchResult):
        output = format_multiple_teams_output(response.teams)
    else:
        output = fix_markdown_headers_spacing(str(response))

    # Update chat history for Gradio (optional, if using ChatInterface)
    chat_history.append((query, output))
    return "", chat_history

# 🖼️ Gradio UI
gr.ChatInterface(
    fn=chat_with_agent,
    title="🧠 Pokémon Strategy Assistant",
    chatbot=gr.Chatbot(height=500),
    theme="soft",
    examples=["Charizard build in Gen7 OU", "Teams with Umbreon", "Compare Garchomp and Salamence"],
    stop_btn="Stop",
    retry_btn="Retry"
).launch()