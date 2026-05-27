from app.services.database import save_memory, search_memory

# 1. Save some facts
save_memory("The user's name is Charan.")
save_memory("Charan is building a full-stack resume-ai application.")
save_memory("Charan wants to improve spoken English for an ITC Infotech interview.")

# 2. Search for something conceptually similar
print("\n🔍 Searching for: 'What is the user's project?'")
results = search_memory("What is the user's project?")

print("\n✅ Results found:")
for fact in results:
    print(f"- {fact}")