import gradio as gr
from typing import List
import requests
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from config import SPRITE_BASE_URL

# Import shared utilities
from shared import (
    logger, SmartMemoryManager, select_prompt, create_agent_executor,
    format_agent_response, format_strategy_markdown, get_pokemon_sprite_urls,
    fix_markdown_headers_spacing
)

# Import Pokemon API utilities
from pokeapi_utils import normalize_pokemon_name_for_api

# Import tools and models
from tools import ddgo_tool, save_tool, clean_smogon_tool, team_search_tool, ALL_SPECIES, extract_species_tier_gen
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon 
from utils import general_prompt, strat_prompt_single, strat_prompt_team, strat_prompt_multi, format_strategy_team_output, format_multiple_teams_output, ALL_FILENAMES

load_dotenv()

tools = [ddgo_tool, save_tool, clean_smogon_tool, team_search_tool]

# Initialize memory manager and LLM
memory_manager = SmartMemoryManager()

try:
    from langchain_openai import ChatOpenAI
    from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE
    llm = ChatOpenAI(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
    logger.info(f"Initialized LLM with model: {DEFAULT_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    raise

def chat_with_agent(query: str, chat_history: List) -> tuple:
    """Handle chat interaction with improved error handling and memory management."""
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
            return "❌ An error occurred while processing your query. Please try again or rephrase your question.", chat_history, False, None

        # Format response using shared function
        output, is_team_output, raw_response = format_agent_response(
            response, 
            fix_markdown_headers_spacing, 
            format_multiple_teams_output
        )

        return output, chat_history, is_team_output, raw_response

    except Exception as e:
        logger.error(f"Unexpected error in chat_with_agent: {e}", exc_info=True)
        return "❌ An unexpected error occurred. Please try again later.", chat_history, False, None


# 🎨 Modern Pokémon-Themed UI (Based on Reference Design)
try:
    # Pokéball SVG for decorations
    pokeball_svg = """
    <svg width="60" height="60" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M50 5C26.25 5 7 24.25 7 48H40C40 42.48 44.48 38 50 38C55.52 38 60 42.48 60 48H93C93 24.25 73.75 5 50 5Z" fill="#FF0000"/>
      <path d="M50 95C73.75 95 93 75.75 93 52H60C60 57.52 55.52 62 50 62C44.48 62 40 57.52 40 52H7C7 75.75 26.25 95 50 95Z" fill="#FFFFFF"/>
      <rect x="7" y="48" width="86" height="4" fill="#3D3D3D" opacity="0.2"/>
      <circle cx="50" cy="50" r="15" fill="#3D3D3D" opacity="0.2"/>
      <circle cx="50" cy="50" r="10" fill="#FFFFFF"/>
      <circle cx="50" cy="50" r="5" fill="#3D3D3D" opacity="0.1"/>
      <circle cx="50" cy="50" r="45" stroke="#3D3D3D" stroke-width="3" opacity="0.2" fill="none"/>
    </svg>
    """
    
    # Modern CSS based on reference design
    custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Color Variables */
    :root {
        --pokemon-red: #FF0000;
        --pokemon-red-dark: #CC0000;
        --pokemon-yellow: #FFD700;
        --pokemon-blue: #3B4CCA;
        --background: #FAFAFA;
        --foreground: #1A1A1A;
        --muted: #F5F5F5;
        --muted-foreground: #666666;
        --border: #E5E5E5;
        --card: #FFFFFF;
        --primary: #FF0000;
        --primary-foreground: #FFFFFF;
        --secondary: #F5F5F5;
    }
    
    /* Main Container - Desktop Optimized */
    .gradio-container {
        max-width: 1400px !important;
        margin: 0 auto !important;
        font-family: 'Outfit', 'Segoe UI', sans-serif !important;
        background: var(--background) !important;
        padding: 2rem 2rem !important;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Floating Pokéballs Background */
    .pokeball-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    
    .pokeball-float {
        position: absolute;
        opacity: 0.1;
    }
    
    .pokeball-float-1 {
        top: 10%;
        left: 5%;
        animation: float1 8s ease-in-out infinite;
    }
    
    .pokeball-float-2 {
        top: 30%;
        right: 8%;
        animation: float2 10s ease-in-out infinite;
    }
    
    .pokeball-float-3 {
        bottom: 20%;
        left: 10%;
        animation: float3 12s ease-in-out infinite;
    }
    
    .pokeball-float-4 {
        top: 60%;
        right: 5%;
        animation: float4 9s ease-in-out infinite;
    }
    
    @keyframes float1 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(10px, -15px) rotate(10deg); }
        50% { transform: translate(-5px, -25px) rotate(-5deg); }
        75% { transform: translate(-15px, -10px) rotate(-10deg); }
    }
    
    @keyframes float2 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-20px, 15px) rotate(-15deg); }
        66% { transform: translate(15px, 10px) rotate(10deg); }
    }
    
    @keyframes float3 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        20% { transform: translate(15px, 20px) rotate(8deg); }
        40% { transform: translate(25px, -10px) rotate(-5deg); }
        60% { transform: translate(-10px, -20px) rotate(-12deg); }
        80% { transform: translate(-20px, 10px) rotate(5deg); }
    }
    
    @keyframes float4 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(-15px, -20px) rotate(-10deg); }
    }
    
    /* Header */
    .header-modern {
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--foreground);
        margin: 0.5rem 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: var(--muted-foreground);
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Quick Action Buttons */
    .quick-actions-modern {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.5rem;
        margin: 1.5rem 0;
        position: relative;
        z-index: 1;
    }
    
    .quick-btn-modern {
        background: transparent !important;
        border: none !important;
        color: var(--muted-foreground) !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }
    
    .quick-btn-modern:hover {
        background: var(--muted) !important;
        color: var(--foreground) !important;
        border: none !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Quick Team Container */
    .quick-team-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 0.125rem !important;
    }
    
    /* Team Count Dropdown – matches React component */
    .team-count-dropdown {
        position: relative !important;
        z-index: 100 !important;
    }
    
    .team-count-dropdown label {
        display: none !important;
    }
    
    /* Outer wrappers - white background, no border, just positioning - even on hover */
    .team-count-dropdown .wrap,
    .team-count-dropdown .wrap:hover,
    .team-count-dropdown .wrap:not(:hover),
    .team-count-dropdown .wrap > div,
    .team-count-dropdown .wrap > div:hover,
    .team-count-dropdown .wrap > div:not(:hover) {
        position: relative !important;
        background: var(--card) !important;
        border: none !important;
        border-width: 0 !important;
        outline: none !important;
        outline-width: 0 !important;
        box-shadow: none !important;
    }
    
    /* Secondary wrap - also white, even on hover, no borders ever */
    .team-count-dropdown .secondary-wrap,
    .team-count-dropdown .secondary-wrap:hover,
    .team-count-dropdown .secondary-wrap:not(:hover) {
        position: relative !important;
        background: var(--card) !important;
        border: none !important;
        border-width: 0 !important;
        outline: none !important;
        outline-width: 0 !important;
        box-shadow: none !important;
    }
    
    /* Ensure ALL child elements are white too */
    .team-count-dropdown .wrap > *,
    .team-count-dropdown .wrap > *:hover,
    .team-count-dropdown .wrap > div > *,
    .team-count-dropdown .wrap > div > *:hover {
        background: var(--card) !important;
    }
    
    /* Main container - Apply hover styles as default (always looks like hover state) */
    .team-count-dropdown .wrap-inner,
    .team-count-dropdown .wrap-inner:hover,
    .team-count-dropdown .wrap-inner:not(:hover),
    .team-count-dropdown .wrap-inner:focus-within,
    .team-count-dropdown .wrap-inner:not(:focus-within) {
        background: var(--card) !important;
        border: none !important;
        border-width: 0 !important;
        border-style: none !important;
        border-color: transparent !important;
        border-radius: 999px !important;
        box-shadow: none !important;
        outline: none !important;
        outline-width: 0 !important;
        outline-style: none !important;
        outline-color: transparent !important;
        padding: 0.25rem 0.5rem !important;
    }
    
    /* Input element styling - dark text, white background, smaller size, NO BORDERS */
    .team-count-dropdown select,
    .team-count-dropdown button,
    .team-count-dropdown input {
        background: var(--card) !important;
        border: none !important;
        outline: none !important;
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: var(--foreground) !important;
        min-width: 60px !important;
        width: auto !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    
    /* Hover and focus states - same as default (already applied above) */
    .team-count-dropdown .wrap-inner:hover {
        background: var(--card) !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .team-count-dropdown .wrap-inner:focus-within {
        border: none !important;
        box-shadow: none !important;
        background: var(--card) !important;
    }
    
    /* Force all states to look the same (like hover) */
    .team-count-dropdown .wrap-inner:active,
    .team-count-dropdown .wrap-inner:visited,
    .team-count-dropdown .wrap-inner:link {
        background: var(--card) !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    .team-count-dropdown select:hover,
    .team-count-dropdown button:hover,
    .team-count-dropdown input:hover {
        background: var(--card) !important;
        color: var(--foreground) !important;
    }
    
    .team-count-dropdown select:focus,
    .team-count-dropdown button:focus,
    .team-count-dropdown input:focus {
        outline: none !important;
        background: var(--card) !important;
        color: var(--foreground) !important;
    }
    
    /* Remove any default browser styles, borders, and shadows from ALL elements */
    .team-count-dropdown *:not(.wrap-inner) {
        box-shadow: none !important;
        border: none !important;
        outline: none !important;
    }
    
    .team-count-dropdown *:not(.wrap-inner):hover {
        background: var(--card) !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .team-count-dropdown *:focus {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Force white background and NO borders on all elements except wrap-inner */
    .team-count-dropdown .wrap *:not(.wrap-inner),
    .team-count-dropdown .wrap *:not(.wrap-inner):hover {
        background: var(--card) !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove ALL borders, outlines, and shadows from everything */
    .team-count-dropdown * {
        border: none !important;
        border-width: 0 !important;
        outline: none !important;
        outline-width: 0 !important;
        box-shadow: none !important;
    }
    
    /* Specifically target wrap-inner to ensure no border in any state */
    .team-count-dropdown .wrap-inner,
    .team-count-dropdown .wrap-inner:not(:hover),
    .team-count-dropdown .wrap-inner:not(:focus),
    .team-count-dropdown .wrap-inner:not(:focus-within) {
        border: none !important;
        border-width: 0 !important;
        box-shadow: none !important;
        outline: none !important;
        outline-width: 0 !important;
    }
    
    /* Remove any potential inset shadows or borders from secondary-wrap */
    .team-count-dropdown .secondary-wrap {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Dropdown arrow/icon - dark to match text */
    .team-count-dropdown .icon-wrap,
    .team-count-dropdown .icon-wrap svg,
    .team-count-dropdown .icon-wrap path {
        color: var(--foreground) !important;
        fill: var(--foreground) !important;
        stroke: var(--foreground) !important;
    }
    
    /* Remove any border artifacts and set white backgrounds on ALL pseudo-elements */
    .team-count-dropdown .wrap::before,
    .team-count-dropdown .wrap::after,
    .team-count-dropdown .wrap > div::before,
    .team-count-dropdown .wrap > div::after,
    .team-count-dropdown .wrap-inner::before,
    .team-count-dropdown .wrap-inner::after,
    .team-count-dropdown .secondary-wrap::before,
    .team-count-dropdown .secondary-wrap::after,
    .team-count-dropdown *::before,
    .team-count-dropdown *::after {
        display: none !important;
        border: none !important;
        outline: none !important;
        background: var(--card) !important;
        box-shadow: none !important;
    }
    
    /* Ensure no border on input/select elements inside, but keep wrap-inner border */
    .team-count-dropdown .wrap-inner select,
    .team-count-dropdown .wrap-inner button,
    .team-count-dropdown .wrap-inner input,
    .team-count-dropdown .secondary-wrap select,
    .team-count-dropdown .secondary-wrap button,
    .team-count-dropdown .secondary-wrap input {
        border: none !important;
        outline: none !important;
    }
    
    /* Dropdown menu - matches React: rounded-xl, border-2, shadow-lg */
    .team-count-dropdown .wrap .options,
    .team-count-dropdown ul {
        background: var(--card) !important;
        border: 2px solid var(--border) !important;
        border-radius: 0.75rem !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
        z-index: 1000 !important;
        padding: 0.375rem !important;
        margin-top: 0.5rem !important;
        overflow: hidden !important;
    }
    
    /* Dropdown items - matches React: rounded-lg, px-3, py-2 */
    .team-count-dropdown .wrap .options li,
    .team-count-dropdown ul li {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 0.5rem !important;
        text-align: left !important;
        transition: all 0.15s ease !important;
        list-style: none !important;
        color: var(--foreground) !important;
    }
    
    /* Hover state - matches React: bg-secondary */
    .team-count-dropdown .wrap .options li:hover,
    .team-count-dropdown ul li:hover {
        background: var(--secondary) !important;
        color: var(--foreground) !important;
    }
    
    /* Selected state - matches React: bg-primary, text-primary-foreground */
    .team-count-dropdown .wrap .options li[aria-selected="true"],
    .team-count-dropdown .wrap .options li.selected {
        background: var(--primary) !important;
        color: var(--primary-foreground) !important;
    }
    
        /* Desktop Layout - Two Column */
        .main-layout {
            display: grid;
            grid-template-columns: minmax(250px, 300px) 1fr;
            gap: 1.5rem;
            align-items: start;
            width: 100%;
            max-width: 100%;
            overflow-x: hidden;
            box-sizing: border-box;
        }
        
        /* Sidebar for Pokémon Sprites */
        .pokemon-sidebar {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.25rem;
            position: relative;
            top: auto;
            max-height: none;
            overflow: visible;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            box-sizing: border-box;
        }
        
        /* Ensure all child elements in sidebar are visible */
        .pokemon-sidebar * {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Fix for Gradio container overflow issues */
        .main-layout,
        .main-layout > div,
        .main-layout > .gr-column,
        .gradio-container > div,
        .gradio-container .contain {
            overflow: visible !important;
        }
        
        /* Force no horizontal scroll in sprite container - but allow images to be visible */
        .pokemon-sidebar > * {
            max-width: 100% !important;
            box-sizing: border-box;
        }
        
        .pokemon-sprites-container {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box;
        }
        
        .pokemon-sprites-modern * {
            box-sizing: border-box !important;
            overflow: visible !important;
        }
        
        /* Ensure images are always visible at all screen sizes */
        .pokemon-sidebar img {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        .pokemon-sprites-empty {
            display: flex !important;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
            text-align: center;
            min-height: 200px;
        }
        
        .pokeball-empty {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }
        
        .pokemon-empty-text {
            font-size: 0.9rem;
            color: var(--muted-foreground);
            margin: 0.5rem 0;
            font-weight: 500;
        }
        
        .pokemon-empty-hint {
            font-size: 0.75rem;
            color: var(--muted-foreground);
            opacity: 0.7;
            margin: 0;
        }
        
        .pokemon-detected-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--muted-foreground);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        .pokemon-sprites-modern {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.75rem;
            width: 100% !important;
            max-width: 100% !important;
            overflow: visible !important;
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        .pokemon-sprite-modern {
            background: var(--muted);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 0.5rem;
            text-align: center;
            transition: all 0.2s ease;
            cursor: pointer;
            min-width: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
            box-sizing: border-box;
            overflow: visible !important;
            word-wrap: break-word;
            overflow-wrap: break-word;
            display: flex !important;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .pokemon-sprite-modern:hover {
            transform: translateY(-4px);
            border-color: var(--pokemon-red);
            box-shadow: 0 4px 12px rgba(255, 0, 0, 0.15);
            background: white;
        }
        
        .pokemon-sprite-modern img {
            height: 70px !important;
            width: auto !important;
            max-width: 100% !important;
            min-width: 0 !important;
            display: block !important;
            margin: 0 auto !important;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
            object-fit: contain !important;
            image-rendering: crisp-edges;
            box-sizing: border-box !important;
            flex-shrink: 0 !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: relative !important;
            z-index: 1;
        }
        
        .pokemon-sprite-name {
            font-size: 0.7rem;
            font-weight: 600;
            color: var(--foreground);
            margin-top: 0.5rem;
            text-transform: capitalize;
            word-break: break-word;
            overflow-wrap: break-word;
            word-wrap: break-word;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Empty State for Pokemon Sprites */
        .pokemon-sprites-empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
            text-align: center;
            color: var(--muted-foreground);
        }
        
        .pokeball-empty {
            font-size: 3rem;
            margin-bottom: 0.75rem;
            opacity: 0.2;
        }
        
        .pokemon-empty-text {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--muted-foreground);
            margin: 0;
        }
        
        .pokemon-empty-hint {
            font-size: 0.75rem;
            color: var(--muted-foreground);
            margin-top: 0.25rem;
            opacity: 0.7;
        }
        
        /* Stats Modal */
        .pokemon-stats-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            animation: fadeIn 0.2s ease;
        }
        
        .pokemon-stats-content {
            background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%);
            margin: 2% auto;
            padding: 0;
            border-radius: 20px;
            width: 90%;
            max-width: 520px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            animation: slideDown 0.3s ease;
            border: 4px solid var(--pokemon-red);
            border-top: 8px solid var(--pokemon-red);
            position: relative;
            overflow: visible;
        }
        
        .pokemon-card-top {
            background: linear-gradient(135deg, var(--pokemon-red) 0%, var(--pokemon-red-dark) 100%);
            padding: 1.5rem 2rem 1rem 2rem;
            text-align: center;
            position: relative;
        }
        
        .pokeball-icon {
            width: 50px;
            height: 50px;
            margin: 0 auto 0.5rem auto;
            position: relative;
            display: inline-block;
        }
        
        .pokeball-icon::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(to bottom, #ffffff 0%, #ffffff 45%, #000000 45%, #000000 55%, #ffffff 55%, #ffffff 100%);
            border: 3px solid #000000;
            box-shadow: 0 0 0 2px #ffffff;
        }
        
        .pokeball-icon::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #ffffff;
            border: 3px solid #000000;
            box-shadow: 0 0 0 2px #ffffff, inset 0 0 0 2px #000000;
        }
        
        .pokemon-card-body {
            padding: 1.5rem 2rem 2rem 2rem;
        }
        
        .pokemon-stats-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .pokemon-stats-title {
            font-size: 1.75rem;
            font-weight: 800;
            color: white;
            text-transform: capitalize;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin: 0;
        }
        
        .pokemon-stats-close {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            cursor: pointer;
            border: none;
            background: rgba(255,255,255,0.2);
            padding: 0;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s ease;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .pokemon-stats-close:hover {
            background: rgba(255,255,255,0.3);
            color: white;
            transform: scale(1.1);
        }
        
        .pokemon-stats-art {
            text-align: center;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%);
            border-radius: 12px;
            padding: 1rem;
            border: 2px solid var(--border);
            position: relative;
            overflow: visible;
        }
        
        .pokemon-stats-art img {
            width: 220px;
            height: 220px;
            image-rendering: auto;
            image-rendering: -webkit-optimize-contrast;
            image-rendering: crisp-edges;
            object-fit: contain;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
        }
        
        .pokemon-type-icon {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            opacity: 0.08;
        }
        
        .pokemon-type-icon svg {
            width: 140px;
            height: 140px;
        }
        
        .pokemon-physical-stats {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding: 1.25rem;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            border: 2px solid var(--border);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        
        .physical-stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.25rem;
        }
        
        .physical-stat-types {
            align-items: center;
            gap: 0.5rem;
        }
        
        .pokemon-types-inline {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
        }
        
        .physical-stat-egggroups {
            align-items: center;
            gap: 0.5rem;
        }
        
        .egg-groups-inline {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
        }
        
        .egg-group-badge {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            background: var(--pokemon-blue);
            color: white;
            text-transform: capitalize;
        }
        
        .physical-stat-label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--muted-foreground);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .physical-stat-value {
            font-size: 1rem;
            font-weight: 700;
            color: var(--foreground);
        }
        
        .physical-stat-value.total-stats {
            color: var(--pokemon-red);
            font-size: 1.1rem;
        }
        
        .physical-stat-divider {
            width: 1px;
            height: 30px;
            background: var(--border);
        }
        
        .mega-symbol {
            position: absolute;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #FF6B6B 0%, #FF0000 100%);
            color: white;
            font-weight: 800;
            font-size: 0.7rem;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(255, 0, 0, 0.4);
            border: 2px solid white;
            z-index: 10;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 2px 8px rgba(255, 0, 0, 0.4);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(255, 0, 0, 0.6);
            }
        }
        
        .pokemon-abilities-section {
            margin-bottom: 1.25rem;
            margin-top: 1.5rem;
            padding: 1rem;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            border: 2px solid var(--border);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .pokemon-abilities-label {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--muted-foreground);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
            flex-shrink: 0;
        }
        
        .pokemon-abilities {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: center;
        }
        
        .pokemon-ability-badge {
            display: inline-block;
            padding: 0.4rem 0.9rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            background: var(--muted);
            color: var(--foreground);
            border: 2px solid var(--border);
            position: relative;
            cursor: help;
            transition: all 0.2s ease;
        }
        
        .pokemon-ability-badge:hover {
            background: var(--card);
            border-color: var(--pokemon-red);
            box-shadow: 0 2px 8px rgba(255, 0, 0, 0.15);
        }
        
        .pokemon-ability-tooltip {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%) translateY(-5px);
            margin-bottom: 0.75rem;
            padding: 1rem;
            background: var(--foreground);
            color: white;
            border-radius: 8px;
            font-size: 0.85rem;
            line-height: 1.5;
            width: 320px;
            max-width: calc(100vw - 4rem);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1001;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease, transform 0.2s ease;
            word-wrap: break-word;
            white-space: normal;
            box-sizing: border-box;
        }
        
        .pokemon-ability-badge:hover .pokemon-ability-tooltip,
        .pokemon-ability-badge:focus .pokemon-ability-tooltip {
            opacity: 1;
            pointer-events: auto;
            transform: translateX(-50%) translateY(0);
        }
        
        .pokemon-ability-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: var(--foreground);
        }
        
        .pokemon-type-badge {
            display: inline-block;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: capitalize;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Type colors */
        .pokemon-type-normal { background: #A8A878; }
        .pokemon-type-fire { background: #F08030; }
        .pokemon-type-water { background: #6890F0; }
        .pokemon-type-electric { background: #F8D030; color: #333; }
        .pokemon-type-grass { background: #78C850; }
        .pokemon-type-ice { background: #98D8D8; color: #333; }
        .pokemon-type-fighting { background: #C03028; }
        .pokemon-type-poison { background: #A040A0; }
        .pokemon-type-ground { background: #E0C068; color: #333; }
        .pokemon-type-flying { background: #A890F0; }
        .pokemon-type-psychic { background: #F85888; }
        .pokemon-type-bug { background: #A8B820; }
        .pokemon-type-rock { background: #B8A038; }
        .pokemon-type-ghost { background: #705898; }
        .pokemon-type-dragon { background: #7038F8; }
        .pokemon-type-dark { background: #705848; }
        .pokemon-type-steel { background: #B8B8D0; color: #333; }
        .pokemon-type-fairy { background: #EE99AC; }
        
        .pokemon-ability-hidden {
            background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
            border-color: var(--pokemon-red);
        }
        
        .hidden-label {
            font-size: 0.75rem;
            color: var(--pokemon-red);
            font-weight: 700;
        }
        
        .pokemon-stats-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .pokemon-stat-item {
            margin-bottom: 0.75rem;
            opacity: 0;
            animation: fadeInUp 0.4s ease forwards;
        }
        
        .stat-row-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .pokemon-stat-name {
            font-weight: 600;
            color: var(--foreground);
            text-transform: capitalize;
            font-size: 0.9rem;
            min-width: 70px;
        }
        
        .stat-bar-container {
            flex: 1;
            height: 10px;
            background: var(--muted);
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }
        
        .stat-bar {
            height: 100%;
            border-radius: 10px;
            transition: width 0.6s ease, background-color 0.3s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        
        .pokemon-stat-value {
            font-weight: 700;
            font-size: 1rem;
            min-width: 35px;
            text-align: right;
            text-shadow: 0 0 3px rgba(255, 255, 255, 1), 0 0 6px rgba(255, 255, 255, 0.9), 0 0 8px rgba(255, 255, 255, 0.7), 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .pokemon-stats-loading {
            text-align: center;
            padding: 2rem;
            color: var(--muted-foreground);
        }
        
        .pokemon-stats-error {
            text-align: center;
            padding: 2rem;
            color: var(--pokemon-red);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Chat Container - Wider for Desktop */
        .chat-container-modern {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            position: relative;
            z-index: 1;
            overflow: hidden;
            min-height: 600px;
        }
        
        .chatbot-modern {
            border: none !important;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
            padding: 2rem !important;
            height: 550px !important;
            border-radius: 32px !important;
        }
    
    /* Message Bubbles */
    .user-message-modern {
        background: var(--pokemon-red) !important;
        color: white !important;
        border-radius: 24px 24px 8px 24px !important;
        padding: 0.875rem 1.125rem !important;
        margin: 0.5rem 0 !important;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 2px 8px rgba(255, 0, 0, 0.15) !important;
    }
    
    .assistant-message-modern {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        color: var(--foreground) !important;
        border-radius: 24px 24px 24px 8px !important;
        padding: 0.875rem 1.125rem !important;
        margin: 0.5rem 0 !important;
        max-width: 85%;
        border: 1px solid var(--border);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Input Area */
    .input-area-modern {
        border-top: 1px solid var(--border);
        padding: 1.25rem;
        background: var(--card);
    }
    
    .input-textbox-modern {
        border: 2px solid var(--border) !important;
        border-radius: 28px !important;
        padding: 0.875rem 1.125rem !important;
        font-size: 1rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        transition: all 0.2s ease !important;
    }
    
    .input-textbox-modern:focus {
        border-color: var(--pokemon-red) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1) !important;
    }
    
    /* Gradio Chatbot and Input Styling */
    .gradio-chatbot,
    .gradio-chatbot > div {
        border-radius: 32px !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
    }
    
    /* Chatbot container background */
    .bubble-wrap,
    .panel-wrap {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border-radius: 32px !important;
    }
    
    
    /* Gradio Textbox/Input Styling */
    textarea,
    input[type="text"] {
        border-radius: 28px !important;
        border: 2px solid var(--border) !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        padding: 0.875rem 1.125rem !important;
        transition: all 0.2s ease !important;
        color: var(--foreground) !important;
    }
    
    textarea:focus,
    input[type="text"]:focus {
        border-color: var(--pokemon-red) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1) !important;
        color: var(--foreground) !important;
    }
    
    textarea::placeholder,
    input[type="text"]::placeholder {
        color: var(--muted-foreground) !important;
    }
    
    /* Multimodal Textbox Container */
    .multimodal-textbox-container,
    .multimodal-textbox-container textarea {
        border-radius: 28px !important;
        color: var(--foreground) !important;
    }
    
    /* Ensure text color in input is visible */
    .input-container textarea,
    .input-container input,
    .multimodal-textbox-container textarea {
        color: var(--foreground) !important;
    }
    
    .input-container textarea::placeholder,
    .input-container input::placeholder {
        color: var(--muted-foreground) !important;
        opacity: 0.7 !important;
    }
    
    /* Buttons */
    button.primary {
        background: var(--pokemon-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    button.primary:hover {
        background: var(--pokemon-red-dark) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3) !important;
    }
    
    button.secondary {
        background: var(--card) !important;
        color: var(--foreground) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    button.secondary:hover {
        background: var(--muted) !important;
        border-color: var(--pokemon-red) !important;
    }
    
    /* Empty State */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        color: var(--muted-foreground);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.4s ease-out forwards;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--muted);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--muted-foreground);
    }
    
    /* Responsive - Large screens (full screen) */
    @media (min-width: 1025px) {
        .pokemon-sidebar {
            min-width: 250px;
            max-width: 300px;
            position: relative !important;
            top: auto !important;
            max-height: none !important;
            overflow: visible !important;
        }
        
        .pokemon-sprites-modern {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        }
        
        .pokemon-sprite-modern img {
            height: 70px !important;
            max-width: 100% !important;
            display: block !important;
            visibility: visible !important;
        }
    }
    
    /* Responsive - Tablet and Mobile */
    @media (max-width: 1024px) {
        .main-layout {
            grid-template-columns: 1fr !important;
        }
        
        .pokemon-sidebar {
            position: relative !important;
            top: 0 !important;
            max-height: none !important;
            margin-bottom: 1rem;
        }
        
        .pokemon-sprites-modern {
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)) !important;
        }
    }
    
    @media (max-width: 768px) {
        .gradio-container {
            padding: 1rem !important;
        }
        
        .pokemon-sprite-modern img {
            height: 56px !important;
        }
        
        .header-title {
            font-size: 2rem !important;
        }
    }
    """
    
    # Load JavaScript for Pokemon stats from external file BEFORE creating Blocks
    js_file_path = Path(__file__).parent / "static" / "pokemon_stats.js"
    pokemon_stats_js = ""
    try:
        if js_file_path.exists():
            with open(js_file_path, 'r', encoding='utf-8') as f:
                pokemon_stats_js = f.read()
            logger.info(f"Loaded Pokemon stats JavaScript from {js_file_path}")
        else:
            logger.warning(f"JavaScript file not found at {js_file_path}, using empty script")
            pokemon_stats_js = "console.warn('Pokemon stats JavaScript file not found');"
    except Exception as e:
        logger.error(f"Error loading Pokemon stats JavaScript: {e}")
        pokemon_stats_js = "console.error('Error loading Pokemon stats JavaScript');"
    
    # JavaScript to format dropdown text with triangle
    dropdown_js = """
    <script>
    (function() {
        function formatDropdown() {
            document.querySelectorAll('.team-count-dropdown').forEach(dropdown => {
                const button = dropdown.querySelector('button');
                const select = dropdown.querySelector('select');
                if (button && select && !button.textContent.includes('▾')) {
                    button.textContent = select.value + ' Pokémon ▾';
                    if (!select.hasAttribute('data-listener-added')) {
                        select.setAttribute('data-listener-added', 'true');
                        select.addEventListener('change', function() {
                            button.textContent = this.value + ' Pokémon ▾';
                        });
                    }
                }
            });
        }
        setTimeout(formatDropdown, 500);
        setInterval(formatDropdown, 1000);
    })();
    </script>
    """
    
    # Inject external JavaScript file into page head
    head_content = f"""
    <script>
    {pokemon_stats_js}
    </script>
    {dropdown_js}
    """
    
    with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="Pokémon Strategy Assistant", head=head_content) as demo:
        
        # Floating Pokéballs Background
        gr.HTML(f"""
        <div class="pokeball-bg">
            <div class="pokeball-float pokeball-float-1">{pokeball_svg}</div>
            <div class="pokeball-float pokeball-float-2">{pokeball_svg.replace('60', '40')}</div>
            <div class="pokeball-float pokeball-float-3">{pokeball_svg.replace('60', '80')}</div>
            <div class="pokeball-float pokeball-float-4">{pokeball_svg.replace('60', '50')}</div>
        </div>
        """)
        
        # Header
        with gr.Column(elem_classes=["header-modern"]):
            gr.Markdown("""
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 2rem;">⚡</span>
                <h1 class="header-title">Pokémon Strategy Assistant</h1>
            </div>
            <p class="header-subtitle">Your AI-powered competitive Pokémon guide</p>
            """)
            
            # Quick Action Buttons
            with gr.Row(elem_classes=["quick-actions-modern"]):
                with gr.Column(scale=0, min_width=140, elem_classes=["quick-team-container"]):
                    quick_team = gr.Button("🔍 Find Teams", elem_classes=["quick-btn-modern"], size="sm")
                    team_pokemon_count = gr.Dropdown(
                        choices=[2, 3, 4, 5, 6],
                        value=2,
                        label="",
                        scale=0,
                        container=False,
                        show_label=False,
                        elem_classes=["team-count-dropdown"]
                    )
                quick_strategy = gr.Button("⚔️ Strategy", elem_classes=["quick-btn-modern"], size="sm")
                quick_compare = gr.Button("🔄 Compare", elem_classes=["quick-btn-modern"], size="sm")
        
        # Desktop Layout - Two Column (Sidebar + Chat)
        with gr.Row(elem_classes=["main-layout"]):
            # Left Sidebar - Pokémon Sprites
            with gr.Column(scale=1, elem_classes=["pokemon-sidebar"]):
                gr.Markdown("**Detected Pokémon**", elem_classes=["pokemon-detected-title"])
                pokemon_html = gr.HTML('''
                <div class="pokemon-sprites-empty">
                    <div class="pokeball-empty">⚪</div>
                    <p class="pokemon-empty-text">No Pokémon detected yet</p>
                    <p class="pokemon-empty-hint">Mention names in chat</p>
                </div>
                ''', elem_classes=["pokemon-sprites-container"])
            
            # Right Column - Chat Interface
            with gr.Column(scale=3, elem_classes=["chat-container-modern"]):
                chatbot = gr.Chatbot(
                    label="",
                    type="messages",
                    render_markdown=True,
                    height=550,
                    show_label=False,
                    container=True,
                    elem_classes=["chatbot-modern"]
                )
                
                # Input Area
                with gr.Row(elem_classes=["input-area-modern"]):
                    query = gr.Textbox(
                        placeholder="Ask about teams, builds, or strategies...",
                        show_label=False,
                        scale=9,
                        container=False,
                        elem_classes=["input-textbox-modern"]
                    )
                    submit_btn = gr.Button("Send", scale=1, variant="primary", size="lg")
                    clear_btn = gr.Button("Clear", scale=1, variant="secondary", size="lg")
        
        # Quick action handlers
        def quick_team_click(num_pokemon):
            """Generate team search template based on number of Pokemon selected."""
            if num_pokemon == 2:
                return "Find teams with <pokemon 1> and <pokemon 2> in <generation> <format>"
            elif num_pokemon == 3:
                return "Find teams with <pokemon 1>, <pokemon 2>, and <pokemon 3> in <generation> <format>"
            elif num_pokemon == 4:
                return "Find teams with <pokemon 1>, <pokemon 2>, <pokemon 3>, and <pokemon 4> in <generation> <format>"
            elif num_pokemon == 5:
                return "Find teams with <pokemon 1>, <pokemon 2>, <pokemon 3>, <pokemon 4>, and <pokemon 5> in <generation> <format>"
            else:  # 6
                return "Find teams with <pokemon 1>, <pokemon 2>, <pokemon 3>, <pokemon 4>, <pokemon 5>, and <pokemon 6> in <generation> <format>"
        
        # Update dropdown display text to show "{value} Pokémon"
        def update_dropdown_display():
            """JavaScript to update dropdown button text to show '{value} Pokémon' format."""
            return """
            <script>
            (function() {
                function updateTeamDropdown() {
                    const dropdowns = document.querySelectorAll('.team-count-dropdown');
                    dropdowns.forEach(dropdown => {
                        const select = dropdown.querySelector('select');
                        const wrap = dropdown.querySelector('.wrap');
                        if (select && wrap) {
                            const value = select.value;
                            const button = wrap.querySelector('button');
                            if (button) {
                                button.textContent = value + ' Pokémon';
                            }
                            // Also update on change
                            select.addEventListener('change', function() {
                                const button = wrap.querySelector('button');
                                if (button) {
                                    button.textContent = this.value + ' Pokémon';
                                }
                            });
                        }
                    });
                }
                // Run on load
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', updateTeamDropdown);
                } else {
                    updateTeamDropdown();
                }
                // Also run after Gradio updates
                setTimeout(updateTeamDropdown, 1000);
            })();
            </script>
            """
        
        def quick_strategy_click():
            return "Strategy for <pokemon name> in <generation> <format>"
        
        def quick_compare_click():
            return "Compare <pokemon name 1> and <pokemon name 2> in <generation> <format>"
        
        quick_team.click(quick_team_click, inputs=[team_pokemon_count], outputs=query)
        quick_strategy.click(quick_strategy_click, outputs=query)
        quick_compare.click(quick_compare_click, outputs=query)
        
        # Helper function to create modern sprite HTML - Show ALL sprites
        def create_modern_sprites_html(sprite_urls_lists):
            """Create modern HTML for Pokémon sprites - shows ALL forms/variants."""
            # Check if we have any sprites at all
            has_sprites = False
            if sprite_urls_lists:
                for sprite_list in sprite_urls_lists:
                    if sprite_list and len(sprite_list) > 0:
                        has_sprites = True
                        break
            
            if not has_sprites:
                # Empty state - similar to React reference
                return '''
                <div class="pokemon-sprites-empty">
                    <div class="pokeball-empty">⚪</div>
                    <p class="pokemon-empty-text">No Pokémon detected yet</p>
                    <p class="pokemon-empty-hint">Mention names in chat</p>
                </div>
                '''
            
            # Functions are already loaded in page head, so we just need sprite HTML
            html = '<div class="pokemon-sprites-modern">'
            
            for sprite_list in sprite_urls_lists:
                if sprite_list and len(sprite_list) > 0:
                    # Show ALL sprites in the list (all forms, variants, etc.)
                    for sprite_url in sprite_list:
                        sprite_filename = sprite_url.split('/')[-1]
                        pokemon_name = sprite_filename.replace('.png', '').replace('-', ' ').title()
                        api_name, base_name = normalize_pokemon_name_for_api(sprite_filename)
                        
                        # Escape quotes for HTML attributes
                        api_name_escaped = api_name.replace("'", "&#39;")
                        base_name_escaped = base_name.replace("'", "&#39;")
                        
                        # Escape single quotes for JavaScript in onclick
                        api_name_js = api_name_escaped.replace("'", "\\'")
                        base_name_js = base_name_escaped.replace("'", "\\'")
                        
                        html += f'''
                        <div class="pokemon-sprite-modern fade-in" data-pokemon-name="{api_name_escaped}" data-base-name="{base_name_escaped}" style="cursor: pointer;">
                            <img src="{sprite_url}" alt="{pokemon_name}" loading="lazy" />
                            <div class="pokemon-sprite-name">{pokemon_name}</div>
                        </div>
                        '''
            html += '</div>'
            return html
        
        # Main response handler
        def respond(message: str, chat_history: List):
            """Handle user message and generate response."""
            try:
                if not message or not message.strip():
                    return chat_history, "", ""
                
                # Show loading
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": "🤔 Thinking..."})
                
                output, _, is_team_output, raw_response = chat_with_agent(message, chat_history[:-1])
                
                if not is_team_output:
                    output = format_strategy_markdown(output)
                
                chat_history[-1] = {"role": "assistant", "content": output}
                
                # Determine if this is a team query by checking both is_team_output and message content
                # This is needed because is_team_output only works if response is AllTeamSearchResult instance
                message_lower = message.lower()
                is_team_query = is_team_output or any(keyword in message_lower for keyword in [
                    'find teams', 'teams with', 'team with', 'search teams', 'show teams',
                    'get teams', 'list teams', 'teams featuring', 'teams containing'
                ])
                
                # Get Pokémon sprites - use Gen 5 Showdown sprites for strategy queries (not team strategy)
                sprite_urls_lists = []
                pokemon_list, _, _ = extract_species_tier_gen(message)
                
                if is_team_query:
                    # For team queries: 
                    # - 1 sprite for the searched Pokémon (e.g., Garchomp)
                    # - 1 sprite for each teammate (each teammate gets exactly 1 sprite)
                    
                    # Helper function to normalize species name to Showdown format
                    def normalize_species_name(name: str) -> str:
                        """
                        Normalize species name to Pokémon Showdown filename base.
                        - Multi-word names: "Great Tusk" → "greattusk" (remove spaces)
                        - Form names: "Landorus-Therian" → "landorus-therian" (keep hyphens)
                        """
                        return (
                            name.lower()
                            .replace(" ", "")        # Remove spaces (e.g., "Great Tusk" → "greattusk")
                            .replace("'", "")        # Remove apostrophes
                            # Keep hyphens for forms (e.g., "Landorus-Therian" stays as "landorus-therian")
                        )
                    
                    # Get ALL searched Pokémon from query (not just the first one)
                    searched_pokemon_set = set()
                    if pokemon_list:
                        for pokemon_name in pokemon_list:
                            searched_pokemon_set.add(normalize_species_name(pokemon_name))
                    
                    # Extract Pokémon names from the raw response object if available
                    pokemon_in_output = set()  # Use set to avoid duplicates
                    
                    if raw_response and isinstance(raw_response, AllTeamSearchResult):
                        # Extract directly from structured data - much more reliable
                        for team in raw_response.teams:
                            for pokemon in team.team:
                                if pokemon.species:
                                    # Extract actual species name (handle enum/model objects)
                                    if isinstance(pokemon.species, str):
                                        species_name = pokemon.species
                                    elif hasattr(pokemon.species, "value"):
                                        # Enum with .value attribute
                                        species_name = pokemon.species.value
                                    elif hasattr(pokemon.species, "name"):
                                        # Enum or model with .name attribute
                                        species_name = pokemon.species.name
                                    else:
                                        # LAST resort — extract last token after dot (e.g., "Species.GARCHOMP" -> "GARCHOMP")
                                        species_str = str(pokemon.species)
                                        # Handle cases like "Species.GARCHOMP" or "<Species.GARCHOMP: 'Garchomp'>"
                                        if '.' in species_str:
                                            species_name = species_str.split('.')[-1].split(':')[0].strip("<>'\"")
                                        else:
                                            species_name = species_str
                                    
                                    # Normalize to Showdown format and add to set
                                    pokemon_in_output.add(normalize_species_name(species_name))
                    else:
                        # Fallback: Extract from formatted output using regex
                        # Pattern to match **PokemonName** (but not **Item:**, **Ability:**, etc.)
                        # Look for patterns like "---\n**PokemonName**" or standalone "**PokemonName**"
                        pokemon_pattern = r'(?:^|\n)---\s*\n\*\*([A-Za-z0-9\-\s]+?)\*\*|(?:^|\n)\*\*([A-Za-z][A-Za-z0-9\-\s]*?)\*\*(?=\n|$)'
                        matches = re.findall(pokemon_pattern, output, re.MULTILINE)
                        
                        for match in matches:
                            # match is a tuple, get the non-empty group
                            pokemon_name = (match[0] or match[1]).strip() if isinstance(match, tuple) else match.strip()
                            # Check if it's in ALL_SPECIES (case-insensitive) and not a label like "Item", "Ability", etc.
                            pokemon_lower = pokemon_name.lower()
                            if pokemon_lower not in ['team name', 'author', 'item', 'ability', 'nature', 'evs', 'ivs', 'moves']:
                                if any(species.lower() == pokemon_lower for species in ALL_SPECIES):
                                    # Normalize to Showdown format for consistency
                                    pokemon_in_output.add(normalize_species_name(pokemon_name))
                    
                    # Remove the searched Pokémon from teammates list
                    # Note: pokemon_in_output already contains lowercase strings
                    teammates = [p for p in pokemon_in_output if p not in searched_pokemon_set]
                    
                    # Show exactly 1 sprite for EACH searched Pokémon (base form only)
                    # This ensures all Pokemon mentioned in the query are shown
                    for searched_pokemon in searched_pokemon_set:
                        matching_filenames = [
                            filename for filename in ALL_FILENAMES
                            if filename.lower().startswith(searched_pokemon)
                        ]
                        if matching_filenames:
                            # Take only the first matching filename (base form)
                            base_name = matching_filenames[0].replace('.png', '')
                            sprite_urls_lists.append([
                                f"https://play.pokemonshowdown.com/sprites/gen5/{base_name}.png"
                            ])
                    
                    # Show exactly 1 sprite for each teammate (each teammate gets 1 sprite, base form only)
                    # Limit teammates to keep total reasonable (max 8 total sprites)
                    max_teammates = max(0, 8 - len(searched_pokemon_set))
                    for teammate in teammates[:max_teammates]:
                        # teammate is already lowercase from pokemon_in_output
                        matching_filenames = []
                        for filename in ALL_FILENAMES:
                            base = filename.replace('.png', '').lower()
                            # Match exact name or forms (e.g., "landorus-therian", "iron-valiant")
                            if base == teammate or base.startswith(teammate + '-'):
                                matching_filenames.append(filename)
                        
                        if matching_filenames:
                            # Take only the first matching filename (base form) - exactly 1 sprite per teammate
                            base_name = matching_filenames[0].replace('.png', '')
                            sprite_urls_lists.append([
                                f"https://play.pokemonshowdown.com/sprites/gen5/{base_name}.png"
                            ])
                else:
                    # Strategy queries: Show all sprite variants (regular, shiny, back, back-shiny)
                    if pokemon_list:
                        for pokemon_name in pokemon_list[:8]:  # Limit to 8 Pokemon
                            pokemon_lower = pokemon_name.lower()
                            sprite_variants = []
                            
                            # Find ALL matching filenames for this Pokemon (all forms, variants, etc.)
                            matching_filenames = [
                                filename for filename in ALL_FILENAMES
                                if filename.lower().startswith(pokemon_lower)
                            ]
                            
                            # Add all 4 variants: regular, shiny, back, back-shiny
                            for filename in matching_filenames:
                                base_name = filename.replace('.png', '')
                                sprite_variants.extend([
                                    f"https://play.pokemonshowdown.com/sprites/gen5/{base_name}.png",
                                    f"https://play.pokemonshowdown.com/sprites/gen5-shiny/{base_name}.png",
                                    f"https://play.pokemonshowdown.com/sprites/gen5-back/{base_name}.png",
                                    f"https://play.pokemonshowdown.com/sprites/gen5-back-shiny/{base_name}.png"
                                ])
                            
                            if sprite_variants:
                                sprite_urls_lists.append(sprite_variants)
                
                # Create modern sprites HTML
                sprites_html = create_modern_sprites_html(sprite_urls_lists)
                
                return chat_history, sprites_html, ""
            except Exception as e:
                logger.error(f"Error in respond function: {e}", exc_info=True)
                error_msg = "❌ An error occurred. Please try again."
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": error_msg})
                return chat_history, "", ""
        
        def clear_chat():
            memory_manager.clear()
            return [], "", ""
        
        # Event handlers
        submit_btn.click(respond, [query, chatbot], [chatbot, pokemon_html, query])
        query.submit(respond, [query, chatbot], [chatbot, pokemon_html, query])
        clear_btn.click(clear_chat, outputs=[chatbot, pokemon_html, query])

    if __name__ == "__main__":
        logger.info("Starting Gradio application...")
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True
        )
except Exception as e:
    logger.critical(f"Failed to initialize Gradio application: {e}", exc_info=True)
    raise
