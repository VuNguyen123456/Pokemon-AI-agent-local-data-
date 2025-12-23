import sys
import re
from dotenv import load_dotenv

# Import shared utilities
from shared import (
    logger, SmartMemoryManager, select_prompt, create_agent_executor,
    format_agent_response, fix_markdown_headers_spacing
)

# Import tools and models
from tools import ddgo_tool, save_tool, clean_smogon_tool, team_search_tool, extract_species_tier_gen
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon 
from utils import general_prompt, strat_prompt_single, strat_prompt_team, strat_prompt_multi, format_strategy_team_output, format_multiple_teams_output

load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE
    llm = ChatOpenAI(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
    logger.info(f"Initialized LLM with model: {DEFAULT_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    print("❌ Failed to initialize AI model. Please check your configuration.")
    sys.exit(1)

tools = [ddgo_tool, save_tool, clean_smogon_tool, team_search_tool]
memory_manager = SmartMemoryManager()

def process_query(query: str) -> str:
    """Process a single query with error handling."""
    try:
        # Extract Pokémon, tier, and gen
        pokemon_list, tier, gen = extract_species_tier_gen(query)
        
        # Smart memory management
        if pokemon_list:
            if memory_manager.should_clear_memory(pokemon_list):
                logger.info(f"Clearing memory due to topic shift. New Pokémon: {pokemon_list}")
                memory_manager.clear()
            memory_manager.update_topics(pokemon_list)

        # Select prompt using shared function (now with Pokémon list for better detection)
        prompt = select_prompt(query, strat_prompt_team, strat_prompt_multi, strat_prompt_single, general_prompt, pokemon_list)

        # Create and execute agent
        try:
            agent_executor = create_agent_executor(
                llm=llm, 
                prompt=prompt, 
                tools=tools, 
                memory=memory_manager.memory
            )

            response = agent_executor.invoke({
                "query": query,
                "name": "Pokemon Research Assistant"
            })
        except Exception as e:
            logger.error(f"Error in agent execution: {e}", exc_info=True)
            return "❌ An error occurred while processing your query. Please try again or rephrase your question."

        # Format response using shared function
        output, _, _ = format_agent_response(
            response, 
            fix_markdown_headers_spacing, 
            format_multiple_teams_output
        )

        return output

    except KeyboardInterrupt:
        logger.info("User interrupted")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_query: {e}", exc_info=True)
        return "❌ An unexpected error occurred. Please try again later."

def main():
    """Main CLI loop."""
    print("🧠 Pokémon Strategy Assistant")
    print("=" * 50)
    print("Type 'quit' or 'exit' to stop\n")
    
    try:
        while True:
            try:
                query = input("\nHow can I help with Pokémon? ").strip()
                
                if not query:
                    continue
                    
                if re.search(r"\b(quit|exit)\b", query.lower()):
                    print("\n👋 Goodbye! Happy battling!")
                    break

                print("\n" + "=" * 50)
                response = process_query(query)
                print(response)
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Happy battling!")
                break
            except EOFError:
                print("\n\n👋 Goodbye! Happy battling!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                print(f"\n❌ An error occurred: {str(e)}")
                print("Please try again or type 'quit' to exit.")
                
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
