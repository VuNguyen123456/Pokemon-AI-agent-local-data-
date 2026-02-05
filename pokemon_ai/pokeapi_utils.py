"""
Pokemon API utilities for interacting with PokeAPI (https://pokeapi.co/).

This module provides helper functions for:
- Normalizing Pokemon names for PokeAPI format
- Converting sprite filenames to API-compatible names
- Handling special forms and variants
"""

from typing import Tuple, Optional
import requests
import logging

logger = logging.getLogger(__name__)

# PokeAPI base URL
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


def normalize_pokemon_name_for_api(sprite_filename: str) -> Tuple[str, str]:
    """
    Convert sprite filename to PokeAPI format.
    
    Args:
        sprite_filename: Filename like "charizard-megax.png" or "pikachu.png"
    
    Returns:
        Tuple of (api_name, base_name) where:
        - api_name: Name formatted for PokeAPI (e.g., "charizard-mega-x")
        - base_name: Base Pokemon name for fallback (e.g., "charizard")
    
    Examples:
        >>> normalize_pokemon_name_for_api("charizard-megax.png")
        ("charizard-mega-x", "charizard")
        >>> normalize_pokemon_name_for_api("pikachu.png")
        ("pikachu", "pikachu")
    """
    # Remove .png extension
    name = sprite_filename.replace('.png', '').lower()
    
    # Handle special cases for PokeAPI
    # PokeAPI uses formats like: charizard-mega-x, charizard-mega-y
    # But our sprites might be: charizard-megax, charizard-megay
    name = name.replace('-megax', '-mega-x')
    name = name.replace('-megay', '-mega-y')
    
    # Handle other common variations
    name = name.replace('-gmax', '-gigantamax')
    
    # Extract base name for fallback (remove all suffixes after first hyphen if it's a form)
    # This helps with mega evolutions and other forms
    base_name = name.split('-')[0] if '-' in name else name
    
    return name, base_name


def get_pokemon_api_url(pokemon_name: str) -> str:
    """
    Get the PokeAPI URL for a Pokemon.
    
    Args:
        pokemon_name: Pokemon name in PokeAPI format (e.g., "charizard-mega-x")
    
    Returns:
        Full API URL for the Pokemon
    """
    return f"{POKEAPI_BASE_URL}/pokemon/{pokemon_name}"


def fetch_pokemon_data(pokemon_name: str, base_name: Optional[str] = None) -> Optional[dict]:
    """
    Fetch Pokemon data from PokeAPI.
    
    Args:
        pokemon_name: Pokemon name in PokeAPI format
        base_name: Optional base name to try as fallback if pokemon_name fails
    
    Returns:
        Pokemon data dictionary from API, or None if not found
    
    Example:
        >>> data = fetch_pokemon_data("charizard-mega-x", "charizard")
        >>> if data:
        ...     print(data['name'])
    """
    try:
        # Try the full name first
        url = get_pokemon_api_url(pokemon_name)
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        
        # If not found and base_name provided, try base name
        if base_name and base_name != pokemon_name:
            logger.info(f"Pokemon '{pokemon_name}' not found, trying base name '{base_name}'")
            url = get_pokemon_api_url(base_name)
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
        
        logger.warning(f"Pokemon not found: {pokemon_name} (base: {base_name})")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Pokemon data for '{pokemon_name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching Pokemon data: {e}")
        return None


def extract_pokemon_stats(api_data: dict) -> dict:
    """
    Extract stats from PokeAPI response data.
    
    Args:
        api_data: Pokemon data dictionary from PokeAPI
    
    Returns:
        Dictionary with stat names and values
    
    Example:
        >>> data = fetch_pokemon_data("pikachu")
        >>> stats = extract_pokemon_stats(data)
        >>> print(stats['hp'])
    """
    if not api_data or 'stats' not in api_data:
        return {}
    
    stat_names = {
        'hp': 'HP',
        'attack': 'Attack',
        'defense': 'Defense',
        'special-attack': 'Sp. Atk',
        'special-defense': 'Sp. Def',
        'speed': 'Speed'
    }
    
    stats = {}
    for stat_entry in api_data['stats']:
        stat_name = stat_entry['stat']['name']
        stat_value = stat_entry['base_stat']
        display_name = stat_names.get(stat_name, stat_name)
        stats[display_name] = stat_value
    
    return stats


def get_pokemon_artwork_url(api_data: dict) -> Optional[str]:
    """
    Get the official artwork URL from PokeAPI data.
    
    Args:
        api_data: Pokemon data dictionary from PokeAPI
    
    Returns:
        URL to official artwork, or None if not available
    """
    if not api_data or 'sprites' not in api_data:
        return None
    
    sprites = api_data['sprites']
    
    # Try official artwork first
    if 'other' in sprites and 'official-artwork' in sprites['other']:
        return sprites['other']['official-artwork'].get('front_default')
    
    # Fallback to regular front sprite
    if 'front_default' in sprites:
        return sprites['front_default']
    
    # Fallback to dream world
    if 'other' in sprites and 'dream_world' in sprites['other']:
        return sprites['other']['dream_world'].get('front_default')
    
    return None

