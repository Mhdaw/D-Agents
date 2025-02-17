from flask import Blueprint, request, jsonify

from backend.app.agents.smolagents import WebAgent  
from smolagents import DuckDuckGoSearchTool 

web_routes_bp = Blueprint("web_routes", __name__, url_prefix="/web") 

# Instantiate the web agent *outside* the route function.
# This means the agent is created only once when the blueprint is loaded, which is more efficient.
# It reuses the same agent instance for all requests to this blueprint.
try:
    web_agent_instance = WebAgent( # Renamed instance variable for clarity
        model_id="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
        agent_type="codeagent",
        tools=[DuckDuckGoSearchTool()],
        max_steps=3,
        verbosity_level=2
    )
except Exception as e:
    # Handle potential errors during agent initialization.
    # You might want to log this error more robustly in a production setting.
    print(f"Error initializing web agent: {e}")
    web_agent_instance = None  # Set to None if initialization fails

@web_routes_bp.route("/search", methods=["GET"]) # Keeping POST as in your original example. GET could also be suitable for search.
def search_web():
    if web_agent_instance is None:
        return jsonify({"error": "Web agent initialization failed."}), 500 # Return error if agent wasn't initialized

    query = request.args.get("query") # Get query from URL parameters (e.g., /web/search?query=...)

    if not query:
        return jsonify({"error": "Missing 'query' parameter in the request."}), 400 # Return error if query is missing

    try:
        result = web_agent_instance.run_web_agent(query) # Use the agent instance to run the search
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error during web agent execution: {e}")
        return jsonify({"error": "Error during web agent execution."}), 500 # Return a generic error to the client