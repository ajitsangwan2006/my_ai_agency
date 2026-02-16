import os
from crewai import Agent, LLM

# 1. Setup the Brain (The Native CrewAI Way)
# The "gemini/" prefix tells the underlying engine to completely ignore OpenAI.
gemini_llm = LLM(
    model="gemini/gemini-3-flash-preview", 
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.6,
    max_retries=5
)

# 2. Define the Product Manager Agent
product_manager = Agent(
    role='Senior Product Manager',
    goal='Uncover user needs and define clear, actionable product requirements (PRD).',
    backstory="""You are an expert Product Manager at a top-tier tech company. 
    You are famous for asking "Why?" until you understand the root user problem. 
    You excel at breaking down vague ideas into comprehensive user stories 
    and acceptance criteria.""",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 3. Define the Solutions Architect Agent
senior_architect = Agent(
    role='Chief Technology Officer',
    goal='Design a scalable, secure, and cost-effective technology stack.',
    backstory="""You are a pragmatic CTO with decades of experience. 
    You prefer proven technologies over hype. You always think about 
    database schema, API security, and deployment logistics before writing code.""",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 4. Define the Security Engineer
security_engineer = Agent(
    role='Lead Security Engineer',
    goal='Identify vulnerabilities and enforce strict security protocols on the proposed architecture.',
    backstory="""You are a paranoid cybersecurity expert who assumes every app will be attacked. 
    You excel at threat modeling and auditing technical specifications to ensure data encryption, 
    secure authentication, and compliance with modern security standards.""",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm # They use the same Gemini 3 brain!
)

# 5. Define the QA Engineer
qa_engineer = Agent(
    role='Director of Quality Assurance',
    goal='Develop a comprehensive testing strategy based on the product requirements and technical specs.',
    backstory="""You are a meticulous QA leader who hates bugs. You specialize in designing 
    unit tests, integration tests, and user acceptance criteria. You always anticipate edge cases 
    that developers and architects often miss.""",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

print("Agents initialized natively with Gemini successfully.")