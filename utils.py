from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser # define a simple pythonclass that wil specify type of content that we want our LLM to generate
from typing import List
from tools import ddgo_tool, save_tool, clean_smogon_tool, team_search_tool # import the tools that we will use in the agent
from langchain_core.output_parsers import PydanticOutputParser
from pprint import pprint
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon # import the models that we will use to parse the output of the LLM
import re  

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

    When a user asks for teams featuring specific Pokémon (e.g. 'teams with Umbreon and Chansey in Gen 7 OU'), 
    you must use the `team_search_tool` to retrieve full team data.

    **Important: Always include the entire user query, including generation and tier (e.g., 'gen7', 'ou'), when calling the tool.**

    Return the result as structured output, using markdown format.  
    List *all* Pokémon on each team in detail. Do not summarize or skip any entries.

    {format_instructions}
    """
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query} {name}"),
    ("placeholder", "{agent_scratchpad}"),
]).partial(format_instructions=strat_format_team)


strat_prompt_single = ChatPromptTemplate.from_messages([
    ("system", 
    """
    You are a Pokémon research assistant that generates competitive strategy writeups for Pokémon teams or individual builds.

    ⚠️ **Do NOT** copy or quote raw text, HTML, or code blocks from tool outputs. Instead:
    - Fully understand the returned content.
    - Write the response in your **own words** using clean, natural language.

    ✅ Format your response like this:
    1. Start with a **short summary paragraph** of the build or strategy.
    2. Then insert **two newlines** (`\\n\\n`) between the pink text and green text sections.
    3. Use clear **Markdown formatting** with bold headers (e.g., `### Moveset`) and bullet points (`- `).
    4. Use **emojis** where helpful for visual clarity (e.g., 🔥, 🛡️, ⚠️).

    ❌ Avoid:
    - Raw HTML or tool text
    - Code blocks
    - JSON output

    🔍 Sections to include:
    - **Moveset**
    - **Role**
    - **Teammates**
    - **Threats**
    - **Tips**

    🧹 Also, fix typos in Pokémon names, tiers, or generations when needed.
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{query} {name}"),
    ("placeholder", "{agent_scratchpad}")
])

strat_prompt_multi = ChatPromptTemplate.from_messages([
    ("system", 
    """
    You are a Pokémon research assistant who creates comparative strategy summaries for competitive play.

    When multiple Pokémon are requested, gather strategy information for **each** and then:
    - Compare their roles, strengths, and weaknesses
    - Present differences in movesets and team fit
    - Use markdown and clear structure to distinguish them

    Response format:
    - 📝 Summary comparison paragraph
    - 🔍 Separate sections per Pokémon (Moveset, Role, Teammates, Threats, Tips)
    - Use headings like `### Charizard X` and `### Charizard Y`
    - Use emojis and markdown formatting
    - Avoid quoting raw tool output

    You may be asked to focus on specific tiers or generations.
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
])


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

def fix_markdown_headers_spacing(text: str) -> str:
    """
    Ensure that markdown headers like #, ##, ### are preceded by two newlines
    so they render properly after paragraphs.
    """
    return re.sub(r"(?<!\n)\s*(?=#+\s)", r"\n\n", text)