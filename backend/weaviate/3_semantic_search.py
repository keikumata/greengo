import weaviate
import json

client = weaviate.connect_to_local()

uscis_policy_manual = client.collections.get("USCIS_Policy_Manual")

response = uscis_policy_manual.query.near_text(
    query="What are the different ways you can get a green card?",
    limit=2
)

for obj in response.objects:
    print(json.dumps(obj.properties, indent=2))

client.close()  # Free up resources