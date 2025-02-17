from backend.app.agents.smolagents.base_agent import Agent

test_agent = Agent(
    model_id="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF",
    agent_type="codeagent",
    tools=[],
    max_steps=3,
    verbosity_level=2
)
task = "Hello"
result = test_agent.run_agent(task)
print(result)
# This works.