import os
import json
import random
import re
from typing import List, Optional
from datetime import datetime
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
import spacy
from spacy.matcher import PhraseMatcher
from pydantic import BaseModel, Field
from typing import Optional
from models import AllTeamSearchResult, TeamSearchResult, TeamPokemon
from langchain.tools import StructuredTool

class TeamSearchInput(BaseModel):
    query: str = Field(..., description="Search query with Pokémon name and optional tier/gen info")
    sample_size: Optional[int] = Field(3, description="Number of results to return")

def load_pokemon_analysis(filepath) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

All_POKEMON_PATH = os.path.join("smogon", "data", "analyses", "gen9.json") # gen5 contain all of pokemon

ALL_TIERS = {
    "ou": "ou", "overused": "ou", "o.u.": "ou", "ou tier": "ou", "over used": "ou",
    "uu": "uu", "underused": "uu", "u.u.": "uu", "uu tier": "uu", "under used": "uu",
    "ru": "ru", "rarelyused": "ru","rarely used": "ru", "r.u.": "ru",
    "nu": "nu", "neverused": "nu","never used": "nu", "n.u.": "nu",
    "pu": "pu", "partiallyused": "pu", "partially used": "pu", "p.u.": "pu",
    "zu": "zu", "zeroused": "zu", "zero used": "zu", "z.u.": "zu",
    "ubers": "ubers", "uber": "ubers", "legendary tier": "ubers",
    "lc": "lc", "little cup": "lc", "l.c.": "lc",
    "nfe": "nfe", "not fully evolved": "nfe",
    "monotype": "monotype", "mono type": "monotype",
    "1v1": "1v1", "one versus one": "1v1", "1 vs 1": "1v1",
    "nationaldex": "nationaldex", "national dex": "nationaldex", "natdex": "nationaldex",
    "nationaldexuu": "nationaldexuu", "national dex uu": "nationaldexuu",
    "stabmons": "stabmons", "stab mons": "stabmons", "stab-mons": "stabmons",
}

ALL_SPECIES = list(load_pokemon_analysis(All_POKEMON_PATH).keys())

GENERATION_ALIASES = {
    "gen1": "gen1","gen 1": "gen1", "generation 1": "gen1", "1st gen": "gen1", "first generation": "gen1",
    "gen2": "gen2","gen 2": "gen2", "generation 2": "gen2", "2nd gen": "gen2", "second generation": "gen2",
    "gen3": "gen3","gen 3": "gen3", "generation 3": "gen3", "3rd gen": "gen3", "third generation": "gen3",
    "gen4": "gen4","gen 4": "gen4", "generation 4": "gen4", "4th gen": "gen4", "fourth generation": "gen4",
    "gen5": "gen5","gen 5": "gen5", "generation 5": "gen5", "5th gen": "gen5", "fifth generation": "gen5",
    "gen6": "gen6","gen 6": "gen6", "generation 6": "gen6", "6th gen": "gen6", "sixth generation": "gen6",
    "gen7": "gen7","gen 7": "gen7", "generation 7": "gen7", "7th gen": "gen7", "seventh generation": "gen7",
    "gen8": "gen8","gen 8": "gen8", "generation 8": "gen8", "8th gen": "gen8", "eighth generation": "gen8",
    "gen9": "gen9","gen 9": "gen9", "generation 9": "gen9", "9th gen": "gen9", "ninth generation": "gen9",
}



# Load the small English model
nlp = spacy.load("en_core_web_sm")

def normalize_generation(text: str) -> Optional[str]:
    cleaned = text.strip().lower()
    return GENERATION_ALIASES.get(cleaned)


def normalize_tier(text: str) -> Optional[str]:
    cleaned = text.strip().lower()
    return ALL_TIERS.get(cleaned)


# def extract_species_tier_gen(user_input: str, ALL_SPECIES: List[str], valid_tiers: set):
#     doc = nlp(user_input.lower())
#     pokemon = None
#     tier = None
#     gen = None

#     for token in doc:
#         if token.text.title() in ALL_SPECIES:
#             pokemon = token.text.title()
#         elif token.text.lower() in valid_tiers:
#             tier = token.text.lower()
#         elif token.text.lower().startswith("gen") and token.text[3:].isdigit():
#             gen = token.text.lower()

#     return pokemon, tier, gen

def extract_species_tier_gen(user_input: str):
    user_input = user_input.lower()
    print(f"[DEBUG] User input: {user_input}")
    doc = nlp(user_input)

    pokemon_list = []
    tier = None
    gen = None

    # 1. Match Pokémon name (title-case match against ALL_SPECIES)
    for token in doc:
        candidate = token.text.title()
        if candidate in ALL_SPECIES and candidate not in pokemon_list:
            pokemon_list.append(candidate)

    # 2. Match tier (using aliases)
    for phrase in ALL_TIERS:
        # print(f"[DEBUG] Checking for tier phrase: {phrase}")
        if re.search(rf"\b{re.escape(phrase)}\b", user_input):
            tier = ALL_TIERS[phrase]
            break

    # 3. Match generation (using aliases)
    for phrase in GENERATION_ALIASES:
        if phrase in user_input:
            gen = GENERATION_ALIASES[phrase]
            break
    # print(f"[DEBUG] Extracted: Pokémon={pokemon}, Tier={tier}, Gen={gen}")
    return pokemon_list, tier, gen


# def extract_species_and_tier(user_input, all_species, valid_tiers):
#     doc = nlp(user_input.lower()) # Process the input text with spaCy
#     # Convert all species to lowercase for case-insensitive matching
#     pokemon = None
#     tier = None

#     for token in doc:
#         if token.text.title() in all_species:
#             pokemon = token.text.title()
#         elif token.text.lower() in valid_tiers:
#             tier = token.text.lower()

#     return pokemon, tier

DATA_DIR = "smogon/data"
ANALYSES_DIR = os.path.join(DATA_DIR, "analyses")

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# def search_teams(params: TeamSearchInput):
#     query = params.query
#     sample_size = params.sample_size or 3
#     """Search teams containing the given Pokémon, optionally filtered by gen and tier."""
#     # Create case-insensitive maps for species and tiers
#     # This allows us to match user input regardless of case
#     matches = []

#     pokemon_list, tier, gen = extract_species_tier_gen(query)
#     if not pokemon_list:
#         return []
#     for filename in os.listdir(DATA_DIR):
#         if not filename.endswith(".json"):
#             continue
#         # print(f"[DEBUG] Checking file: {filename}")
#         # Filter by gen and/or tier if specified
#         filename_no_ext = filename.replace(".json", "").lower()
#         # print(f"[DEBUG] Processing file: {filename_no_ext}")
#         if gen and not filename_no_ext.startswith(gen.lower()):
#             continue
#         if tier and tier.lower() not in filename_no_ext:
#             continue

#         filepath = os.path.join(DATA_DIR, filename)
#         # print(f"[DEBUG] Loading teams from: {filepath}")
#         try:
#             teams = load_json(filepath)
#         except Exception as e:
#             print(f"Error reading {filename}: {e}")
#             continue

#         for team in teams:
#             pokemon_in_team = {entry.get("species", "").lower() for entry in team.get("data", [])}
#             if all(p.lower() in pokemon_in_team for p in pokemon_list): # Check if all Pokémon in the query are in the team
#                 matches.append({
#                     "file": filename,
#                     "team_name": team.get("name", "Unnamed Team"),
#                     "author": team.get("author", "Unknown"),
#                     "team": team.get("data", []),
#                     "pokemonShowdownExport": create_pokemon_showdown_export(team.get("data", []))
#                 })

#     # Return a random sample of matches
#     # return random.sample(matches, min(sample_size, len(matches)))
#     return matches[:sample_size]
def search_teams(*, query: str, sample_size: int = 3) -> AllTeamSearchResult:
    params = TeamSearchInput(query=query, sample_size=sample_size)
    query = params.query
    sample_size = params.sample_size or 3
    matches = []

    pokemon_list, tier, gen = extract_species_tier_gen(query)
    if not pokemon_list or not isinstance(pokemon_list, list):
        return AllTeamSearchResult(teams=[])

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue

        filename_no_ext = filename.replace(".json", "").lower()
        if gen and not filename_no_ext.startswith(gen.lower()):
            continue
        if tier and tier.lower() not in filename_no_ext:
            continue

        filepath = os.path.join(DATA_DIR, filename)
        try:
            teams = load_json(filepath)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        for team in teams:
            pokemon_in_team = {entry.get("species", "").lower() for entry in team.get("data", []) if "species" in entry}
            if all(p.lower() in pokemon_in_team for p in pokemon_list):
                # Convert raw team data dicts into TeamPokemon models
                team_pokemon = []
                for p in team.get("data", []):
                    team_pokemon.append(TeamPokemon(
                        species=p.get("species"),
                        gender=p.get("gender"),
                        item=p.get("item"),
                        ability=p.get("ability"),
                        evs=p.get("evs"),
                        ivs=p.get("ivs"),
                        nature=p.get("nature"),
                        moves=p.get("moves") or []
                    ))

                team_result = TeamSearchResult(
                    file=filename,
                    team_name=team.get("name", "Unnamed Team"),
                    author=team.get("author", "Unknown"),
                    team=team_pokemon,
                    pokemonShowdownExport=create_pokemon_showdown_export(team.get("data", []))
                )
                matches.append(team_result)

    # Limit results to sample_size
    limited_matches = matches[:sample_size]

    # Wrap all results in AllTeamSearchResult
    return AllTeamSearchResult(teams=limited_matches)


def search_pokemon_analysis(query: str, gen: str) -> Optional[str]:
    """Search the gen9.json analysis file for a Pokémon and return its set descriptions."""
    filepath = os.path.join("smogon", "data", "analyses", f"{gen}.json") if gen else All_POKEMON_PATH
    data = load_json(filepath)

    for species_name, mon_data in data.items():
        if query.lower() == species_name.lower():
            strategies = []
            for tier_name, tier_data in mon_data.items():
                sets = tier_data.get("sets", {})
                for set_name, set_data in sets.items():
                    desc = set_data.get("description")
                    if desc:
                        strategies.append(
                            f"🛡️ **{species_name} | {tier_name.upper()} | {set_name}**\n{desc.strip()}"
                        )
            return "\n\n".join(strategies) if strategies else f"No strategy descriptions found for {query.title()}."
    return None

# When the LLM returns plain text, the AI agent can interpret and respond to it flexibly — meaning it can:

# Follow system prompt guidance (like “use markdown” or “summarize the strengths”),

# Write natural language answers with explanations, formatting, emoji, etc.,

# Include helpful context, reasoning, or additional suggestions.

def combined_smogon_search(query: str) -> str:
    # Create case-insensitive maps for species and tiers
    # This allows us to match user input regardless of case
    query = query.lower()
    pokemon_list, tier, gen = extract_species_tier_gen(query)
    if len(pokemon_list) > 1:
        return "❌ Please ask about only **one Pokémon** at a time for strategy lookup."

    if not pokemon_list:
        return "❌ I couldn't find a valid Pokémon name in your query."
    
    pokemon = pokemon_list[0].title()
    # All_POKEMON_PATH
    genpath = os.path.join("smogon", "data", "analyses", f"{gen}.json") if gen else All_POKEMON_PATH
    print(f"[DEBUG] Using analysis file: {genpath}")
    data = load_pokemon_analysis(genpath)
    if not pokemon:
        return "Sorry, I couldn't find any Pokémon mentioned in your query."
    pokemon = pokemon.title()  # Ensure we use the correct case for species names
    if tier:
        # Use smogon_team_analysis logic for tier-specific output
        tiers = data.get(pokemon, {})
        if tier not in tiers:
            return f"No analysis found for {pokemon} in tier {tier.upper()}."
        tier_data = tiers[tier]
        sets = tier_data.get("sets", {})
        if not sets:
            return f"{pokemon} has no available sets in {tier.upper()}."
        output = [f"Strategy for {pokemon} in {tier.upper()}:"]
        for set_name, set_data in sets.items():
            desc = set_data.get("description", "No description available.")
            output.append(f"🛡️ **{pokemon} | {tier.upper()} | {set_name}**\n{desc.strip()}")
        comments = tier_data.get("comments", "No author comments available.")
        if not comments:
            return f"{pokemon} has no available comments in {tier.upper()}."
        else:
            output.append(f"\n💬 **Author Comments**:\n{comments}")
        credits = tier_data.get("credits")
        if credits:
            writers = ", ".join(u["username"] for u in credits.get("writtenBy", []))
            teams = []
            for team in credits.get("teams", []):
                team_name = team.get("name", "Unknown team")
                members = ", ".join(m["username"] for m in team.get("members", []))
                teams.append(f"{team_name}: {members}")
            
            output.append("\n\n📝 **Credits**:")
            if writers:
                output.append(f"- Written by: {writers}")
            for team_info in teams:
                output.append(f"- {team_info}")
        return "\n".join(output)

    else:
        # No tier specified, return all sets across all tiers (use your simpler function)
        result = search_pokemon_analysis(pokemon, gen)
        return result or f"No analysis available for {pokemon}."

def save_to_txt(data: str, filename: str = "poke_output.txt"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    formatted_text = f"--- Pokemon Research Output ---\nTimestamp: {timestamp}\n\n{data}\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Data saved to {filename} at {timestamp}"

def create_pokemon_showdown_export(team_data: list) -> str:
    lines = []

    for mon in team_data:
        name = mon.get("species", "Unknown")
        item = mon.get("item", "")
        ability = mon.get("ability", "")
        tera_type = mon.get("tera_type", "")
        nature = mon.get("nature", "")
        evs = mon.get("evs", {})
        moves = mon.get("moves", [])

        # First line: "Pokemon @ Item"
        lines.append(f"{name} @ {item}" if item else name)

        # Ability
        if ability:
            lines.append(f"Ability: {ability}")

        # EVs
        if evs:
            ev_parts = [f"{val} {stat}" for stat, val in evs.items() if val > 0]
            if ev_parts:
                lines.append(f"EVs: {' / '.join(ev_parts)}")

        # Tera Type
        if tera_type:
            lines.append(f"Tera Type: {tera_type}")

        # Nature
        if nature:
            lines.append(f"{nature} Nature")

        # Moves
        for move in moves:
            if move:
                lines.append(f"- {move}")

        # Add a blank line between Pokémon
        lines.append("")

    return "\n".join(lines).strip()


smogon_tool = Tool(
    name="smogon_strategy_lookup",
    func=combined_smogon_search,
    description="Use this tool to search for Pokémon strategies, moves and analyses from Smogon data based on user queries."
)

team_search_tool = StructuredTool.from_function(
    name="search_teams_by_pokemon",
    func=search_teams,
    description= "Use this tool to find full Pokémon teams that include certain Pokémon names, from saved team files.",
    args_schema=TeamSearchInput, #Automatically parse the query input inside the TeamSearchInput model
)


save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Save text data to a file.",
)

search = DuckDuckGoSearchRun()
ddgo_tool = Tool(
    name="search_web",
    func=search.run,
    description="When you need to answer general questions about current events or general knowledge in pokemon. Input should be a search query.",
)


# api_wrapper = WikipediaAPIWrapper(top_k_result = 1, doc_content_chars_max=100)
# wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# need to fix the output so that it's not text but a json style output