# showPokemonStats Function Documentation

## Location

The `showPokemonStats` function is defined in **`app.py`** at **line 976**, inside the `create_modern_sprites_html()` function.

## What It Does

`showPokemonStats` is a JavaScript function that displays a modal popup with Pokemon statistics fetched from PokeAPI when you click on a Pokemon sprite.

### Function Signature
```javascript
window.showPokemonStats(pokemonName, baseName)
```

**Parameters:**
- `pokemonName` (string): The Pokemon name in PokeAPI format (e.g., "charizard", "charizard-mega-x")
- `baseName` (string): The base Pokemon name for fallback if the form-specific name fails (e.g., "charizard")

## How It Works

1. **Creates/Shows Modal**: Creates a modal dialog if it doesn't exist, or shows the existing one
2. **Displays Loading State**: Shows "Loading stats..." message
3. **Fetches Data from PokeAPI**: Calls `fetchPokemon(pokemonName)` which makes an API request to:
   ```
   https://pokeapi.co/api/v2/pokemon/{pokemonName}
   ```
4. **Fallback Strategy**: If the form-specific name fails (e.g., "charizard-mega-x" not found), it tries the base name (e.g., "charizard")
5. **Displays Stats**: Parses the API response and displays:
   - Official artwork image
   - Base stats (HP, Attack, Defense, Sp. Atk, Sp. Def, Speed)
6. **Error Handling**: Shows an error message if the Pokemon can't be found

## Where It's Called

The function is called from the **onclick handler** on Pokemon sprite elements (line 1074 in `app.py`):

```html
<div class="pokemon-sprite-modern" onclick="window.showPokemonStats('charizard', 'charizard')">
```

## Related Functions

- **`fetchPokemon(nameToTry)`** (line 930): Makes the actual API call to PokeAPI
- **`closePokemonStats()`** (line 1038): Closes the modal dialog

## API Call Details

The PokeAPI call happens in the `fetchPokemon` function:
- **URL**: `https://pokeapi.co/api/v2/pokemon/{name}`
- **Method**: GET
- **Response**: JSON with Pokemon data including:
  - `stats[]`: Array of stat objects with `base_stat` and `stat.name`
  - `sprites.other['official-artwork'].front_default`: Official artwork URL
  - `species.name`: Pokemon species name

## Current Issue

If clicking sprites does nothing, it means:
1. The embedded script might not be executing (Gradio may sanitize it)
2. The function might not be assigned to `window` properly
3. The onclick handler might not be firing

**Check the browser console for:**
- `[Pokemon Stats] Functions embedded and ready`
- `[Click] Sprite clicked:` (when you click a sprite)
- `[showPokemonStats] Function called with:` (when the function executes)

