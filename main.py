import autogen
from autogen import ConversableAgent
from dotenv import load_dotenv
import os

load_dotenv()

config_list = {
    "model": "gpt-4.1-nano",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "cache_seed": 45
}

user_proxy = autogen.UserProxyAgent(
    name="admin",
    system_message="Human admin that interacts with the planner to discuss the plan. Plan execution needs to be approved by this admin",
    code_execution_config={
        "work_dir": "program",
        "use_docker": False,
    },
    human_input_mode="ALWAYS"
)

planner_agent = autogen.AssistantAgent(
    name="planner_agent",
    llm_config=config_list,
    system_message="""Your team is making a snake game using python and tkinter. In the team, your role is a planner responsible
    for project planning of the snake game. You as a planner agent will provide specific programming instructions to the 'coder_agent',
    and you need to make sure the game has all the basic features such as the game engine(snake physics and how it moves), keeping game score record and
    in-memory data, key stroke control and all necessary things for it to be one complete snake game. You need to tell all these 
    plans to the coder agent to perform its coding job 
    
    Things to make sure:
    1. the snake starts with a 3-block length
    2. the score keeps displayed on the left top area 
    """,
    human_input_mode="NEVER",
)

coder_agent = autogen.AssistantAgent(
    name="coder_agent",
    llm_config=config_list,
    system_message="""Your team is making a snake game using python and tkinter. In the team, your role is a coder responsible
    for writing the code of the snake game. The planner agent will provide specific programming instructions and you should
    follow it to implement the program.
    """,
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "program",
        "use_docker": False,
    }
)

tester_agent = autogen.AssistantAgent(
    name="tester_agent",
    llm_config=config_list,
    system_message="""Your team is making a snake game using python and tkinter. In the team, your role is a tester responsible
    for testing the program made by 'coder_agent'. You need to tell 'coder_agent' if you face an error and the snake game doesn't run
    as expected. You need to be very meticulous and have a hawk eye finding the existing or possible error. Also, making sure the snake game 
    was built as planned (by planner_agent) is one of your important jobs.

    - Confirm that the game runs as expected
    - Then, explicitly notify the `publisher_agent` that the game is ready to publish.
    - Say: 'The code works and matches the plan. Please proceed to publishing.'
    """,
    human_input_mode="NEVER",
)

publisher_agent = autogen.AssistantAgent(
    name="publisher_agent",
    llm_config=config_list,
    system_message="""You are the publisher of the project.
Do not run the final game code.Instead, save the final working code into a file named `snake_game.py` using the following method:
```python 
with open("snake_game.py", "w") as f:
     f.write(\"\"\"<PASTE FULL CODE HERE>\"\"\")
```

- Then say: 'Publishing complete' to finish the project.

Do **not** start unless tester_agent clearly says everything works as planned.
""",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "program",
        "use_docker": False,
    },
    is_termination_msg=lambda msg: "publishing complete" in msg["content"].lower()
)

group_chat = autogen.GroupChat(
    agents=[user_proxy, planner_agent, coder_agent, tester_agent, publisher_agent],
    messages=[],
    max_round=15
)

manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=config_list)

user_proxy.initiate_chat(
    recipient=manager,
    message="""
    I want the team to develop snake game in tkinter.
    """
)
