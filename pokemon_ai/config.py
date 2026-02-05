"""
Configuration file for Pokémon AI Agent.
All paths and settings are centralized here.
"""
import os
from pathlib import Path
from typing import Optional

# Base directory - can be overridden with environment variable
# Go up one level from pokemon_ai package to project root
BASE_DIR = Path(os.getenv("POKEMON_AI_BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Data directories
SMOGON_BASE_DIR = BASE_DIR / "smogon"
DATA_DIR = SMOGON_BASE_DIR / "data"
ANALYSES_DIR = DATA_DIR / "analyses"

# Default analysis file (Gen 9 contains all Pokémon)
DEFAULT_ANALYSIS_FILE = ANALYSES_DIR / "gen9.json"

# Output directory for saved files
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)  # Create if doesn't exist

# Default output filename
DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "poke_output.txt"

# Sprite base URL
SPRITE_BASE_URL = "https://play.pokemonshowdown.com/sprites/gen5/"

# Memory settings
MEMORY_MAX_TOKENS = int(os.getenv("MEMORY_MAX_TOKENS", "2000"))  # Max tokens to keep in memory
MEMORY_CLEAR_THRESHOLD = int(os.getenv("MEMORY_CLEAR_THRESHOLD", "10"))  # Clear after N unrelated queries

# Model settings
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "pokemon_ai.log"

# Create logs directory if it doesn't exist
LOG_FILE.parent.mkdir(exist_ok=True)

def get_analysis_file_path(gen: Optional[str] = None) -> Path:
    """Get the path to an analysis file for a specific generation."""
    if gen:
        return ANALYSES_DIR / f"{gen}.json"
    return DEFAULT_ANALYSIS_FILE

def validate_paths() -> dict:
    """Validate that all required paths exist. Returns dict with validation results."""
    results = {
        "valid": True,
        "errors": []
    }
    
    if not SMOGON_BASE_DIR.exists():
        results["valid"] = False
        results["errors"].append(f"Smogon base directory not found: {SMOGON_BASE_DIR}")
    
    if not DATA_DIR.exists():
        results["valid"] = False
        results["errors"].append(f"Data directory not found: {DATA_DIR}")
    
    if not ANALYSES_DIR.exists():
        results["valid"] = False
        results["errors"].append(f"Analyses directory not found: {ANALYSES_DIR}")
    
    if not DEFAULT_ANALYSIS_FILE.exists():
        results["valid"] = False
        results["errors"].append(f"Default analysis file not found: {DEFAULT_ANALYSIS_FILE}")
    
    return results

