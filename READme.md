# 🧠 Pokémon AI Agent

A smart conversational assistant built with **LangChain** and **ChatGPT-4o Mini**, capable of handling advanced Pokémon strategy queries and analysis. It integrates tools like **Smogon**, **DuckDuckGo**, and competitive team data to provide fast, detailed, and natural explanations.

This project is designed for both **casual** and **competitive** players who want quick, high-quality strategic insights.

---

## 🚀 Features

### 🔎 1. General Pokémon Info  
Ask about **any Pokémon**, and the assistant returns clean, markdown-formatted summaries including:

- Typing  
- Abilities  
- Lore  
- General stats and usage  

> **Example:**  
> `What is Garchomp’s typing and ability?`

---

### ⚔️ 2. Competitive Strategy Insights  
Get detailed **strategy breakdowns** for specific Pokémon. Optionally, filter by **generation** and **tier**.

The AI analyzes the tool output and rewrites it **in its own words**—not copying raw text or HTML. You get a natural summary with:

- 🛡️ **Role**  
- 🧠 **Moveset**  
- 🤝 **Teammates**  
- ⚠️ **Threats**  
- 💡 **Tips**

> **Examples:**  
> `Charizard build in Gen7 OU`  
> `How do people use Umbreon in Gen8 UU?`

---

### 🧩 3. Team Search by Pokémon  
Ask for **sample teams** that include specific Pokémon, filtered by **generation** and **tier**.

Each team includes:

- Full Pokémon roster  
- Moves, abilities, natures, EVs/IVs  
- Showdown export format (📋)  
- Clean markdown layout  

> **Examples:**  
> `Charizard team Gen7 OU`  
> `Teams with Gliscor in Gen6`

---

## 🛠️ Tools Used

| Tool               | Purpose                                                     |
|--------------------|-------------------------------------------------------------|
| `smogon_tool`      | Retrieves movesets, strategies, and usage from Smogon       |
| `team_search_tool` | Finds sample teams based on Pokémon names and filters       |
| `ddgo_tool`        | Fetches general Pokémon info using DuckDuckGo               |
| `save_tool`        | Saves outputs or results for later reuse or export          |

> 🧠 These tools are dynamically called by the **LangChain agent**, depending on the user’s query.

---

## 🧰 Tech Stack

- 🐍 Python 3.10+  
- 🔗 LangChain  
- 🧠 OpenAI GPT-4o Mini (`ChatOpenAI`)  
- 📦 Pydantic (for structured outputs)  
- 🌐 BeautifulSoup4 (for HTML cleanup)  
- 🔤 Regex + markdown formatting helpers  

---

## 💬 Usage Tips

Try asking:

"Show me teams with Umbreon and Chansey."

"Find sample teams using Garchomp and Rotom-Wash in Gen 9 OU."

"Give me 3 VGC teams that include Flutter Mane and Iron Hands."

"Can you give me a Pokémon team with Skarmory and Blissey?"

"I want a stall team with Toxapex and Corviknight."

"List teams with Meowscarada in Gen 9 UU."

"Do you have any teams using Kingambit and Garganacl?

"What's a good moveset for Iron Valiant in OU?"

![Screenshot 2025-06-28 001957](https://github.com/user-attachments/assets/0e2ce7fc-a90b-4b65-abf0-a79b7e3b4a6a)

![Screenshot 2025-06-28 001842](https://github.com/user-attachments/assets/916f9b69-6538-4d26-afdb-c27e92f05b33)



"What are the strengths and weaknesses of a rain team?"

"Build a Hyper Offense team strategy around Dragapult."
