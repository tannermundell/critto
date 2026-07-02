# AMD AI Academy — Plain-English Glossary

Running reference for the AI Developer path (AI Agents 101 & 201). Each entry: what it is, why it matters.

---

## The mental model: the 4-layer stack

Every agent you build stacks four swappable layers. Knowing which layer a thing belongs to is half the battle.

1. **Model** — the brain (e.g. Qwen3, Llama 3). Takes text in, produces text out, including structured "call this tool" requests. Knows nothing about how to actually run a tool.
2. **Inference server / engine** — serves the model as an API (e.g. vLLM, SGLang). Pure serving, no agent logic.
3. **Harness / agent framework** — the conductor (e.g. Pydantic-AI, CrewAI, LangGraph, Google ADK, Hermes Agent). Holds the prompt, registers tools, runs the tool-calling loop, manages connections.
4. **Tools** — external abilities (MCP servers: time, weather, Airbnb, etc.).

You can swap any layer without touching the others (swap Qwen for Llama, vLLM for SGLang, Pydantic-AI for CrewAI).

---

## AI Agents 101 — core terms

**AI Agent** — a model that doesn't just reply, it *decides and acts*: calls tools, reads results, loops until a task is done. The difference from a chatbot is action.

**Inference engine (vLLM, SGLang)** — open-source software that loads a model onto a GPU and exposes it as an API. You ran `vllm serve Qwen3` to do exactly this. Both are open-source and run on your own hardware (not proprietary cloud endpoints).

**Harness / agent framework** — the orchestration code wrapped around a model. Pydantic-AI, CrewAI, LangGraph, Google ADK, Hermes Agent, OpenClaw are all harnesses — interchangeable conductors. NOT models.

**Tool calling / function calling** — the loop where a model triggers a function:
1. You ask a question.
2. Harness sends the prompt + the list of available tools (name, description, params) to the model.
3. Model emits a structured tool-call request (not prose).
4. Harness catches it, runs the real function, gets the result.
5. Harness feeds the result back to the model.
6. Model writes the final answer.
The model never runs the tool itself — it requests; the harness executes.

**MCP (Model Context Protocol)** — a standard "universal adapter" for plugging tools and data into a model. One protocol; any compliant tool connects. Saves hand-wiring each tool to each model.

**MCP architecture (Host / Client / Server)** — the chain is:
`Model ↔ Host (agent app) ↔ MCP Client ↔ MCP Server ↔ real tool/API`.
The model speaks tool-calls; the client speaks MCP; the host brokers between them. The model never touches the server directly.

**MCP primitives (the 3 things a server exposes):**
- **Tools** — actions the *model* chooses to run; have effects (call an API, write a file). Model-controlled.
- **Resources** — data the server makes available to *read into context* (a file, DB rows, a document). Read-oriented. App-controlled.
- **Prompts** — pre-built templates/workflows a *user* triggers. User-controlled.
(Most people only ever use Tools and miss the other two.)

**MCP transports (where the server runs):**
- **stdio** — server runs as a local subprocess on the same machine (`MCPServerStdio`). What the course used.
- **HTTP/streaming** — server runs remotely; the client connects over the network (needs a URL + auth).

**Tool schema = source of truth** — the model learns a tool's real name and parameters from the *registered schema* (auto-generated from the function + docstring), NOT from the system-prompt text. If a tool silently never fires, check the registered schema first. The system prompt is only a hint.

**Universal MCP config format** — every MCP server publishes setup as JSON with `command`, `args`, `env`. You translate that into whatever harness you use (e.g. into Pydantic-AI's `MCPServerStdio`). Same config, any harness.

**Agentic chaining** — multiple tools/servers used in sequence, with the model deciding the order (e.g. get date → get forecast → search listings → recommend). This sequencing is what makes it an *agent*, and it's the "beyond RAG" behaviour the hackathon wants.

---

## AI Agents 201 — multi-agent terms

**Multi-agent system** — instead of one generalist agent holding many tools, *several specialist agents* that coordinate, each with a narrow job, its own tools, and its own prompt. More reliable and easier to debug than one overloaded agent.

**Orchestration patterns** — how agents are wired together: a supervisor delegating to workers, sequential handoffs, or hierarchies. The heart of multi-agent design.

**A2A (Agent-to-Agent) protocol** — a standard handshake so independent agents can talk *regardless of framework or owner*. "HTTP for agents." Lets your agent transact with someone else's agent without knowing how it was built.
- **MCP vs A2A:** MCP = agent → tools/data. A2A = agent → agent. Different jobs.
- Matters most when crossing a boundary (different company, different framework). For a multi-agent system you fully control, you usually don't need it — one framework is simpler.

**Agent Card** — a JSON "business card" an agent publishes: its identity, capabilities, endpoint (how to reach it), and auth needs. The foundation of *discovery* — how one agent finds out another exists and what it can do. It's the MCP tool schema idea, one level up (agent-to-agent instead of agent-to-tool). A2A flow: **discover** (read the Agent Card) → **communicate** (talk via A2A).

**Google ADK (Agent Development Kit)** — a Google agent framework/harness. Known for built-in context management via Session / State / Memory.

**Session** — one conversation thread; the container for a single interaction's back-and-forth. (One chat window.)

**State** — the scratchpad *within* a session; key-value data the agent reads/writes mid-task. Short-term; lives and dies with the session. (What's on your desk during one meeting.)

**Memory** — recall *across* sessions; persisted beyond a single conversation so the agent remembers later. Long-term. (The filing cabinet of all past meetings.)
- Key distinction: **State = within this conversation; Memory = across conversations.**

---

## Choosing a harness — Framework vs. Platform

Harnesses come in two categories. They don't compete on the same axis; pick by the job.

**Framework / SDK (Google ADK, CrewAI, LangGraph, Pydantic-AI)** — you write code to build the agent. More work, full control, you own the codebase. "Buy lumber, build the cabinet."
- Worth it for: custom products, fine control of orchestration/state, embedding agents in your own app, anything you need to own, ship, or stand behind (the hackathon entry; Aigeus as a sold product).

**Platform / app (Hermes Agent, OpenClaw)** — install it; the harness, connectors, memory, scheduling, subagents ship built-in. You configure a pre-built agent. Fast, less control, you inherit their architecture. "Buy the flat-pack."
- Worth it for: speed, standard integrations out of the box, personal/internal ops automation, fast prototypes.

**Rule of thumb:** speed + standard connectors → platform (Hermes). Control + ownership + customization → framework (ADK/etc.). For a compliance/security product like Aigeus, ownership of the stack and data flow is part of the value, so lean framework.

**Learning note:** the academy teaches frameworks so you understand the internals — what a platform like Hermes is doing for you under the hood. Build one cabinet from lumber before judging the flat-pack.

---

## LiteLLM and the "universal adapter" pattern

**LiteLLM** — a universal adapter for *models*. An open-source layer that lets you call 100+ LLM providers (OpenAI, Anthropic, Google, local vLLM/Ollama) through one OpenAI-compatible interface. Change a string, switch models — same code. Comes as a library (`litellm.completion(...)`) or a proxy/gateway (a server that routes to many models and handles keys, fallbacks, cost tracking).
- **Why it appears in the course:** Google ADK is built to want Gemini. LiteLLM is the bridge that lets ADK talk to *open* models (Llama/Qwen) served by vLLM on the AMD GPU. It's how a Google framework runs non-Google models on AMD hardware.
- **For you:** no model lock-in. Develop against a cheap API, swap one line to run on the AMD-served model. Aigeus is never married to one model vendor.

**The universal-adapter pattern (the big unifying idea)** — the same trick shows up at three layers. One standard interface so you don't hand-wire every combination:
- **LiteLLM** = adapter for *models* (harness → any model provider).
- **MCP** = adapter for *tools* (agent → any tool).
- **A2A** = adapter for *agents* (agent → any other agent).
(It's also exactly what vLLM's OpenAI-compatible API gave you — LiteLLM just generalizes it to every provider.)

---

## Multi-agent build patterns (from the Purchasing Concierge capstone)

**A2A Client vs Server (roles):**
- **A2A Client** — the agent that *initiates* a request (the root/orchestrator). In the demo: the Purchasing Concierge.
- **A2A Server** — an agent exposing an HTTP endpoint that *accepts* tasks and returns results. In the demo: the Burger and Pizza sellers.

**Agent Card discovery (`/.well-known/agent.json`)** — a server agent publishes its Agent Card at this standard URL. The client agent fetches it to discover who the agent is and what it can do. (Saw it live: the root agent GET'd this from both sellers and registered them.)

**Task / Message** — the units of A2A exchange. A **Task** is one unit of work ("place a burger order"); it's made up of **Messages**.

**CrewAI structure: Agent → Task → Crew → Output** — CrewAI's pipeline. Agent (role/goal/tools/LLM) + Task (the work + expected output) linked by a Crew (the orchestrator that runs it). Tasks must run through a Crew.

**LangGraph ReAct loop** — LangGraph builds an agent as a graph running Reason → Act → Observe: reason about the request, act by calling a tool, observe the result, repeat until done.

**Background-thread serving** — running an always-on agent server inside a thread so the notebook cell returns and stays usable. Same "blocking process" problem as `vllm serve`, solved with a thread instead of a separate terminal.

**Structured-output reliability / silent failure (the keeper)** — same code, two model-serving setups, two outcomes: vLLM (full-precision) returned clean structured output; Ollama (quantized) ran the tool but failed to return the strict structured response, so the agent reported failure even though the action succeeded. Lessons: (1) model choice + serving + quantization directly affect output reliability; (2) "silent success with a failure message" is a dangerous pattern — independently verify the action happened rather than trusting the model's structured response alone. Critical for compliance-grade work (Aigeus).

---

*Add to this as the courses continue.*
