#!/usr/bin/env python3
"""
Main entry point for Dynamic SOP Agent
"""

import os
from src.agents.dynamic_sop_agent import DynamicSOPAgent


def main():
    """Main function to run the Dynamic SOP Agent"""
    
    print("=" * 60)
    print("🤖 DYNAMIC SOP AGENT")
    print("Context-Aware Standard Operating Procedure Assistant")
    print("=" * 60)
    print()
    
    # Initialize agent with example SOPs
    sop_dirs = ["examples/sops"]
    
    print("📚 Initializing agent and loading SOPs...")
    agent = DynamicSOPAgent(sop_directories=sop_dirs)
    
    print(f"✅ Agent initialized with {len(agent.mcp_connector.get_all_sops())} SOPs")
    print()
    
    # Show welcome message
    print("Welcome! I can help you find and execute Standard Operating Procedures.")
    print("Type 'help' for available commands, or just describe what you need to do.")
    print("Type 'quit' to exit.")
    print()
    
    # Interactive loop
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("💬 You: ").strip()
            
            if not user_input:
                continue
            
            # Process message
            response = agent.chat(user_input)
            
            # Print response
            print(f"\n🤖 Assistant: {response}\n")
            
            # Check for exit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            
            conversation_count += 1
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            print("Type 'help' for assistance or 'quit' to exit.\n")


if __name__ == "__main__":
    main()
