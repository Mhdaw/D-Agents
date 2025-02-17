from backend.app.agents.smolagents.base_agent import Agent
from smolagents import DuckDuckGoSearchTool, VisitWebpageTool
#from backend.app.tools.smolagentsTools.WebTools import initialize_tavily_client, get_tavily_search_results, extract_url_tavily 

from typing import List, Dict, Any, Union, Optional, Tuple, Type

class WebAgent: 
    def __init__(self,
                 model_id: str="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
                 agent_type: str="codeagent",
                 tools: Optional[List[str]]=None,
                 max_steps: Optional[int]=3,
                 verbosity_level: Optional[int]=1):
                 
        # Initialize the Agent class from base_agent.py, passing the tools argument
        self.agent = Agent(
            model_id=model_id,
            agent_type=agent_type,
            tools=tools, #
            max_steps=max_steps,
            verbosity_level=verbosity_level
        )

    def test_web_agent(self):
        task = "Search for the best books about parallel computing"
        result = self.run(task)
        print(f"Test Result: {result}") 


#if __name__ == "__main__":
 #   tools = [DuckDuckGoSearchTool()] # Initialize tools outside the class for clarity if needed here
#
 #   web_agent_instance = WebAgent( # Create an instance of WebAgent
  #      model_id="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
   #     agent_type="codeagent",
    #    tools=tools, # Pass the tools to the WebAgent instance
     #   max_steps=3,
      #  verbosity_level=2
    #)

    #web_agent_instance.test_web_agent() # Call test_web_agent on the instance
    # Alternatively, you could run a task directly:
    # task = "What is the weather in London?"
    # result = web_agent_instance.run(task)
    # print(f"Task Result: {result}")
