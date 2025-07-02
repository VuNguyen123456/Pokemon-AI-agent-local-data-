import gradio as gr
import re
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from typing import List
from dotenv import load_dotenv

# tools:
from tools import ddgo_tool, save_tool, clean_smogon_tool, team_search_tool, fix_markdown_headers_spacing, ALL_SPECIES, extract_species_tier_gen
from models import TeamSearchResult, AllTeamSearchResult, TeamPokemon 
from utils import general_prompt, strat_prompt_single, strat_prompt_team, strat_prompt_multi, format_strategy_team_output, format_multiple_teams_output, suffixes, ALL_FILENAMES

load_dotenv()



tools = [ddgo_tool, save_tool, clean_smogon_tool, team_search_tool]
last_pokemon_list = []
llm = ChatOpenAI(model = "gpt-3.5-turbo") 
  # or gpt-3.5-turbo

def format_strategy_markdown(output: str) -> str:
    # Replace \n with actual newlines
    output = output.replace("\\n", "\n")

    # Highlight section titles
    output = output.replace("Moveset", "### 🧠 Moveset")
    output = output.replace("Role", "### 🛡️ Role")
    output = output.replace("Teammates", "### 🤝 Teammates")
    output = output.replace("Threats", "### ⚠️ Threats")
    output = output.replace("Tips", "### 💡 Tips")

    # Add markdown formatting for lists
    output = output.replace("- ", "- ")

    return output.strip()

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, input_key="query")

def add_pokemon_image(pokemon_name):
    base_url = "https://play.pokemonshowdown.com/sprites/gen5/"
    return f"![{pokemon_name} sprite]({base_url}{pokemon_name.lower()}.png)\n"

# def format_strategy_markdown(output: str) -> str:
#     output = output.replace("\\n", "\n")
#     # Add image at the top if Pokémon name is found
#     for name in ALL_SPECIES:
#         if name in output:
#             output = add_pokemon_image(name) + output
#             break
#     # Continue your section formatting...
#     return output.strip()

def chat_with_agent(query, chat_history):
    global last_pokemon_list

    # Extract Pokémon, tier, and gen
    pokemon_list, tier, gen = extract_species_tier_gen(query)

    # Clear memory only if new Pokémon are detected
    if pokemon_list and set(pokemon_list) != set(last_pokemon_list):
        print(f"[DEBUG] New Pokémon detected: {pokemon_list}, clearing memory.")
        memory.clear()
        last_pokemon_list = pokemon_list.copy()

    # Prompt selection logic...
    if re.search(r"\bteam(s|ing)?\b", query, re.IGNORECASE):
        prompt = strat_prompt_team
    elif re.search(r"\b(strategy|build|moveset|compare|vs)\b", query, re.IGNORECASE) and (" and " in query.lower() or "," in query):
        prompt = strat_prompt_multi
    elif re.search(r"\b(strategy|build|weakness|strength|moves|items|abilities)\b", query, re.IGNORECASE):
        prompt = strat_prompt_single
    else:
        prompt = general_prompt

    # Agent execution...
    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False)

    response = agent_executor.invoke({
        "query": query,
        "name": "Pokemon Research Assistant"
    })

    # Format result
    if isinstance(response, AllTeamSearchResult):
        output = format_multiple_teams_output(response.teams)
    else:
        output = fix_markdown_headers_spacing(str(response))

    return output, chat_history


# 🖼️ Gradio UI
with gr.Blocks(theme="soft") as demo:
    gr.Markdown("## 🧠 Pokémon Strategy Assistant")
    
    # Add image area for showing Pokémon sprite
    pokemon_gallery = gr.Gallery(label="Pokémon Sprites", visible=False, columns=6, height=120)

    chatbot = gr.Chatbot(type="messages", render_markdown=True, height=500)
    query = gr.Textbox(placeholder="Ask about teams, builds, or matchups...")

    def get_pokemon_image_urls_from_text(text: str) -> List[str]:
        text = text.lower()
        matches = []
        sprite_base_url = "https://play.pokemonshowdown.com/sprites/gen5/"

        for species in ALL_SPECIES:
            base_name = species.lower()
            if base_name in text:
                for filename in ALL_FILENAMES:
                    if filename.startswith(base_name):
                        matches.append(f"{sprite_base_url}{filename}")
                break  # Only match the first Pokémon found in the text

        return matches




    def respond(message, chat_history):
        output, chat_history = chat_with_agent(message, chat_history)
        formatted_output = format_strategy_markdown(output)

        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": formatted_output})

        image_urls = get_pokemon_image_urls_from_text(message)
        if image_urls:
            return "", chat_history, gr.update(value=image_urls, visible=True)
        else:
            return "", chat_history, gr.update(visible=False)


    query.submit(respond, [query, chatbot], [query, chatbot, pokemon_gallery])


demo.launch()

# # 🖼️ Gradio UI
# with gr.Blocks(theme="soft") as demo:
#     gr.Markdown("## 🧠 Pokémon Strategy Assistant")
#     chatbot = gr.Chatbot(type="messages", render_markdown=True, height=500)
#     query = gr.Textbox(placeholder="Ask about teams, builds, or matchups...")

#     def respond(message, chat_history):
#         output, chat_history = chat_with_agent(message, chat_history)
#         formatted_output = format_strategy_markdown(output)

#         # Add both user and assistant messages
#         chat_history.append({"role": "user", "content": message})
#         chat_history.append({"role": "assistant", "content": formatted_output})

#         return "", chat_history


#     query.submit(respond, [query, chatbot], [query, chatbot])


# demo.launch()
