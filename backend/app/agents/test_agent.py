from base_agent import Agent

test_agent = Agent(
    model_id="fireworks::accounts/fireworks/models/llama-v3p1-405b-instruct-long",
    agent_type="codeagent",
    tools=[],
    max_steps=3,
    verbosity_level=2
)
task = "Hello"
result = test_agent.run_agent(task)
print(result)