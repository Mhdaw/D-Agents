from backend.app.agents.smolagents.base_client import get_model
from smolagents import CodeAgent, ToolCallingAgent
from typing import List, Dict, Any, Union, Optional, Tuple, Type

class Agent:
    def __init__(self,
                 model_id: str="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
                 agent_type: str="codeagent",
                 tools: Optional[List[str]]=None,
                 max_steps: Optional[int]=3,
                 verbosity_level: Optional[int]=1):
        """
        Initialize an Agent instance.
        
        Args:
            model_id (str): The model identifier to use
            agent_type (str): Type of agent ("codeagent" or "toolcallingagent")
            tools (List[str], optional): List of tools to make available to the agent
            max_steps (int, optional): Maximum number of steps for the agent to take
            verbosity_level (int, optional): Level of verbosity in output
        """
        self.model_id = model_id
        self.agent_type = agent_type.lower()
        self.max_steps = max_steps
        self.verbosity_level = verbosity_level
        try:
            self.client = get_model(model_id)
        except Exception as e:
            raise Exception(f"Failed to initialize client: {str(e)}")
        self.tools = tools if tools else []
        self.agent = self.get_agent()

    def get_agent(self):
        """Create and return the appropriate agent type."""
        if self.agent_type == "codeagent":
            return CodeAgent(
                tools=self.tools, 
                model=self.client, 
                max_steps=self.max_steps,
                verbosity_level=(self.verbosity_level > 0)
            )
        elif self.agent_type == "toolcallingagent":
            print("Creating ToolCallingAgent, If you faced some issues with the agent try changing it to `CodeAgent`!")
            return ToolCallingAgent(
                tools=self.tools, 
                model=self.client, 
                max_steps=self.max_steps,
                verbosity_level=(self.verbosity_level > 0)
            )
        else:
            raise ValueError(f"Invalid agent type: {self.agent_type}. Must be 'codeagent' or 'toolcallingagent'")
