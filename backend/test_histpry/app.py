import os
import re
import shutil
import json
import uuid
from datetime import datetime
from typing import Optional, List

from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents import CodeAgent, ToolCallingAgent
from smolagents.memory import MemoryStep
from smolagents.utils import _is_package_available
from smolagents import DuckDuckGoSearchTool

import openai
from smolagents import OpenAIServerModel

base_url = "https://chatapi.akash.network/api/v1"
api_key = "sk-s2Hpm8x0MkhzV743Ecqzqw"
def get_model(model_id: str="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF"):

    client = OpenAIServerModel(
        model_id=model_id,
        api_base=base_url,
        api_key=api_key,
    )
    return client


def pull_messages_from_step(
    step_log: MemoryStep,
):
    """Extract messages from agent steps, yielding dictionaries for JSON streaming."""

    message_list = [] # Changed to return a list instead of yield for class context

    if isinstance(step_log, ActionStep):
        # Output the step number
        step_number = f"Step {step_log.step_number}" if step_log.step_number is not None else ""
        message_list.append({"role": "assistant", "content": f"**{step_number}**"})

        # First yield the thought/reasoning from the LLM
        if hasattr(step_log, "model_output") and step_log.model_output is not None:
            # Clean up the LLM output
            model_output = step_log.model_output.strip()
            # Remove any trailing <end_code> and extra backticks, handling multiple possible formats
            model_output = re.sub(r"```\s*<end_code>", "```", model_output)  # handles ```<end_code>
            model_output = re.sub(r"<end_code>\s*```", "```", model_output)  # handles <end_code>```
            model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)  # handles ```\n<end_code>
            model_output = model_output.strip()
            message_list.append({"role": "assistant", "content": f"{model_output}"})

        # For tool calls, create a parent message
        if hasattr(step_log, "tool_calls") and step_log.tool_calls is not None:
            first_tool_call = step_log.tool_calls[0]
            used_code = first_tool_call.name == "python_interpreter"
            parent_id = f"call_{len(step_log.tool_calls)}"

            # Tool call becomes the parent message with timing info
            # First we will handle arguments based on type
            args = first_tool_call.arguments
            if isinstance(args, dict):
                content = str(args.get("answer", str(args)))
            else:
                content = str(args).strip()

            if used_code:
                # Clean up the content by removing any end code tags
                content = re.sub(r"```.*?\n", "", content)  # Remove existing code blocks
                content = re.sub(r"\s*<end_code>\s*", "", content)  # Remove end_code tags
                content = content.strip()
                if not content.startswith("```python"):
                    content = f"```python\n{content}\n```"

            parent_message_tool = f"Used tool {first_tool_call.name}: {content}"
            message_list.append({"role": "assistant", "content": parent_message_tool})

            # Nesting execution logs under the tool call if they exist
            if hasattr(step_log, "observations") and (
                step_log.observations is not None and step_log.observations.strip()
            ):  # Only yield execution logs if there's actual content
                log_content = step_log.observations.strip()
                if log_content:
                    log_content = re.sub(r"^Execution logs:\s*", "", log_content)
                    message_list.append({"role": "assistant", "content": f"Execution Logs: {log_content}"})

            # Nesting any errors under the tool call
            if hasattr(step_log, "error") and step_log.error is not None:
                message_list.append({"role": "assistant", "content": f"Error: {str(step_log.error)}"})


        # Handle standalone errors but not from tool calls
        elif hasattr(step_log, "error") and step_log.error is not None:
            message_list.append({"role": "assistant", "content": f"Error: {str(step_log.error)}"})

        # Calculate duration and token information
        step_footnote = f"{step_number}"
        if hasattr(step_log, "input_token_count") and hasattr(step_log, "output_token_count"):
            token_str = (
                f" | Input-tokens:{step_log.input_token_count:,} | Output-tokens:{step_log.output_token_count:,}"
            )
            step_footnote += token_str
        if hasattr(step_log, "duration"):
            step_duration = f" | Duration: {round(float(step_log.duration), 2)}" if step_log.duration else None
            step_footnote += step_duration
        step_footnote = f"""<span style="color: #bbbbc2; font-size: 12px;">{step_footnote}</span> """ # Keep span to avoid breaking existing logic, but won't render in terminal
        message_list.append({"role": "assistant", "content": f" {step_footnote}"})
        message_list.append({"role": "assistant", "content": "-----"})
    return message_list


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

    def run_with_history(self, task: str, conversation_history: Optional[List[dict]] = None, reset_agent_memory: bool = False, additional_args: Optional[dict] = None):
        """Runs the agent and returns the conversation history along with the final result."""
        if conversation_history is None:
            conversation_history = []

        total_input_tokens = 0
        total_output_tokens = 0

        for step_log in self.agent.run(task, stream=True, reset=reset_agent_memory, additional_args=additional_args):
            # Track tokens if model provides them
            if getattr(self.agent.model, "last_input_token_count", None) is not None:
                total_input_tokens += self.agent.model.last_input_token_count
                total_output_tokens += self.agent.model.last_output_token_count
                if isinstance(step_log, ActionStep):
                    step_log.input_token_count = self.agent.model.last_input_token_count
                    step_log.output_token_count = self.agent.model.last_output_token_count

            step_messages = pull_messages_from_step(step_log)
            for message_dict in step_messages:
                message_data = {
                    "message_uuid": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "role": message_dict["role"],
                    "content": message_dict["content"]
                }
                conversation_history.append(message_data)


        final_answer = step_log  # Last log is the run's final_answer
        final_answer = handle_agent_output_types(final_answer)

        if isinstance(final_answer, AgentText):
            final_answer_content = f"**Final answer:**\n{final_answer.to_string()}\n"
            final_answer_data = {
                "message_uuid": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": final_answer_content
            }
            conversation_history.append(final_answer_data)
        elif isinstance(final_answer, AgentImage):
            final_answer_content = "Final answer: Image output (path in final_answer)" # Web can't display images directly in this simple example
            final_answer_data = {
                "message_uuid": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": final_answer_content
            }
            conversation_history.append(final_answer_data)
        elif isinstance(final_answer, AgentAudio):
            final_answer_content = "Final answer: Audio output (path in final_answer)" # Web can't play audio directly in this simple example
            final_answer_data = {
                "message_uuid": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": final_answer_content
            }
            conversation_history.append(final_answer_data)
        else:
            final_answer_content = f"**Final answer:** {str(final_answer)}"
            final_answer_data = {
                "message_uuid": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": final_answer_content
            }
            conversation_history.append(final_answer_data)

        return final_answer, conversation_history # Return both final answer and history


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
