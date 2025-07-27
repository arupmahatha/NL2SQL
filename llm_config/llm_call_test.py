from llm_call import generate_text, reset_conversation  # Import the functions

# Start with a fresh conversation
reset_conversation()

# First prompt
prompt1 = "Tell me a joke."
response1 = generate_text(prompt1,"sk-5111bf293f17458ca635a8675cbc42ea")
print("Generated Response 1:")
print(response1)

# Follow-up prompt without needing to include previous context (handled by conversation history)
prompt2 = "What was our last conversation about?"
response2 = generate_text(prompt2,"sk-5111bf293f17458ca635a8675cbc42ea")
print("\nGenerated Response 2:")
print(response2)