from backend.app.agents.smolagents.base_agent import Agent
from smolagents import DuckDuckGoSearchTool, VisitWebpageTool
#from backend.app.tools.smolagentsTools.WebTools import initialize_tavily_client, get_tavily_search_results, extract_url_tavily 

from typing import List, Dict, Any, Union, Optional, Tuple, Type
from backend.app.agents.smolagents.base_client import get_model
from smolagents import CodeAgent, ToolCallingAgent
from typing import List, Dict, Any, Union, Optional, Tuple, Type
import os
import re
import shutil
import json
import uuid
from datetime import datetime

from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents import CodeAgent, ToolCallingAgent
from smolagents.memory import MemoryStep
from smolagents.utils import _is_package_available
from smolagents import DuckDuckGoSearchTool

import openai
from smolagents import OpenAIServerModel

class WebAgent:
    def __init__(self, model_id="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
                 agent_type="codeagent",
                 tools: Optional[List[str]]=None,
                 max_steps: Optional[int]=3,
                 verbosity_level: Optional[int]=1):
        
        self.agent_instance = Agent(
            model_id=model_id,
            agent_type=agent_type,
            tools=tools,
            max_steps=max_steps,
            verbosity_level=verbosity_level
        )
        self.current_conversation_id = None
    
    def run_with_history(self, task: str, conversation_history: Optional[List[dict]] = None, 
                        reset_agent_memory: bool = False, additional_args: Optional[dict] = None,
                        conversation_id: Optional[str] = None):
        """Runs the web agent and returns the conversation history along with the final result."""
        
        # Use existing conversation ID or generate new one
        self.current_conversation_id = conversation_id or str(uuid.uuid4())
        
        # Initialize conversation history if None
        if conversation_history is None:
            conversation_history = []
            
        final_answer, history = self.agent_instance.run_with_history(
            task, conversation_history, reset_agent_memory, additional_args
        )
        
        # Save the conversation
        save_conversation_to_json(
            history,
            conversation_id=self.current_conversation_id,
            filename=f"data/conversations/{self.current_conversation_id}.json"
        )
        
        return final_answer, history, self.current_conversation_id

def save_conversation_to_json(conversation_data, conversation_id=None, filename=None):
    """
    Saves conversation data to a JSON file with conversation tracking.
    
    Args:
        conversation_data: List of conversation messages
        conversation_id: Optional UUID for the conversation (generated if None)
        filename: Optional specific filename to save to
    """
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
    
    # Create the conversation object
    conversation_object = {
        "conversation_id": conversation_id,
        "created_at": datetime.now().isoformat(),
        "messages": conversation_data
    }
    
    # Determine the filename and path
    if filename is None:
        # Store each conversation in its own file
        filename = f"data/conversations/{conversation_id}.json"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write the file
    with open(filename, 'w') as f:  # Use 'w' mode for individual files
        json.dump(conversation_object, f, indent=2)
    
    return conversation_id

"""
if __name__ == "__main__":
    tools = [DuckDuckGoSearchTool()] # Initialize tools outside the class for clarity if needed here

    web_agent_instance = WebAgent( # Create an instance of WebAgent
        model_id="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
        agent_type="codeagent",
        tools=tools, # Pass the tools to the WebAgent instance
        max_steps=3,
        verbosity_level=2
    )

    # Run test and print history
    #web_agent_instance.test_web_agent()

    #print("\n\n\n")

    # Example of running a task and saving history:
    task2 = "What is the current time in Tokyo?"
    final_answer2, history2, conv_id = web_agent_instance.run_with_history(task2)
    print(f"\nTask 2 Result: {final_answer2}")
    print("\nTask 2 Conversation History:")
    for message in history2:
        print(f"[{message['timestamp']}] {message['role']}: {message['content']}")
    print(f"\nTask 2 Result: {final_answer2}")
    print(f"Conversation ID: {conv_id}")
    print("\nConversation saved to: data/conversations/{conv_id}.json")
    # In your __main__ block, update the save_conversation_to_json call:
save_conversation_to_json(history2, conv_id, filename="data/web_agent_history.json")
print("\nConversation history saved to web_agent_history.json")
"""
