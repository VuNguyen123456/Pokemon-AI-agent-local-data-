"""
Pokémon AI Agent - Core Package

This package contains the core modules for the Pokémon AI Agent:
- config: Configuration and path management
- models: Pydantic data models
- shared: Shared utilities and agent creation
- tools: LangChain tools for the agent
- utils: Utility functions for formatting and data processing
- pokeapi_utils: PokeAPI integration utilities
"""

__version__ = "1.0.0"

# Import from config
from .config import (
    BASE_DIR,
    SMOGON_BASE_DIR,
    DATA_DIR,
    ANALYSES_DIR,
    DEFAULT_ANALYSIS_FILE,
    OUTPUT_DIR,
    DEFAULT_OUTPUT_FILE,
    SPRITE_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    get_analysis_file_path,
    validate_paths
)

# Import from models
from .models import (
    TeamPokemon,
    TeamSearchResult,
    AllTeamSearchResult
)

# Import from shared
from .shared import (
    logger,
    SmartMemoryManager,
    select_prompt,
    create_agent_executor,
    format_agent_response,
    format_strategy_markdown,
    get_pokemon_sprite_urls,
    fix_markdown_headers_spacing
)

# Import from tools
from .tools import (
    ddgo_tool,
    save_tool,
    clean_smogon_tool,
    team_search_tool,
    ALL_SPECIES,
    extract_species_tier_gen,
    TeamSearchInput
)

# Import from utils
from .utils import (
    general_prompt,
    strat_prompt_single,
    strat_prompt_team,
    strat_prompt_multi,
    format_strategy_team_output,
    format_multiple_teams_output,
    ALL_FILENAMES
)

# Import from pokeapi_utils
from .pokeapi_utils import (
    normalize_pokemon_name_for_api
)

__all__ = [
    # Config
    "BASE_DIR",
    "SMOGON_BASE_DIR",
    "DATA_DIR",
    "ANALYSES_DIR",
    "DEFAULT_ANALYSIS_FILE",
    "OUTPUT_DIR",
    "DEFAULT_OUTPUT_FILE",
    "SPRITE_BASE_URL",
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "get_analysis_file_path",
    "validate_paths",
    # Models
    "TeamPokemon",
    "TeamSearchResult",
    "AllTeamSearchResult",
    # Shared
    "logger",
    "SmartMemoryManager",
    "select_prompt",
    "create_agent_executor",
    "format_agent_response",
    "format_strategy_markdown",
    "get_pokemon_sprite_urls",
    "fix_markdown_headers_spacing",
    # Tools
    "ddgo_tool",
    "save_tool",
    "clean_smogon_tool",
    "team_search_tool",
    "ALL_SPECIES",
    "extract_species_tier_gen",
    "TeamSearchInput",
    # Utils
    "general_prompt",
    "strat_prompt_single",
    "strat_prompt_team",
    "strat_prompt_multi",
    "format_strategy_team_output",
    "format_multiple_teams_output",
    "ALL_FILENAMES",
    # PokeAPI Utils
    "normalize_pokemon_name_for_api",
]
