import os
import json
import re
import logging
from typing import List, Optional
from datetime import datetime
from langchain.tools import Tool, StructuredTool
from langchain_community.tools import DuckDuckGoSearchRun
import spacy
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
from models import AllTeamSearchResult, TeamSearchResult, TeamPokemon
from config import (
    DATA_DIR, ANALYSES_DIR, DEFAULT_ANALYSIS_FILE, OUTPUT_DIR, DEFAULT_OUTPUT_FILE,
    get_analysis_file_path, validate_paths
)
from shared import fix_markdown_headers_spacing

# Set up logging
logger = logging.getLogger(__name__)

class TeamSearchInput(BaseModel):
    query: str = Field(..., description="Search query with Pokémon name and optional tier/gen info")
    sample_size: Optional[int] = Field(3, description="Number of results to return")

def load_pokemon_analysis(filepath) -> dict:
    """Load Pokémon analysis data from JSON file with error handling."""
    try:
        if not os.path.exists(filepath):
            logger.error(f"Analysis file not found: {filepath}")
            raise FileNotFoundError(f"Analysis file not found: {filepath}")
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded analysis file: {filepath}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {filepath}: {e}")
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")
    except Exception as e:
        logger.error(f"Error loading analysis file {filepath}: {e}")
        raise

# Validate paths on import
_path_validation = validate_paths()
if not _path_validation["valid"]:
    logger.warning("Path validation failed. Some features may not work:")
    for error in _path_validation["errors"]:
        logger.warning(f"  - {error}")

All_POKEMON_PATH = str(DEFAULT_ANALYSIS_FILE)

# Load ALL_SPECIES with error handling
try:
    ALL_SPECIES = list(load_pokemon_analysis(All_POKEMON_PATH).keys())
    logger.info(f"Loaded {len(ALL_SPECIES)} Pokémon species")
except Exception as e:
    logger.error(f"Failed to load Pokémon species list: {e}")
    ALL_SPECIES = []  # Fallback to empty list

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


# def strip_html(text: str) -> str:
#     """Strip HTML tags from text and return clean plain text."""
#     soup = BeautifulSoup(text, "html.parser")
#     return soup.get_text(separator="\n").strip()

def strip_html(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(separator="\n").strip()
    return re.sub(r"\n{2,}", "\n\n", clean)  # Collapse excessive newlines


def extract_species_tier_gen(user_input: str):
    """Extract Pokémon species, tier, and generation from user input with error handling."""
    try:
        user_input = user_input.lower()
        logger.debug(f"Extracting from user input: {user_input}")
        
        try:
            doc = nlp(user_input)
        except Exception as e:
            logger.error(f"Error processing input with spaCy: {e}")
            # Fallback to simple matching
            doc = None

        pokemon_list = []
        tier = None
        gen = None

        # 1. Match Pokémon name using robust regex-based matching (same as get_pokemon_sprite_urls)
        # This ensures we find all Pokemon mentioned, including multi-word ones
        for species in ALL_SPECIES:
            name = species.lower()
            
            # Check if this is a multi-word Pokemon (has space or hyphen)
            has_separator = ' ' in name or '-' in name
            
            matches = False
            
            if has_separator:
                # For multi-word Pokemon (like "great-tusk" or "great tusk"):
                # Try matching with both space and hyphen variations
                name_with_space = name.replace('-', ' ')
                name_with_hyphen = name.replace(' ', '-')
                
                # Use word boundaries to ensure we match the whole phrase
                patterns = [
                    r'\b' + re.escape(name) + r'\b',  # original format
                    r'\b' + re.escape(name_with_space) + r'\b',  # with spaces
                    r'\b' + re.escape(name_with_hyphen) + r'\b',  # with hyphens
                ]
                
                for pattern in patterns:
                    if re.search(pattern, user_input):
                        matches = True
                        break
            else:
                # For single-word Pokemon, use word boundary to avoid substring matches
                pattern = r'\b' + re.escape(name) + r'\b'
                matches = bool(re.search(pattern, user_input))
            
            if matches and species not in pokemon_list:
                pokemon_list.append(species)  # Keep original case from ALL_SPECIES

        # 2. Match tier (using aliases)
        for phrase in ALL_TIERS:
            try:
                if re.search(rf"\b{re.escape(phrase)}\b", user_input):
                    tier = ALL_TIERS[phrase]
                    break
            except re.error as e:
                logger.warning(f"Regex error for tier phrase '{phrase}': {e}")
                continue

        # 3. Match generation (using aliases)
        for phrase in GENERATION_ALIASES:
            if phrase in user_input:
                gen = GENERATION_ALIASES[phrase]
                break
        
        logger.debug(f"Extracted: Pokémon={pokemon_list}, Tier={tier}, Gen={gen}")
        return pokemon_list, tier, gen
    except Exception as e:
        logger.error(f"Unexpected error in extract_species_tier_gen: {e}", exc_info=True)
        return [], None, None


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

def load_json(filepath):
    """Load JSON file with error handling."""
    try:
        if not os.path.exists(filepath):
            logger.warning(f"JSON file not found: {filepath}")
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON file {filepath}: {e}")
        return None

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
    """Search for teams containing specific Pokémon with error handling."""
    try:
        params = TeamSearchInput(query=query, sample_size=sample_size)
        query = params.query
        sample_size = params.sample_size or 3
        matches = []

        pokemon_list, tier, gen = extract_species_tier_gen(query)
        if not pokemon_list or not isinstance(pokemon_list, list):
            logger.info(f"No Pokémon found in query: {query}")
            return AllTeamSearchResult(teams=[])

        if not DATA_DIR.exists():
            logger.error(f"Data directory not found: {DATA_DIR}")
            return AllTeamSearchResult(teams=[])

        try:
            files = os.listdir(DATA_DIR)
        except PermissionError as e:
            logger.error(f"Permission denied accessing {DATA_DIR}: {e}")
            return AllTeamSearchResult(teams=[])
        except Exception as e:
            logger.error(f"Error listing files in {DATA_DIR}: {e}")
            return AllTeamSearchResult(teams=[])

        for filename in files:
            if not filename.endswith(".json"):
                continue

            filename_no_ext = filename.replace(".json", "").lower()
            if gen and not filename_no_ext.startswith(gen.lower()):
                continue
            if tier and tier.lower() not in filename_no_ext:
                continue

            filepath = DATA_DIR / filename
            teams = load_json(str(filepath))
            
            if teams is None:
                continue
            
            if not isinstance(teams, list):
                logger.warning(f"Expected list in {filename}, got {type(teams)}")
                continue

            for team in teams:
                if not isinstance(team, dict):
                    logger.warning(f"Invalid team format in {filename}")
                    continue
                    
                pokemon_in_team = {entry.get("species", "").lower() for entry in team.get("data", []) if isinstance(entry, dict) and "species" in entry}
                if all(p.lower() in pokemon_in_team for p in pokemon_list):
                    # Convert raw team data dicts into TeamPokemon models
                    team_pokemon = []
                    for p in team.get("data", []):
                        if not isinstance(p, dict):
                            continue
                        try:
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
                        except Exception as e:
                            logger.warning(f"Error creating TeamPokemon: {e}")
                            continue

                    try:
                        team_result = TeamSearchResult(
                            file=filename,
                            team_name=team.get("name", "Unnamed Team"),
                            author=team.get("author", "Unknown"),
                            team=team_pokemon,
                            pokemonShowdownExport=create_pokemon_showdown_export(team.get("data", []))
                        )
                        matches.append(team_result)
                    except Exception as e:
                        logger.warning(f"Error creating TeamSearchResult: {e}")
                        continue

        # Limit results to sample_size
        limited_matches = matches[:sample_size]
        logger.info(f"Found {len(limited_matches)} teams for query: {query}")

        # Wrap all results in AllTeamSearchResult
        return AllTeamSearchResult(teams=limited_matches)
    except Exception as e:
        logger.error(f"Unexpected error in search_teams: {e}", exc_info=True)
        return AllTeamSearchResult(teams=[])


def search_pokemon_analysis(query: str, gen: Optional[str] = None) -> Optional[str]:
    """Search the analysis file for a Pokémon and return its set descriptions."""
    try:
        filepath = get_analysis_file_path(gen)
        data = load_pokemon_analysis(str(filepath))

        if not data:
            logger.warning(f"No data loaded from {filepath}")
            return None

        for species_name, mon_data in data.items():
            if query.lower() == species_name.lower():
                strategies = []
                if not isinstance(mon_data, dict):
                    continue
                for tier_name, tier_data in mon_data.items():
                    if not isinstance(tier_data, dict):
                        continue
                    sets = tier_data.get("sets", {})
                    if not isinstance(sets, dict):
                        continue
                    for set_name, set_data in sets.items():
                        if not isinstance(set_data, dict):
                            continue
                        desc = set_data.get("description")
                        if desc:
                            strategies.append(
                                f"🛡️ **{species_name} | {tier_name.upper()} | {set_name}**\n{desc.strip()}"
                            )
                return "\n\n".join(strategies) if strategies else f"No strategy descriptions found for {query.title()}."
        return None
    except Exception as e:
        logger.error(f"Error in search_pokemon_analysis: {e}", exc_info=True)
        return None

# When the LLM returns plain text, the AI agent can interpret and respond to it flexibly — meaning it can:

# Follow system prompt guidance (like “use markdown” or “summarize the strengths”),

# Write natural language answers with explanations, formatting, emoji, etc.,

# Include helpful context, reasoning, or additional suggestions.

def combined_smogon_search(query: str) -> str:
    """Search Smogon data for Pokémon strategy information with error handling."""
    try:
        query = query.lower()
        pokemon_list, tier, gen = extract_species_tier_gen(query)
        
        if len(pokemon_list) > 1:
            return "❌ Please ask about only **one Pokémon** at a time for strategy lookup."

        if not pokemon_list:
            return "❌ I couldn't find a valid Pokémon name in your query."
        
        pokemon = pokemon_list[0].title()
        genpath = get_analysis_file_path(gen)
        logger.debug(f"Using analysis file: {genpath}")
        
        try:
            data = load_pokemon_analysis(str(genpath))
        except Exception as e:
            logger.error(f"Failed to load analysis file {genpath}: {e}")
            return f"❌ Error loading analysis data. Please try again later."

        if not data:
            return "❌ Could not load Pokémon analysis data."

        pokemon = pokemon.title()  # Ensure we use the correct case for species names
        
        if tier:
            # Use smogon_team_analysis logic for tier-specific output
            if pokemon not in data:
                return f"❌ No analysis found for {pokemon}."
            
            tiers = data.get(pokemon, {})
            if not isinstance(tiers, dict):
                return f"❌ Invalid data format for {pokemon}."
            
            if tier not in tiers:
                return f"❌ No analysis found for {pokemon} in tier {tier.upper()}."
            
            tier_data = tiers[tier]
            if not isinstance(tier_data, dict):
                return f"❌ Invalid tier data for {pokemon} in {tier.upper()}."
            
            sets = tier_data.get("sets", {})
            if not sets or not isinstance(sets, dict):
                return f"❌ {pokemon} has no available sets in {tier.upper()}."
            
            output = [f"Strategy for {pokemon} in {tier.upper()}:"]
            for set_name, set_data in sets.items():
                if not isinstance(set_data, dict):
                    continue
                desc = set_data.get("description", "No description available.")
                output.append(f"🛡️ **{pokemon} | {tier.upper()} | {set_name}**\n{desc.strip()}")
            
            comments = tier_data.get("comments", "")
            if comments:
                output.append(f"\n💬 **Author Comments**:\n{comments}")
            
            credits = tier_data.get("credits")
            if credits and isinstance(credits, dict):
                writers = []
                if "writtenBy" in credits and isinstance(credits["writtenBy"], list):
                    writers = [u.get("username", "Unknown") for u in credits["writtenBy"] if isinstance(u, dict)]
                
                teams = []
                if "teams" in credits and isinstance(credits["teams"], list):
                    for team in credits["teams"]:
                        if isinstance(team, dict):
                            team_name = team.get("name", "Unknown team")
                            members_list = team.get("members", [])
                            if isinstance(members_list, list):
                                members = ", ".join(m.get("username", "Unknown") for m in members_list if isinstance(m, dict))
                                teams.append(f"{team_name}: {members}")
                
                if writers or teams:
                    output.append("\n\n📝 **Credits**:")
                    if writers:
                        output.append(f"- Written by: {', '.join(writers)}")
                    for team_info in teams:
                        output.append(f"- {team_info}")
            
            return "\n".join(output)
        else:
            # No tier specified, return all sets across all tiers
            result = search_pokemon_analysis(pokemon, gen)
            return result or f"❌ No analysis available for {pokemon}."
    except Exception as e:
        logger.error(f"Unexpected error in combined_smogon_search: {e}", exc_info=True)
        return "❌ An error occurred while searching for Pokémon strategy. Please try again."

def save_to_txt(data: str, filename: Optional[str] = None):
    """Save data to a text file with error handling."""
    try:
        if filename is None:
            filename = str(DEFAULT_OUTPUT_FILE)
        else:
            # If relative path, save to output directory
            if not os.path.isabs(filename):
                filename = str(OUTPUT_DIR / filename)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        formatted_text = f"--- Pokemon Research Output ---\nTimestamp: {timestamp}\n\n{data}\n"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, "a", encoding="utf-8") as f:
            f.write(formatted_text)
        
        logger.info(f"Data saved to {filename} at {timestamp}")
        return f"✅ Data saved to {filename} at {timestamp}"
    except PermissionError as e:
        logger.error(f"Permission denied writing to {filename}: {e}")
        return f"❌ Permission denied: Cannot write to {filename}"
    except Exception as e:
        logger.error(f"Error saving to file {filename}: {e}", exc_info=True)
        return f"❌ Error saving file: {str(e)}"

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

def clean_smogon_search(query: str) -> str:
    raw_output = combined_smogon_search(query)  # Your original HTML-returning function
    text_only = strip_html(raw_output)
    cleaned = fix_markdown_headers_spacing(text_only)
    return cleaned

clean_smogon_tool = Tool(
    name="clean_smogon_strategy_lookup",
    func=clean_smogon_search,
    description=(
        "Use this tool to search for Pokémon competitive strategies, movesets, builds, weaknesses, strengths, "
        "items, abilities, EVs, IVs, natures, and tera types from Smogon data. "
        "Returns clean text with HTML removed. "
        "Use this for ANY competitive strategy question about a specific Pokémon. "
        "DO NOT use this for team searches or general knowledge questions."
    ),
    return_direct=False
)

team_search_tool = StructuredTool.from_function(
    name="search_teams_by_pokemon",
    func=search_teams,
    description=(
        "Use this tool to find complete Pokémon teams (squads, lineups, compositions) that include certain Pokémon names. "
        "Use when user asks for: teams, squads, lineups, comps, rosters, 'what works with X', teammates, or partners. "
        "Returns full team data including all Pokémon, items, moves, EVs, and abilities from saved team files."
    ),
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
    description=(
        "Use this tool ONLY when: "
        "(1) The question is about current events, news, or recent updates in Pokémon, "
        "(2) The question cannot be answered from Smogon strategy data, "
        "(3) The question is about general Pokémon trivia not related to competitive play. "
        "DO NOT use this for strategy, moveset, build, team, or competitive questions - "
        "use clean_smogon_tool or team_search_tool instead. "
        "Input should be a search query string."
    ),
)