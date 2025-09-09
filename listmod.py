import google.generativeai as genai

# Configure your API key
genai.configure(api_key="AIzaSyAn6X7NcjUDmA5BITkZI2gczVXAGiYkkss")

# Iterate through all available models
print("List of all available models:")
for m in genai.list_models():
  print(f"Name: {m.name}")
  print(f"Description: {m.description}")
  print("-" * 20)