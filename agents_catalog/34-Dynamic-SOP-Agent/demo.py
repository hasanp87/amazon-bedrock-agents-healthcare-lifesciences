#!/usr/bin/env python3
"""
Demo script showing Dynamic SOP Agent capabilities
"""

import os
import sys
from src.agents.dynamic_sop_agent import DynamicSOPAgent


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_context_analysis():
    """Demonstrate context analysis capabilities"""
    print_section("DEMO 1: Context Analysis")
    
    agent = DynamicSOPAgent(sop_directories=["examples/sops"])
    
    queries = [
        "I need to admit a cardiac patient to the ICU",
        "Emergency code blue in room 301",
        "How do I safely administer IV medications to a patient",
        "Schedule a follow-up appointment for cardiology"
    ]
    
    print("The agent analyzes queries to extract context:\n")
    
    for query in queries:
        print(f"Query: \"{query}\"")
        response = agent.chat(f"analyze context: {query}")
        print(f"{response}\n")
        print("-" * 70 + "\n")


def demo_sop_discovery():
    """Demonstrate SOP discovery based on context"""
    print_section("DEMO 2: Context-Based SOP Discovery")
    
    agent = DynamicSOPAgent(sop_directories=["examples/sops"])
    
    scenarios = [
        {
            "query": "I need to admit a cardiac patient",
            "description": "Clinical admission scenario"
        },
        {
            "query": "Emergency cardiac arrest situation",
            "description": "Emergency response scenario"
        },
        {
            "query": "Administering medications safely",
            "description": "Medication safety scenario"
        }
    ]
    
    for scenario in scenarios:
        print(f"Scenario: {scenario['description']}")
        print(f"Query: \"{scenario['query']}\"\n")
        
        response = agent.chat(f"get sops for: {scenario['query']}")
        print(f"{response}\n")
        print("-" * 70 + "\n")


def demo_sop_execution():
    """Demonstrate step-by-step SOP execution"""
    print_section("DEMO 3: Step-by-Step SOP Execution")
    
    agent = DynamicSOPAgent(sop_directories=["examples/sops"])
    
    print("Starting SOP execution for Cardiac ICU Patient Admission...\n")
    
    # Start SOP
    response = agent.chat("start sop SOP-CARD-001")
    print(f"{response}\n")
    print("-" * 70 + "\n")
    
    # Show progress
    print("Checking progress...\n")
    response = agent.chat("status")
    print(f"{response}\n")
    print("-" * 70 + "\n")
    
    # Complete first step
    print("Completing Step 1...\n")
    response = agent.chat("complete step 1 with notes: Patient identity verified, all checks passed")
    print(f"{response}\n")
    print("-" * 70 + "\n")
    
    # Get step details
    print("Getting details for Step 3...\n")
    response = agent.chat("get step 3 details")
    print(f"{response}\n")


def demo_sop_search():
    """Demonstrate SOP search capabilities"""
    print_section("DEMO 4: SOP Search and Retrieval")
    
    agent = DynamicSOPAgent(sop_directories=["examples/sops"])
    
    print("Listing all available SOPs:\n")
    response = agent.chat("list all sops")
    print(f"{response}\n")
    print("-" * 70 + "\n")
    
    print("Listing SOP categories:\n")
    response = agent.chat("categories")
    print(f"{response}\n")
    print("-" * 70 + "\n")
    
    print("Searching for 'emergency' SOPs:\n")
    response = agent.chat("search for emergency")
    print(f"{response}\n")


def demo_mcp_integration():
    """Demonstrate MCP server integration"""
    print_section("DEMO 5: MCP Server Integration")
    
    agent = DynamicSOPAgent(sop_directories=["examples/sops"])
    
    print("Registering MCP repositories...\n")
    
    # Register Git repository
    agent.register_mcp_repository(
        name="hospital_sops_git",
        source_type="mcp_git",
        source_url="https://github.com/hospital/sop-repository",
        description="Hospital SOPs from Git repository via MCP"
    )
    
    # Register AWS docs
    agent.mcp_connector.connect_aws_docs_mcp(["bedrock", "healthlake"])
    
    # Show registered repositories
    response = agent.chat("repos")
    print(f"{response}\n")
    
    print("\nNote: In production, these MCP connections would fetch SOPs from:")
    print("  • Git repositories via Git Repo Research MCP Server")
    print("  • AWS Documentation via AWS Documentation MCP Server")
    print("  • Custom organizational repositories via custom MCP servers")


def demo_interactive_session():
    """Demonstrate an interactive session"""
    print_section("DEMO 6: Interactive Session Example")
    
    agent = DynamicSOPAgent(sop_directories=["examples/sops"])
    
    conversation = [
        ("Hello! I need help with patient admission procedures", 
         "Initial greeting"),
        ("I'm a nurse in the cardiac unit",
         "Setting context"),
        ("I need to admit a patient to the ICU",
         "Describing task"),
        ("Show me SOP-CARD-001",
         "Requesting specific SOP"),
        ("Start this SOP",
         "Beginning execution"),
        ("Complete step 1",
         "Progressing through steps"),
    ]
    
    print("Simulated interactive conversation:\n")
    
    for user_msg, description in conversation:
        print(f"[{description}]")
        print(f"💬 User: {user_msg}")
        
        # Simplify messages for demo
        if "Show me SOP" in user_msg:
            response = agent.chat("get sop by id SOP-CARD-001")
        elif "Start this SOP" in user_msg:
            response = agent.chat("start sop SOP-CARD-001")
        else:
            response = agent.chat(user_msg)
        
        print(f"🤖 Agent: {response[:300]}...")
        print()


def main():
    """Run all demos"""
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "DYNAMIC SOP AGENT - DEMONSTRATION" + " " * 25 + "║")
    print("║" + " " * 68 + "║")
    print("║" + "  Context-Aware Standard Operating Procedure Assistant" + " " * 13 + "║")
    print("╚" + "=" * 68 + "╝")
    
    demos = [
        ("Context Analysis", demo_context_analysis),
        ("SOP Discovery", demo_sop_discovery),
        ("SOP Execution", demo_sop_execution),
        ("SOP Search", demo_sop_search),
        ("MCP Integration", demo_mcp_integration),
        ("Interactive Session", demo_interactive_session),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run All Demos")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-7): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!\n")
                break
            
            choice_num = int(choice)
            
            if choice_num == len(demos) + 1:
                # Run all demos
                for name, demo_func in demos:
                    try:
                        demo_func()
                        input("\nPress Enter to continue to next demo...")
                    except Exception as e:
                        print(f"\n⚠️  Demo error: {e}")
                        print("Continuing to next demo...\n")
                break
            elif 1 <= choice_num <= len(demos):
                # Run selected demo
                name, demo_func = demos[choice_num - 1]
                try:
                    demo_func()
                except Exception as e:
                    print(f"\n⚠️  Demo error: {e}\n")
            else:
                print("Invalid choice. Please select 0-7.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}\n")


if __name__ == "__main__":
    main()
