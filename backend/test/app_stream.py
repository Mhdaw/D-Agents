import os
import re
import shutil
import json
import uuid
from datetime import datetime
from typing import Optional

from flask import Flask, render_template, request, jsonify, Response
from smolagents.agent_types import AgentAudio, AgentImage, AgentText, handle_agent_output_types
from smolagents.agents import ActionStep, MultiStepAgent
from smolagents.memory import MemoryStep
from smolagents.utils import _is_package_available
from smolagents import DuckDuckGoSearchTool

import os
import json
import openai
import requests
from smolagents import OpenAIServerModel

base_url = "https://chatapi.akash.network/api/v1"
api_key = "sk-s2Hpm8x0MkhzV743Ecqzqw"
def get_client():

    client = openai.OpenAI(base_url=base_url, api_key=api_key)
    return client

def get_model(model_id: str="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF"):

    client = OpenAIServerModel(
        model_id=model_id,
        api_base=base_url,
        api_key=api_key,
    )
    return client

app = Flask(__name__)

# Replace this with your actual agent initialization
# For demonstration, let's assume you have a function to create your agent
def create_agent():
    # Placeholder: Replace with your agent creation logic
    from smolagents.agents import CodeAgent

    agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=get_model(), max_steps=4, verbosity_level=4)
    return agent

agent_instance = create_agent() # Initialize agent globally for simplicity in this example

def pull_messages_from_step(
    step_log: MemoryStep,
):
    """Extract messages from agent steps, yielding dictionaries for JSON streaming."""

    if isinstance(step_log, ActionStep):
        # Output the step number
        step_number = f"Step {step_log.step_number}" if step_log.step_number is not None else ""
        yield {"role": "assistant", "content": f"**{step_number}**"}

        # First yield the thought/reasoning from the LLM
        if hasattr(step_log, "model_output") and step_log.model_output is not None:
            # Clean up the LLM output
            model_output = step_log.model_output.strip()
            # Remove any trailing <end_code> and extra backticks, handling multiple possible formats
            model_output = re.sub(r"```\s*<end_code>", "```", model_output)  # handles ```<end_code>
            model_output = re.sub(r"<end_code>\s*```", "```", model_output)  # handles <end_code>```
            model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)  # handles ```\n<end_code>
            model_output = model_output.strip()
            yield {"role": "assistant", "content": f"{model_output}"}

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
            yield {"role": "assistant", "content": parent_message_tool}

            # Nesting execution logs under the tool call if they exist
            if hasattr(step_log, "observations") and (
                step_log.observations is not None and step_log.observations.strip()
            ):  # Only yield execution logs if there's actual content
                log_content = step_log.observations.strip()
                if log_content:
                    log_content = re.sub(r"^Execution logs:\s*", "", log_content)
                    yield {"role": "assistant", "content": f"Execution Logs: {log_content}"}

            # Nesting any errors under the tool call
            if hasattr(step_log, "error") and step_log.error is not None:
                yield {"role": "assistant", "content": f"Error: {str(step_log.error)}"}


        # Handle standalone errors but not from tool calls
        elif hasattr(step_log, "error") and step_log.error is not None:
            yield {"role": "assistant", "content": f"Error: {str(step_log.error)}"}

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
        yield {"role": "assistant", "content": f" {step_footnote}"}
        yield {"role": "assistant", "content": "-----"}


def stream_agent_response(
    agent,
    task: str,
    conversation_history: list,
    reset_agent_memory: bool = False,
    additional_args: Optional[dict] = None,
):
    """Streams agent responses as JSON objects."""
    yield '[' # Start of JSON array for SSE

    first_message = True # Flag to handle comma separation in JSON array

    total_input_tokens = 0
    total_output_tokens = 0

    for step_log in agent.run(task, stream=True, reset=reset_agent_memory, additional_args=additional_args):
        # Track tokens if model provides them
        if getattr(agent.model, "last_input_token_count", None) is not None:
            total_input_tokens += agent.model.last_input_token_count
            total_output_tokens += agent.model.last_output_token_count
            if isinstance(step_log, ActionStep):
                step_log.input_token_count = agent.model.last_input_token_count
                step_log.output_token_count = agent.model.last_output_token_count

        for message_dict in pull_messages_from_step(
            step_log,
        ):
            message_content = message_dict["content"]
            message_data = {
                "message_uuid": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "role": message_dict["role"],
                "content": message_content
            }
            conversation_history.append(message_data)
            json_message = json.dumps(message_data)
            if not first_message:
                yield ',' # Add comma between messages in JSON array
            else:
                first_message = False
            yield json_message


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
        if not first_message:
            yield ','
        else:
            first_message = False
        yield json.dumps(final_answer_data)
    elif isinstance(final_answer, AgentImage):
        final_answer_content = "Final answer: Image output (path in final_answer)" # Web can't display images directly in this simple example
        final_answer_data = {
            "message_uuid": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": final_answer_content
        }
        conversation_history.append(final_answer_data)
        if not first_message:
            yield ','
        else:
            first_message = False
        yield json.dumps(final_answer_data)
    elif isinstance(final_answer, AgentAudio):
        final_answer_content = "Final answer: Audio output (path in final_answer)" # Web can't play audio directly in this simple example
        final_answer_data = {
            "message_uuid": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": final_answer_content
        }
        conversation_history.append(final_answer_data)
        if not first_message:
            yield ','
        else:
            first_message = False
        yield json.dumps(final_answer_data)
    else:
        final_answer_content = f"**Final answer:** {str(final_answer)}"
        final_answer_data = {
            "message_uuid": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": final_answer_content
        }
        conversation_history.append(final_answer_data)
        if not first_message:
            yield ','
        else:
            first_message = False
        yield json.dumps(final_answer_data)

    yield ']' # End of JSON array for SSE


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    conversation_history = [] # Initialize history for this request. In real app, use sessions/DB

    def generate():
        yield from stream_agent_response(agent_instance, user_message, conversation_history)
        # After streaming is complete, you might want to save the conversation history here
        # save_conversation_to_json({"messages": conversation_history}, filename="flask_conversations.json") # Example save

    return Response(generate(), mimetype='application/json') # Expecting JSON array


def save_conversation_to_json(conversation_data, filename="flask_conversations.json"):
    """Saves conversation data to a JSON file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as f:
        json.dump(conversation_data, f)
        f.write('\n')


if __name__ == '__main__':
    app.run(debug=True) # Set debug=False for production
