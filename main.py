import os
from crewai import Crew, Process
from agents import product_manager, senior_architect, security_engineer, qa_engineer
from tasks import task_define_app, task_tech_stack, task_security_review, task_qa_planning

# Helper function to read files safely
def read_file(filepath):
    if not os.path.exists(filepath):
        print(f"\n❌ ERROR: Required checkpoint file '{filepath}' not found!")
        print("You must run the previous steps to generate this file before resuming here.")
        exit()
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

# 1. The CLI Menu
print("\n==============================================")
print("🚀 VIRTUAL AGENCY CONTROL PANEL")
print("==============================================")
print("Where would you like to start the pipeline?")
print("1. PM phase        (Start Fresh - Runs all 4 Agents)")
print("2. Architect phase (Requires PRD.md)")
print("3. Security phase  (Requires PRD.md & TechSpec.md)")
print("4. QA phase        (Requires PRD.md, TechSpec.md & SecurityReview.md)")

choice = input("\nEnter choice (1-4): ").strip()

# Base configuration variables
agents_list = []
tasks_list = []
inputs_dict = {}

# 2. Dynamic Routing Logic
if choice == '1':
    idea = input("\nWhat app would you like us to build? \n> ")
    inputs_dict = {'topic': idea}
    agents_list = [product_manager, senior_architect, security_engineer, qa_engineer]
    tasks_list = [task_define_app, task_tech_stack, task_security_review, task_qa_planning]

elif choice == '2':
    print("\nLoading PRD.md checkpoint...")
    prd_text = read_file('PRD.md')
    
    # We inject the file content directly into the Architect's task description
    task_tech_stack.description += f"\n\n--- INJECTED CONTEXT: PRD ---\n{prd_text}"
    
    agents_list = [senior_architect, security_engineer, qa_engineer]
    tasks_list = [task_tech_stack, task_security_review, task_qa_planning]

elif choice == '3':
    print("\nLoading PRD.md and TechSpec.md checkpoints...")
    prd_text = read_file('PRD.md')
    tech_text = read_file('TechSpec.md')
    
    # We inject both files into the Security Engineer's task description
    task_security_review.description += f"\n\n--- INJECTED CONTEXT ---\nPRD:\n{prd_text}\n\nTECH SPEC:\n{tech_text}"
    
    agents_list = [security_engineer, qa_engineer]
    tasks_list = [task_security_review, task_qa_planning]

elif choice == '4':
    print("\nLoading all checkpoints for QA...")
    prd_text = read_file('PRD.md')
    tech_text = read_file('TechSpec.md')
    sec_text = read_file('SecurityReview.md')
    
    task_qa_planning.description += f"\n\n--- INJECTED CONTEXT ---\nPRD:\n{prd_text}\n\nTECH SPEC:\n{tech_text}\n\nSECURITY:\n{sec_text}"
    
    agents_list = [qa_engineer]
    tasks_list = [task_qa_planning]

else:
    print("Invalid choice. Exiting.")
    exit()

# 3. Execution
print("\n⚙️ Assembling Crew and starting execution...\n")
dynamic_crew = Crew(
    agents=agents_list,
    tasks=tasks_list,
    process=Process.sequential,
    max_rpm=2,
    verbose=True
)

dynamic_crew.kickoff(inputs=inputs_dict)

print("\n==============================================")
print("✅ PIPELINE EXECUTION COMPLETE!")
print("==============================================")