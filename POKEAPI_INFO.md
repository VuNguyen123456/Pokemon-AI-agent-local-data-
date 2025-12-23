# PokeAPI Information

## API Structure

PokeAPI (https://pokeapi.co/) is a RESTful API that provides Pokemon data.

### Base URL
```
https://pokeapi.co/api/v2
```

### Main Endpoints

#### 1. Pokemon Endpoint
```
GET /pokemon/{id or name}
```

**Example:**
- `https://pokeapi.co/api/v2/pokemon/charizard`
- `https://pokeapi.co/api/v2/pokemon/6`
- `https://pokeapi.co/api/v2/pokemon/charizard-mega-x`

**Response Structure (Key Fields):**
```json
{
  "id": 6,
  "name": "charizard",
  "base_experience": 267,
  "height": 6,              // Height in decimetres (divide by 10 for meters)
  "weight": 905,            // Weight in hectograms (divide by 10 for kg)
  "is_default": true,       // Whether this is the default form
  "order": 56,              // Sort order
  "abilities": [            // Array of possible abilities
    {
      "is_hidden": false,
      "slot": 1,
      "ability": {
        "name": "blaze",
        "url": "https://pokeapi.co/api/v2/ability/66/"
      }
    }
  ],
  "stats": [                // Array of base stats
    {
      "base_stat": 78,      // The stat value
      "effort": 0,          // EV yield
      "stat": {
        "name": "hp",       // Stat name: hp, attack, defense, special-attack, special-defense, speed
        "url": "https://pokeapi.co/api/v2/stat/1/"
      }
    }
  ],
  "types": [                // Array of types
    {
      "slot": 1,
      "type": {
        "name": "fire",
        "url": "https://pokeapi.co/api/v2/type/10/"
      }
    },
    {
      "slot": 2,
      "type": {
        "name": "flying",
        "url": "https://pokeapi.co/api/v2/type/3/"
      }
    }
  ],
  "sprites": {
    "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png",
    "back_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/6.png",
    "other": {
      "official-artwork": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png"
      },
      "dream_world": {
        "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/dream-world/6.svg"
      }
    }
  },
  "species": {
    "name": "charizard",
    "url": "https://pokeapi.co/api/v2/pokemon-species/6/"
  },
  "moves": [...],           // Array of moves with learn methods
  "forms": [...],           // Array of forms this Pokemon can take
  "game_indices": [...],    // Game indices by generation
  "held_items": [...],      // Items this Pokemon may hold
  "location_area_encounters": "/api/v2/pokemon/6/encounters"
}
```

### Stat Names Mapping

The API uses these stat names (from the `stat.name` field):
- `hp` → Display as "HP"
- `attack` → Display as "Attack"
- `defense` → Display as "Defense"
- `special-attack` → Display as "Sp. Atk"
- `special-defense` → Display as "Sp. Def"
- `speed` → Display as "Speed"

**Stat Structure:**
```json
{
  "base_stat": 78,        // The actual stat value
  "effort": 0,            // EV yield when defeated
  "stat": {
    "name": "hp",         // Stat name (use this for mapping)
    "url": "https://pokeapi.co/api/v2/stat/1/"
  }
}
```

### Pokemon Name Formats

PokeAPI uses lowercase names with hyphens:
- Base forms: `charizard`, `pikachu`, `garchomp`
- Mega evolutions: `charizard-mega-x`, `charizard-mega-y`
- Gigantamax: `charizard-gigantamax`
- Regional forms: `charizard-alola`, `charizard-galar`
- Other forms: `deoxys-attack`, `deoxys-defense`, `deoxys-speed`

### Important Notes

1. **Name Normalization**: Our sprite filenames use formats like `charizard-megax.png`, but PokeAPI uses `charizard-mega-x`. The `normalize_pokemon_name_for_api()` function handles this conversion.

2. **Fallback Strategy**: If a form-specific name fails (e.g., `charizard-mega-x`), we fall back to the base name (`charizard`).

3. **Not All Forms Available**: Some mega evolutions and special forms may not be available in PokeAPI. The API will return a 404 error for these.

4. **Rate Limiting**: PokeAPI has rate limiting. Be mindful of making too many requests.

### Example Usage

```javascript
// Fetch Pokemon data
fetch('https://pokeapi.co/api/v2/pokemon/charizard')
  .then(response => response.json())
  .then(data => {
    console.log('Name:', data.name);
    console.log('Stats:', data.stats);
    console.log('Artwork:', data.sprites.other['official-artwork'].front_default);
  });
```

### Python Usage (via pokeapi_utils.py)

```python
from pokeapi_utils import fetch_pokemon_data, extract_pokemon_stats

# Fetch data
data = fetch_pokemon_data("charizard-mega-x", "charizard")
if data:
    stats = extract_pokemon_stats(data)
    print(stats)  # {'HP': 78, 'Attack': 130, ...}
```

