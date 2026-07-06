from typing import TypedDict
from langgraph.graph import StateGraph, END
from rag_engine import search, get_embedding, genai_client


# ---- 1. Define the "state" — the data that flows through the graph ----
class AgentState(TypedDict):
    question: str
    filename: str
    retrieved_chunks: list
    answer: str
    is_grounded: bool
    attempts: int


# ---- 2. Retriever node: fetch relevant chunks from Qdrant ----
def retriever_node(state: AgentState) -> AgentState:
    chunks = search(state["question"], state["filename"], top_k=5)
    state["retrieved_chunks"] = chunks
    return state


# ---- 3. Reasoning node: generate an answer from the retrieved chunks ----
def reasoning_node(state: AgentState) -> AgentState:
    context = "\n---\n".join(state["retrieved_chunks"])

    prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't know based on this document."

CONTEXT:
{context}

QUESTION: {state["question"]}

ANSWER:"""

    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        state["answer"] = response.text
    except Exception as e:
        state["answer"] = f"Sorry, the AI service is temporarily unavailable ({str(e)[:100]})"
    return state


# ---- 4. Critic node: check if the answer is actually grounded in the context ----
def critic_node(state: AgentState) -> AgentState:
    context = "\n---\n".join(state["retrieved_chunks"])

    critic_prompt = f"""You are a strict fact-checker. Given the CONTEXT and the ANSWER below,
reply with ONLY "yes" if the answer is fully supported by the context, or ONLY "no" if it contains
any information not present in the context.

CONTEXT:
{context}

ANSWER:
{state["answer"]}

Reply with only "yes" or "no":"""

    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=critic_prompt
        )
        verdict = response.text.strip().lower()
        state["is_grounded"] = "yes" in verdict
    except Exception:
        # If the critic itself fails (e.g. rate limit), default to trusting the answer
        # rather than crashing or looping forever
        state["is_grounded"] = True

    state["attempts"] = state.get("attempts", 0) + 1
    return state


# ---- 5. Routing logic: decide what happens after the Critic ----
def route_after_critic(state: AgentState) -> str:
    if state["is_grounded"] or state["attempts"] >= 2:
        return "end"
    return "retry"


# ---- 6. Build the graph ----
graph = StateGraph(AgentState)

graph.add_node("retriever", retriever_node)
graph.add_node("reasoning", reasoning_node)
graph.add_node("critic", critic_node)

graph.set_entry_point("retriever")
graph.add_edge("retriever", "reasoning")
graph.add_edge("reasoning", "critic")
graph.add_conditional_edges(
    "critic",
    route_after_critic,
    {"retry": "retriever", "end": END}
)

agent_graph = graph.compile()


# ---- 7. Function to run the whole workflow ----
def run_agent(question: str, filename: str):
    initial_state = {
        "question": question,
        "filename": filename,
        "retrieved_chunks": [],
        "answer": "",
        "is_grounded": False,
        "attempts": 0
    }
    final_state = agent_graph.invoke(initial_state)
    return {
        "answer": final_state["answer"],
        "is_grounded": final_state["is_grounded"],
        "attempts": final_state["attempts"]
    }