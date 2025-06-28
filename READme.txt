🧠 Pokémon AI Agent
A smart conversational assistant built using LangChain and ChatGPT-4o Mini, capable of performing advanced Pokémon strategy queries and analysis with integrated tools like Smogon, DuckDuckGo, and Pokémon team data search.

This project is designed for both casual and competitive players who want quick and high-quality strategic insights.

🚀 Features
🔎 1. General Pokémon Info
Ask about any Pokémon, and the agent will return well-formatted general details including types, abilities, lore, and more using natural language with markdown, emojis, and bullet points.

Example:
What is Garchomp’s typing and ability?

⚔️ 2. Competitive Strategy Insights
Get detailed strategy analysis for a specific Pokémon, with optional filters like generation and tier.

The AI summarizes movesets, roles, team synergies, threats, and usage tips in its own natural language—no raw dumps from tools or HTML clutter.

Example:
Charizard build in Gen7 OU
How do people use Umbreon in Gen8 UU?

You’ll receive a clean summary including:

🛡️ Role

🧠 Moveset

🤝 Teammates

⚠️ Threats

💡 Tips

🧩 3. Team Search by Pokémon
Search for competitive teams that include a specific Pokémon, optionally filtered by generation and tier.

Each team result contains:

Pokémon names, movesets, abilities, EVs, and IVs

Team export (Pokémon Showdown format)

Markdown layout for easy reading

Example:
Charizard team Gen7 OU
Teams with Gliscor in Gen6

🛠️ Tools Used
Tool	Purpose
smogon_tool	Strategy data (moves, sets, usage, etc.)
team_search_tool	Retrieve actual sample teams including specified Pokémon
ddgo_tool	General info via DuckDuckGo
save_tool	Save outputs and ideas for reuse or export

All tools are wrapped inside a LangChain agent which determines what tools to use based on the user query.

🧰 Tech Stack
Python 3.10+

LangChain

OpenAI GPT-4o (Mini) via ChatOpenAI

Pydantic for structured tool output

BeautifulSoup4 for HTML cleanup

Re and markdown formatting helpers

💬 Usage Tips
You can type:

"Show me teams with Umbreon and Chansey."

"Find sample teams using Garchomp and Rotom-Wash in Gen 9 OU."

"Give me 3 VGC teams that include Flutter Mane and Iron Hands."

"Can you give me a Pokémon team with Skarmory and Blissey?"

"I want a stall team with Toxapex and Corviknight."

"List teams with Meowscarada in Gen 9 UU."

"Do you have any teams using Kingambit and Garganacl?

"What's a good moveset for Iron Valiant in OU?"

"What are the strengths and weaknesses of a rain team?"

"Build a Hyper Offense team strategy around Dragapult."

✅ To Do
 Add leaderboard or ranking data

 Optimize team search filters by usage stats

 Add GUI version with search and strategy tabs

 Export results to Markdown or PDF

📄 License
This project is licensed under the MIT License.