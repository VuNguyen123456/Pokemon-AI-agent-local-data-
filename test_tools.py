import os
import pprint
import ast
from tools import TeamSearchInput, AllTeamSearchResult, TeamSearchResult

from tools import (
    smogon_tool,
    team_search_tool,
    save_tool,
    ddgo_tool
)

def test_smogon_tool():
    print("Testing Smogon Strategy Lookup:")
    query = "Give me some info on Charizard in zero used"
    result = smogon_tool.func(query)
    print(result)
    print("-" * 50)

def test_team_search_tool():
    print("Testing Team Search by Pokemon:")
    keyword = "Show me teams with Umbreon and chansEY"

    results: AllTeamSearchResult = team_search_tool.func(TeamSearchInput(query=keyword))
    if not results or not results.teams:
        print(f"No teams found with '{keyword}'")
        return

    print(f"Found {len(results.teams)} teams with '{keyword}'")
    print("-" * 50)

    for i, result in enumerate(results.teams, start=1):
        print(f"Team {i}:")
        print(f"  Source file: {result.file}")
        print(f"  Team name: {result.team_name}")
        print(f"  Author: {result.author}")
        print("  Pokémon in team:")
        for pokemon in result.team:
            print("    Pokémon details:")
            print(f"      species: {pokemon.species}")
            if pokemon.gender:
                print(f"      gender: {pokemon.gender}")
            if pokemon.item:
                print(f"      item: {pokemon.item}")
            if pokemon.ability:
                print(f"      ability: {pokemon.ability}")
            if pokemon.evs:
                print(f"      evs: {pokemon.evs}")
            if pokemon.ivs:
                print(f"      ivs: {pokemon.ivs}")
            if pokemon.nature:
                print(f"      nature: {pokemon.nature}")
            if pokemon.moves:
                print(f"      moves: {pokemon.moves}")
            print()
        print("-" * 50)
        print("  📝 Pokémon Showdown Export:")
        print(result.pokemonShowdownExport or "No export available")
        print("-" * 50)



def test_save_tool():
    print("Testing Save to File:")
    test_text = "This is a test save content from test script."
    message = save_tool.func(test_text, filename="test_output.txt")
    print(message)
    print("-" * 50)

def test_ddgo_tool():
    print("Testing DuckDuckGo Search (live API call):")
    query = "What is the difference between poison and deadly poison? in pokemon"
    try:
        results = ddgo_tool.func(query)
        print(results)
    except Exception as e:
        print(f"Error in DuckDuckGo tool: {e}")
    print("-" * 50)

# def test_wiki_tool():
#     print("Testing Wikipedia Query (live API call):")
#     query = "what does the item Choice Scarf do in Pokemon?"
#     try:
#         result = wiki_tool.run(query)
#         print(result)
#     except Exception as e:
#         print(f"Error in Wikipedia tool: {e}")
#     print("-" * 50)

if __name__ == "__main__":
    # test_smogon_tool()
    test_team_search_tool()
    # test_save_tool()
    # test_ddgo_tool()
    # test_wiki_tool()
