import weaviate
from weaviate.classes.config import Configure

client = weaviate.connect_to_local()

# Check if collection exists
try:
    client.collections.delete_all()
    print("Deleted all collections")

    # Create collection only if it doesn't exist
    uscis_policy_manual = client.collections.create(
        name="USCIS_Policy_Manual",
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://localhost:11434",
            model="nomic-embed-text",
        ),
        generative_config=Configure.Generative.ollama(
            api_endpoint="http://localhost:11434",
            model="llama3.2",
        )
    )
    print("Created new 'USCIS_Policy_Manual' collection")
except Exception as e:
    print(f"Error during query: {str(e)}")
finally:
    client.close()
