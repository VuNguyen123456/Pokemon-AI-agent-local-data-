"""
Shared utilities and classes used across the application.
This module centralizes common functionality to avoid duplication.
"""
import re
import logging
from typing import List, Optional, Set, Tuple
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, LOG_LEVEL, LOG_FILE

# Configure logging once for the entire application
def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ],
        force=True  # Override any existing configuration
    )
    return logging.getLogger(__name__)

logger = setup_logging()


class SmartMemoryManager:
    """Manages conversation memory with topic-based retention."""
    
    def __init__(self, max_unrelated_queries: int = 5, max_topics: int = 10):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True, 
            input_key="query"
        )
        self.current_topics: Set[str] = set()
        self.unrelated_query_count = 0
        self.max_unrelated_queries = max_unrelated_queries
        self.max_topics = max_topics
        
    def should_clear_memory(self, new_pokemon_list: List[str]) -> bool:
        """Determine if memory should be cleared based on topic changes."""
        new_topics = set(new_pokemon_list) if new_pokemon_list else set()
        
        # If completely new topics (no overlap), consider clearing
        if new_topics and not new_topics.intersection(self.current_topics):
            self.unrelated_query_count += 1
            # Only clear if we've had several unrelated queries
            if self.unrelated_query_count >= self.max_unrelated_queries:
                return True
        else:
            # Related query, reset counter
            self.unrelated_query_count = 0
        
        return False
    
    def update_topics(self, pokemon_list: List[str]):
        """Update current conversation topics."""
        new_topics = set(pokemon_list) if pokemon_list else set()
        
        if new_topics:
            self.current_topics.update(new_topics)
            # Keep only recent topics
            if len(self.current_topics) > self.max_topics:
                # Convert to list, keep last N, convert back to set
                topics_list = list(self.current_topics)
                self.current_topics = set(topics_list[-self.max_topics:])
    
    def clear(self):
        """Clear memory and reset topic tracking."""
        self.memory.clear()
        self.current_topics.clear()
        self.unrelated_query_count = 0
        logger.info("Memory cleared")


def select_prompt(query: str, strat_prompt_team, strat_prompt_multi, strat_prompt_single, general_prompt, pokemon_list: List[str] = None):
    """
    Select the appropriate prompt based on query content.
    
    Improvements:
    1. Expanded team keywords (squad, lineup, comp, roster, teammates, partners)
    2. Expanded comparison keywords (versus, difference, compared to)
    3. Expanded strategy keywords (set, spread, EVs, IVs, nature, tera type)
    4. Direct detection of multiple Pokémon (if 2+ Pokémon found, use comparison)
    5. Better keyword matching for team-related queries
    """
    try:
        query_lower = query.lower()
        
        # IMPROVEMENT #4: If multiple Pokémon detected, use comparison prompt
        if pokemon_list and len(pokemon_list) > 1:
            return strat_prompt_multi
        
        # IMPROVEMENT #1: Expanded team keywords
        team_keywords = r"\b(team(s|ing)?|squad(s)?|lineup(s)?|comp(s|osition)?|roster(s)?|composition(s)?|teammate(s)?|partner(s)?|works?\s+with)\b"
        if re.search(team_keywords, query, re.IGNORECASE):
            return strat_prompt_team
        
        # IMPROVEMENT #2: Expanded comparison keywords and better detection
        comparison_keywords = r"\b(strategy|build|moveset|compare|vs|versus|difference|compared\s+to|versus)\b"
        has_comparison_keyword = re.search(comparison_keywords, query, re.IGNORECASE)
        
        # More flexible separators for multi-Pokémon
        separators = [" and ", ",", " or ", " vs ", " versus ", " compared to ", " versus "]
        has_separator = any(sep in query_lower for sep in separators)
        
        if has_comparison_keyword and has_separator:
            return strat_prompt_multi
        
        # IMPROVEMENT #3: Expanded strategy keywords
        strategy_keywords = r"\b(strategy|build|weakness|strength|moves?|items?|abilities?|set|spread|evs?|ivs?|nature|tera\s+type|how\s+to\s+use|how\s+to\s+play|best\s+.*\s+for)\b"
        if re.search(strategy_keywords, query, re.IGNORECASE):
            return strat_prompt_single
        
        # Default to general
        return general_prompt
    except Exception as e:
        logger.warning(f"Error in prompt selection, using general: {e}")
        return general_prompt


def create_agent_executor(llm: ChatOpenAI, prompt, tools, memory, verbose: bool = False):
    """Create and configure an agent executor."""
    try:
        agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=15
        )
        return agent_executor
    except Exception as e:
        logger.error(f"Error creating agent executor: {e}", exc_info=True)
        raise


def format_agent_response(response, fix_markdown_func, format_multiple_teams_func) -> Tuple[str, bool, any]:
    """Format agent response and determine if it's a team output.
    Returns: (formatted_output, is_team_output, raw_team_result)
    """
    try:
        from models import AllTeamSearchResult
        
        # Extract output from response
        if isinstance(response, dict) and 'output' in response:
            output = response['output']
        else:
            output = response
        
        # Check if the response itself is AllTeamSearchResult
        if isinstance(response, AllTeamSearchResult):
            formatted_output = format_multiple_teams_func(response.teams)
            return formatted_output, True, response
        
        # Check if the extracted output is AllTeamSearchResult
        if isinstance(output, AllTeamSearchResult):
            formatted_output = format_multiple_teams_func(output.teams)
            return formatted_output, True, output
        
        # Not a team result
        formatted_output = fix_markdown_func(str(output))
        return formatted_output, False, None
    except Exception as e:
        logger.error(f"Error formatting response: {e}", exc_info=True)
        return "❌ An error occurred while formatting the response.", False, None


def format_strategy_markdown(output: str) -> str:
    """Format strategy output with markdown emojis."""
    try:
        # Replace \n with actual newlines
        output = output.replace("\\n", "\n")
        
        # Highlight section titles with emojis
        replacements = {
            "Moveset": "### 🧠 Moveset",
            "Role": "### 🛡️ Role",
            "Teammates": "### 🤝 Teammates",
            "Threats": "### ⚠️ Threats",
            "Tips": "### 💡 Tips"
        }
        
        for old, new in replacements.items():
            output = output.replace(old, new)
        
        return output.strip()
    except Exception as e:
        logger.error(f"Error formatting markdown: {e}")
        return output


def get_pokemon_sprite_urls(text: str, all_species: List[str], all_filenames: List[str], sprite_base_url: str, max_pokemon: int = 6) -> List[List[str]]:
    """Get Pokémon sprite URLs from text, returning a list of lists (one per Pokémon)."""
    try:
        import re
        text_lower = text.lower()
        matched_species = []
        
        for species in all_species:
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
                # Escape special regex characters in the name
                patterns = [
                    r'\b' + re.escape(name) + r'\b',  # original format
                    r'\b' + re.escape(name_with_space) + r'\b',  # with spaces
                    r'\b' + re.escape(name_with_hyphen) + r'\b',  # with hyphens
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        matches = True
                        break
            else:
                # For single-word Pokemon, use word boundary to avoid substring matches
                # e.g., "char" won't match "charizard", "pika" won't match "pikachu"
                pattern = r'\b' + re.escape(name) + r'\b'
                matches = bool(re.search(pattern, text_lower))
            
            if matches and name not in matched_species:
                matched_species.append(name)
                if len(matched_species) >= max_pokemon:
                    break
        
        result = []
        for matched_name in matched_species:
            # Find sprites - match filenames that start with the Pokemon name
            image_urls = []
            
            for filename in all_filenames:
                filename_lower = filename.lower().replace('.png', '')
                # Check if filename starts with the matched name
                if filename_lower.startswith(matched_name):
                    image_urls.append(f"{sprite_base_url}{filename}")
                elif ' ' in matched_name or '-' in matched_name:
                    # For multi-word names, also check variations (space/hyphen)
                    name_variations = [
                        matched_name.replace('-', ' '),
                        matched_name.replace(' ', '-'),
                    ]
                    for variation in name_variations:
                        if filename_lower.startswith(variation):
                            image_urls.append(f"{sprite_base_url}{filename}")
                            break
            
            result.append(image_urls)
        
        return result
    except Exception as e:
        logger.error(f"Error getting Pokémon sprite URLs: {e}")
        return []


def fix_markdown_headers_spacing(text: str) -> str:
    """
    Ensure that markdown headers like #, ##, ### are preceded by two newlines
    so they render properly after paragraphs.
    """
    return re.sub(r"(?<!\n)\s*(?=#+\s)", r"\n\n", text)

