# 🧠 Pokémon AI Agent

A smart conversational assistant built with LangChain and ChatGPT-4o Mini, capable of handling advanced Pokémon strategy queries and analysis. It integrates tools like Smogon, DuckDuckGo, and competitive team data to provide fast, detailed, and natural explanations.

This project is designed for both casual and competitive players who want quick, high-quality strategic insights.

Data for this are taken from: https://github.com/pkmn/smogon/tree/main
---

## 🚀 Features

### 🔎 1. General Pokémon Info
Ask about any Pokémon, and the assistant returns clean, markdown-formatted summaries including:

- Typing  
- Abilities  
- Lore  
- General stats and usage

**Example:**  
> What is Garchomp’s typing and ability?

---

### ⚔️ 2. Competitive Strategy Insights  
Get detailed strategy breakdowns for specific Pokémon. Optionally, filter by generation and tier.

The AI analyzes tool outputs and rewrites them in its own words—not copying raw text or HTML. You get a natural summary with:

- 🛡️ Role  
- 🧠 Moveset  
- 🤝 Teammates  
- ⚠️ Threats  
- 💡 Tips

**Examples:**  
> Charizard build in Gen7 OU  
> How do people use Umbreon in Gen8 UU?

---

### 🔁 3. Multi-Pokémon Strategy Comparison
Compare strategies, builds, and roles for two or more Pokémon side by side. Useful for building balanced teams or understanding synergy.

**Examples:**  
> Compare Charizard X and Y in Gen6 OU  
> What are the roles of Garchomp and Landorus-T in Gen9 OU?

---

### 👥 4. Team Search by Pokémon  
Ask for sample teams that include specific Pokémon, filtered by generation and tier.

Each team includes:

- Full Pokémon roster  
- Moves, abilities, natures, EVs/IVs  
- Showdown export format (📋)  
- Clean markdown layout

**Examples:**  
> Charizard team Gen7 OU  
> Teams with Gliscor in Gen6

---

### 🧠 5. Conversational Memory 
The assistant remembers previously mentioned Pokémon and topics in the session using LangChain memory.

**Examples:**  
> What were Gliscor’s threats again?  
> Add a teammate to that Umbreon build.  
> Can I see a rain team with the same Pokémon?

---

### 🖼️ 6. Smart UI with Pokémon Sprites 
Built with **Gradio**, the assistant now includes an intuitive and visual interface:

- 🖼️ **Image gallery preview** of detected Pokémon and all variants (e.g. mega, gmax, hisui, paldea forms)  
- 🔍 **Automatic sprite detection** and display above the chatbox (based on your question)  
- 💬 **Clean markdown chat output** (no duplicate images in chat bubbles)  
- Responsive layout that adapts across screen sizes  

**Example:**  
`What's the best set for Tyranitar in Gen3?`  
→ You'll see `Tyranitar` and `Tyranitar-Mega` sprites above the chat, and a detailed markdown strategy below.

---

### 📊 7. Interactive Pokémon Stats Card
Click on any Pokémon sprite to open a detailed stats card with comprehensive information:

**Physical Attributes:**
- 📏 **Height** (in meters)
- ⚖️ **Weight** (in kilograms)
- 🎨 **Type(s)** - Color-coded type badges (Fire, Water, Grass, etc.)
- 📐 **Shape** - Physical body shape classification
- 🎨 **Color** - Primary color classification
- 🥚 **Egg Group(s)** - Breeding compatibility groups

**Abilities:**
- 💪 **All Abilities** - Including hidden abilities
- 📝 **Ability Descriptions** - Hover over ability badges to see detailed descriptions
- 🏷️ **Hidden Ability Indicator** - Clearly marked hidden abilities

**Base Stats:**
- ❤️ **HP** - Hit Points
- ⚔️ **Attack** - Physical attack power
- 🛡️ **Defense** - Physical defense
- 🔮 **Sp. Atk** - Special attack power
- 🛡️ **Sp. Def** - Special defense
- ⚡ **Speed** - Speed stat
- 📊 **Total** - Sum of all base stats

**Visual Features:**
- 🖼️ **Official Artwork** - High-quality official Pokémon artwork
- 🌈 **Color-Coded Stat Bars** - Visual representation with dynamic colors:
  - Red for stats below 70
  - Yellow for stats 70-90
  - Green for stats 90-100
  - Bright green for stats 100-120
  - Blue-teal for stats 120-130
  - Deep blue-teal for stats 130+
- 🎨 **Type-Based Background** - Gradient backgrounds matching Pokémon types
- 🔴 **Mega Evolution Indicator** - Special "MEGA" badge for Mega forms
- 🎯 **Animated Stat Bars** - Smooth animations when stats load

**How to Use:**
Simply click on any Pokémon sprite in the sidebar to view its complete stats card. The modal can be closed by clicking the X button, clicking outside the modal, or pressing the Escape key.

**Data Source:** All Pokémon data is fetched from [PokeAPI](https://pokeapi.co/), providing accurate and up-to-date information.

---

## 🛠️ Tools Used

| Tool               | Purpose                                                |
|--------------------|--------------------------------------------------------|
| `smogon_tool`      | Retrieves movesets, strategies, and usage from Smogon |
| `team_search_tool` | Finds sample teams based on Pokémon and filters       |
| `ddgo_tool`        | Fetches general Pokémon info from DuckDuckGo          |
| `save_tool`        | Saves outputs or builds for reuse or export           |

🧠 These tools are dynamically selected by a LangChain agent based on your query.

---

## 🧰 Tech Stack

- 🐍 Python 3.10+  
- 🔗 LangChain  
- 🧠 OpenAI GPT-4o Mini (`ChatOpenAI`)  
- 📦 Pydantic  
- 🌐 BeautifulSoup4  
- 🧹 Regex + Markdown formatting helpers  
- 🖼️ Gradio (interactive UI with custom CSS styling)

---

## 💬 Usage Tips

Ask things like:

- "Show me teams with Umbreon and Chansey."
- "Compare Charizard X and Y in Gen6."
- "Give me 3 VGC teams with Flutter Mane and Iron Hands."
- "What is a good moveset for Iron Valiant in OU?"
- "What are the strengths of a rain team?"
- "Build a Hyper Offense strategy around Dragapult."
- "Remind me of Garchomp’s role again."
- "Add a wallbreaker to the team with Skarmory."

![image](https://github.com/user-attachments/assets/57b6c657-bb1c-4fdd-ad8f-3143ef2e4c32)

---

## 📚 Data Sources & Credits

This project uses data and assets from the following sources:

### 🎮 Smogon Data
**Competitive Pokémon strategy data** (movesets, analyses, team compositions) is sourced from:
- **Smogon University**: [https://www.smogon.com/](https://www.smogon.com/)
  - Smogon is a community-driven resource for competitive Pokémon battling
  - Data includes analyses, usage statistics, and team sets across multiple generations and tiers
  - All strategy information, movesets, and competitive insights come from Smogon's comprehensive database

### 🖼️ Pokémon Sprites
**Pokémon sprite images** are sourced from:
- **Pokémon Showdown**: [https://play.pokemonshowdown.com/sprites/gen5/](https://play.pokemonshowdown.com/sprites/gen5/)
  - Pokémon Showdown is the official battle simulator that hosts sprite assets
  - Sprites include all Pokémon forms (Mega, G-Max, Regional variants, etc.)
  - Used for visual display in the Gradio UI interface

**Note:** This project is not affiliated with Smogon University or Pokémon Showdown. All data and assets are used for educational and research purposes in accordance with their respective terms of use.

---

## 📸 Screenshots

### Main Interface
![Pokémon Strategy Assistant Interface](https://github.com/user-attachments/assets/main-interface)

The main interface features a clean, modern design with:
- Quick action buttons for common queries
- Sidebar showing detected Pokémon sprites
- Main chat area for strategy discussions
- Team search and comparison capabilities

### Pokémon Stats Card
![Pokémon Stats Card](https://github.com/user-attachments/assets/pokemon-stats-card)

Interactive stats card showing comprehensive Pokémon information including:
- Official artwork
- Physical attributes (height, weight, type, shape, color, egg groups)
- Abilities with descriptions
- Color-coded base stats with animated progress bars

### Team Search Results
![Team Search Results](https://github.com/user-attachments/assets/team-search-results)

Team search functionality displaying:
- Complete team compositions
- Individual Pokémon builds with moves, abilities, and EVs
- Team strategies and synergies
- Showdown export format

### Comparison Feature
![Pokémon Comparison](https://github.com/user-attachments/assets/pokemon-comparison)

Side-by-side comparison of multiple Pokémon showing:
- Movesets
- Roles and strategies
- Strengths and weaknesses
- Usage recommendations

---


