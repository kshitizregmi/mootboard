from google import genai
from google.genai import types
from google.adk.agents import Agent
from PIL import Image
import os
from dotenv import load_dotenv
# Conceptual Example: Defining Hierarchy
from google.adk.agents import LlmAgent, BaseAgent

from moodboard_agent import get_mootboard_agent
from text_to_sketch_agent import get_text_to_sketch_agent
from sketch_to_digital_agent import get_sketch_to_digital_agent

# Define individual agents
sketch_to_digital_agent = get_sketch_to_digital_agent()
text_to_sketch_agent = get_text_to_sketch_agent()
# face_swap_agent = LlmAgent(name="FaceSwapper", model="gemini-2.0-flash")
mootboard_agent = get_mootboard_agent()

# Create parent agent and assign children via sub_agents
root_agent = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash-exp",
    description = (
        "You are the coordinator agent responsible for managing and orchestrating the workflow "
        "between specialized sub-agents: converting text prompts into sketches, transforming sketches "
        "into digital illustrations, and generating final fashion moodboards. You ensure tasks are "
        "delegated efficiently and results flow seamlessly between agents."
    ),
    sub_agents=[ 
        sketch_to_digital_agent,
        text_to_sketch_agent,
        mootboard_agent,
    ],
)

# Framework automatically sets:
# assert greeter.parent_agent == coordinator
# assert task_doer.parent_agent == coordinator