from flask import Blueprint, request, jsonify

from backend.app.agents.smolagents import WebAgent
from smolagents import DuckDuckGoSearchTool

web_routes_bp = Blueprint("web_routes", __name__, url_prefix="/web")

try:
    web_agent_instance = WebAgent(  
        model_id="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
        agent_type="codeagent",
        tools=[DuckDuckGoSearchTool()],
        max_steps=3,
        verbosity_level=2,
    )
except Exception as e:
    # Handle potential errors during agent initialization.
    print(f"Error initializing web agent: {e}")
    web_agent_instance = None  # Set to None if initialization fails


@web_routes_bp.route("/search", methods=["GET"])  # Keeping GET for search queries
def search_web():
    if web_agent_instance is None:
        return jsonify({"error": "Web agent initialization failed."}), 500  # Return error if agent wasn't initialized

    query = request.args.get("query")  # Get query from URL parameters (e.g., /web/search?query=...)

    if not query:
        return jsonify({"error": "Missing 'query' parameter in the request."}), 400  # Return error if query is missing

    try:
        final_answer, history, conversation_id = web_agent_instance.run_with_history(query)  # Use run_with_history
        return jsonify(
            {"result": str(final_answer), "conversation_id": conversation_id}
        )  # Return final answer and conversation ID
    except Exception as e:
        print(f"Error during web agent execution: {e}")
        return jsonify({"error": "Error during web agent execution."}), 500  # Return a generic error to the client
