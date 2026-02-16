from crewai import Task
from agents import product_manager, senior_architect, security_engineer, qa_engineer

task_define_app = Task(
    description='Analyze the user idea: {topic}. Create a detailed PRD.',
    expected_output='A markdown document containing a feature list and user stories.',
    agent=product_manager,
    output_file='PRD.md'
)

task_tech_stack = Task(
    description='Based on the PRD provided by the PM, define the technology stack, database schema, and API structure.',
    expected_output='A highly technical markdown specification document.',
    agent=senior_architect,
    output_file='TechSpec.md'
)

task_security_review = Task(
    description='Review the PRD and the technical stack provided by the Architect. Identify potential security flaws and suggest encryption standards.',
    expected_output='A markdown document containing a Threat Model.',
    agent=security_engineer,
    output_file='SecurityReview.md'
)

task_qa_planning = Task(
    description='Based on the PRD, Tech Spec, and Security Review, formulate a complete testing strategy.',
    expected_output='A markdown document detailing Unit Tests and Integration Tests.',
    agent=qa_engineer,
    output_file='QAPlan.md'
)