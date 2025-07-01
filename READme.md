# 🧠 Pokémon AI Agent

A smart conversational assistant built with LangChain and ChatGPT-4o Mini, capable of handling advanced Pokémon strategy queries and analysis. It integrates tools like Smogon, DuckDuckGo, and competitive team data to provide fast, detailed, and natural explanations.

This project is designed for both casual and competitive players who want quick, high-quality strategic insights.

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

The AI analyzes the tool output and rewrites it in its own words—not copying raw text or HTML. You get a natural summary with:

- 🛡️ Role  
- 🧠 Moveset  
- 🤝 Teammates  
- ⚠️ Threats  
- 💡 Tips  

**Examples:**  
> Charizard build in Gen7 OU  
> How do people use Umbreon in Gen8 UU?

---

### 🔁 3. Multi-Pokémon Strategy Comparison (NEW)  
Compare strategies, builds, and roles for **two or more Pokémon** side by side. This is useful for decisions like choosing team leaders or understanding type synergy.

**Example:**  
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

### 🧠 5. Conversational Memory (NEW)  
The assistant **remembers previous Pokémon or topics** mentioned in the current session using LangChain memory.

This means you can follow up with natural questions like:
> What were Gliscor’s threats again?  
> Add a teammate to that Umbreon build.  
> Can I see a rain team with the same Pokémon?

---

## 🛠️ Tools Used

| Tool              | Purpose                                               |
|-------------------|-------------------------------------------------------|
| `smogon_tool`     | Retrieves movesets, strategies, and usage from Smogon |
| `team_search_tool`| Finds sample teams based on Pokémon and filters       |
| `ddgo_tool`       | Fetches general Pokémon info from DuckDuckGo          |
| `save_tool`       | Saves outputs or builds for reuse or export           |

🧠 These tools are dynamically selected by a LangChain agent based on your query.

---

## 🧰 Tech Stack

- 🐍 Python 3.10+  
- 🔗 LangChain  
- 🧠 OpenAI GPT-4o Mini (ChatOpenAI)  
- 📦 Pydantic (for structured outputs)  
- 🌐 BeautifulSoup4 (for HTML cleanup)  
- 🔤 Regex + Markdown formatting helpers  
- 🖼️ Gradio (for future UI)

---

## 💬 Usage Tips

You can ask things like:

- "Show me teams with Umbreon and Chansey."  
- "Compare Charizard X and Y in Gen6."  
- "Give me 3 VGC teams with Flutter Mane and Iron Hands."  
- "What is a good moveset for Iron Valiant in OU?"  
- "What are the strengths of a rain team?"  
- "Build a Hyper Offense strategy around Dragapult."  
- "Remind me of Garchomp’s role again."  
- "Add a wallbreaker to the team with Skarmory."

---

## ✅ To Do
- Add tier usage stats and rankings  
- Better support for team builder UI  
- Export builds and summaries as PDF or Markdown  
- Type synergy checker  
- Visualization of team roles and weaknesses

---

## 📄 License
This project is licensed under the **MIT License**.
