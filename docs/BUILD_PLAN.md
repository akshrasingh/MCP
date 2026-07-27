# 📋 Full Detailed Build Plan — AI Travel Planner

> This is the original phase-by-phase build plan used to develop this project.
> It's kept here for reference/history. For the current project overview, setup,
> and usage instructions, see the main [README.md](../README.md).

This expands the phases into **concrete, ordered, sub-tasks** — including what to test, what "done" looks like, and what mistakes to avoid at each step.

---

## 🎯 Guiding Principle
**Build vertically, not horizontally.** Get one full path (User → Agent → MCP Client → 1 Server → back) working end-to-end before adding breadth (more servers/tools). This is exactly how Day 3 worked — you didn't build `calculator`, `search`, `current_time`, `finish` all at once and then test; you'd have struggled to debug 4 things simultaneously.

---

## 🧱 PHASE 0 — Environment & Skeleton (30–45 min)

### Steps
1. Create virtual environment:
   ```powershell
   cd "c:\Users\akshrasingh\OneDrive - Microsoft\Desktop\AIFoundry\Projects\AI Travel Planner"
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Write `requirements.txt`:
   ```
   ollama
   mcp
   pydantic
   pytest
   ```
3. Install: `pip install -r requirements.txt`
4. Write `config.py` — just constants, no logic:
   - `MODEL_NAME`, `TEMPERATURE`, `MAX_STEPS`, `MAX_HISTORY`
   - `MCP_SERVERS` — a list/dict describing how to launch each server (command + args), even if only `weather_server` is filled in for now.

### ✅ Definition of Done
- `pip install -r requirements.txt` succeeds.
- `python -c "import config; print(config.MODEL_NAME)"` runs without error.

### ⚠️ Common Mistake to Avoid
Don't start writing `agent.py` yet — you have nothing to call.

---

## 🌦️ PHASE 1 — First MCP Server (Weather) — Prove the Protocol (1–2 hrs)

### Step 1.1 — `provider.py` (pure business logic, no MCP yet)
- Write `get_weather(location: str, date: str) -> dict` returning **hardcoded fake data**:
  ```python
  {"location": "Tokyo", "date": "2026-08-01", "condition": "Sunny", "temp_c": 28}
  ```
- **Test this in isolation first**: `python -c "from provider import get_weather; print(get_weather('Tokyo','2026-08-01'))"`

### Step 1.2 — `server.py` (MCP wrapper)
- Use the `mcp` SDK's server pattern to expose `get_weather` as a tool with a JSON schema (name, description, params).
- Implement `list_tools()` and `call_tool()` per MCP spec.
- Run it standalone: `python server.py` — it should sit and listen (stdio or HTTP).

### Step 1.3 — Throwaway test client
- Write a **temporary script** (`scratch_test_weather.py`, not part of final app) that:
  1. Spawns `server.py` as a subprocess (or connects via HTTP).
  2. Calls `list_tools()` → prints the schema.
  3. Calls `call_tool("get_weather", {"location": "Tokyo", "date": "2026-08-01"})` → prints result.
- Delete/archive this script once it works — it was just a protocol sanity check.

### ✅ Definition of Done
You've called `get_weather` **through the actual MCP wire protocol**, not a direct Python import, and gotten correct JSON back.

### ⚠️ Common Mistake
Don't try to build all 6 servers' `provider.py` files at once "to save time" — you won't know if failures are protocol issues or business-logic issues.

---

## 🔌 PHASE 2 — MCP Client Layer (1–2 hrs)

### Step 2.1 — `transport.py`
- Abstract the connection mechanism: for now, just subprocess + stdio (simplest MCP transport).
- Function: `start_server_process(command, args) -> connection_handle`

### Step 2.2 — `client.py`
- `MCPClient` class:
  - `connect(server_configs: list)` — starts each configured server, performs MCP `initialize` handshake.
  - `list_tools() -> list[ToolSchema]` — aggregates tools from all connected servers.
  - `call_tool(name, args) -> result` — routes to the correct server based on which one registered that tool name.

### Step 2.3 — `tool_catalogue.py`
- `ToolCatalogue.describe_all() -> str` — formats all discovered tools into a prompt-injectable string (like Day 3's `tool_descriptions()`, but dynamic).

### Step 2.4 — Test
- Write `tests/test_mcp_client.py`:
  ```python
  def test_connect_and_call_weather():
      client = MCPClient()
      client.connect([weather_server_config])
      result = client.call_tool("get_weather", {"location": "Tokyo", "date": "2026-08-01"})
      assert "temp_c" in result
  ```

### ✅ Definition of Done
`pytest tests/test_mcp_client.py` passes — MCP Client can talk to the weather server without any Agent/Planner involved.

---

## 🧠 PHASE 3 — Port the ReAct Core from Day 3 (2–3 hrs)

Do these **in this exact order** — each depends on the previous:

### Step 3.1 — `agent/memory.py`
- Copy Day 3's `Memory` class almost verbatim.
- Test standalone: add 2 fake steps, call `format_for_prompt()`, verify text output looks right.

### Step 3.2 — `agent/llm.py`
- Copy Day 3's `call_llm()` wrapper.
- Test standalone: call it with a simple prompt, verify Ollama responds.

### Step 3.3 — `agent/prompts/system_prompt.py`
- Write the ReAct system prompt template, but leave a placeholder `{tool_catalogue}` to be filled in dynamically at runtime (unlike Day 3's static prompt).

### Step 3.4 — `agent/planner.py`
- Copy Day 3's `Planner` structure:
  - `build_prompt(query, memory, tool_catalogue)` — now takes tool catalogue as a parameter, injected by Agent.
  - `plan(query, memory, tool_catalogue)` — calls LLM.
  - `parse_response(raw_text)` — same regex parsing as Day 3.
- Test standalone: mock a `tool_catalogue` string, call `plan()` with a fake query, verify the parsed dict looks right.

### Step 3.5 — `agent/agent.py`
- Copy Day 3's loop structure, but:
  - Constructor takes an `MCPClient` instance instead of a static `TOOLS` dict.
  - Tool execution: `observation = self.mcp_client.call_tool(tool_name, kwargs)` instead of `execute_tool(tool, **kwargs)`.
  - Everything else (memory storage, final_answer check, MAX_STEPS loop) is identical to Day 3.

### Step 3.6 — `main.py`
- Starts the weather MCP server, builds `MCPClient`, connects it, builds `Agent(mcp_client)`, runs the REPL (same shape as Day 3's `main.py`).

### ✅ Definition of Done — 🏁 MILESTONE 1
Run `python main.py`, ask **"What's the weather in Tokyo tomorrow?"**, and get a correct answer through the full stack: `main → agent → planner → llm → parse → mcp_client → weather_server → provider → back up → finish`.

**This is your biggest checkpoint. Don't move to Phase 4 until this works reliably.**

---

## 🔁 PHASE 4 — Add Remaining Servers One at a Time (1–2 hrs each)

Repeat this **exact recipe** for each server, in this order (easiest → hardest):

| Order | Server | Why this order |
|---|---|---|
| 1 | `currency_server` | Simplest — pure math, no external API needed even mocked |
| 2 | `flight_server` | Slightly more complex mock data (list of flight options) |
| 3 | `hotel_server` | Similar shape to flights |
| 4 | `maps_server` | Needed before itinerary composer |

For **each** server:
1. Write `provider.py` (mocked data) → test standalone.
2. Write `server.py` (MCP wrapper) → test standalone with a throwaway script.
3. Add its config to `config.py`'s `MCP_SERVERS` list.
4. Restart `main.py` — **no code changes needed in `agent.py`/`planner.py`/`mcp_client.py`** — verify the LLM can now pick between multiple tools correctly.

### ✅ Definition of Done — 🏁 MILESTONE 2
Ask a question requiring 2+ tools (e.g., "Find me a flight to Tokyo and convert $500 to JPY") and watch the agent correctly chain multiple tool calls across different servers in one run.

### ⚠️ Common Mistake
If the LLM starts picking the wrong tool as you add more, it's a **prompt/description problem** (tool descriptions in `provider`/`server.py` too vague) — not an architecture bug. Fix descriptions, don't add hacky routing logic.

---

## 🗺️ PHASE 5 — Itinerary Composer (1–2 hrs)

1. `mcp_servers/itinerary_server/composer.py` — pure function `build_itinerary(weather, flights, hotels, places) -> str`. Test standalone with fake inputs.
2. `mcp_servers/itinerary_server/server.py` — exposes `generate_itinerary(...)` as an MCP tool.
3. Add to `config.py`'s server list.
4. Optionally refine `agent/prompts/itinerary_prompt.py` if you want the final LLM output formatted nicely (e.g., markdown day-by-day).

### ✅ Definition of Done — 🏁 MILESTONE 3
Ask **"Plan my 3-day trip to Tokyo, budget $2000"** and get a full day-by-day itinerary, built from multiple chained tool calls + the composer tool.

---

## 💾 PHASE 6 — Session Management (1 hr)

1. `session/session_manager.py`:
   - `get_context(session_id) -> dict`
   - `update_context(session_id, key, value)`
   - In-memory dict is fine for now (no DB needed yet).
2. Update `main.py`'s REPL loop:
   - Maintain one `session_id` for the whole conversation.
   - Before calling `agent.run(query)`, merge session context into the query/prompt (e.g., inject "Destination: Tokyo, Budget: $2000" if not restated).
   - After each turn, update session context based on what was discussed.

### ✅ Definition of Done — 🏁 MILESTONE 4
Multi-turn conversation works:
```
> Plan a trip to Tokyo
> Now find me a hotel   ← no need to repeat "Tokyo"
> What about currency conversion for $2000?
```

---

## ✅ PHASE 7 — Tests + Polish (1–2 hrs)

1. `tests/test_memory.py` — add/format/clear behavior.
2. `tests/test_planner.py` — mock LLM response, verify parsing.
3. `tests/test_mcp_client.py` — already written in Phase 2, expand for each server.
4. `evaluation/test_cases.py` — 3–5 end-to-end scenarios with assertions on final answer content.
5. Update `README.md` — replace this build-plan doc with the **actual final project README** (overview, architecture diagram, how to run, example queries).

### ✅ Definition of Done — 🏁 PROJECT COMPLETE
`pytest` passes all tests, `README.md` accurately describes the finished system, and you can demo 3 different query types (single-tool, multi-tool, multi-turn) live.

---

## 📊 Total Time Estimate

| Phase | Time |
|---|---|
| 0 — Foundation | 30–45 min |
| 1 — First MCP server | 1–2 hrs |
| 2 — MCP Client | 1–2 hrs |
| 3 — Agent core (Milestone 1) | 2–3 hrs |
| 4 — Remaining 4 servers | 4–8 hrs (1–2 hrs × 4) |
| 5 — Itinerary composer | 1–2 hrs |
| 6 — Session management | 1 hr |
| 7 — Tests + polish | 1–2 hrs |
| **Total** | **~12–20 hrs** (spread across several days) |
