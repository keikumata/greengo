import logging
import weaviate
import requests
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class USCISPolicyQuerier:
    def __init__(self, client):
        self.client = client
        self.ollama_base_url = "http://localhost:11434"
        self.collection_name = "USCIS_Policy_Manual"
        self.chat_history = []
        
        # Verify collection exists
        try:
            schema = self.client.schema.get()
            logger.info(f"Available collections: {[c['class'] for c in schema['classes']]}")
            if not any(c['class'] == self.collection_name for c in schema['classes']):
                logger.error(f"Collection {self.collection_name} not found!")
        except Exception as e:
            logger.error(f"Error checking schema: {e}")

    def get_relevant_context(self, question: str) -> List[Dict]:
        """Get relevant context using hybrid search (BM25 + semantic search)"""
        try:
            logger.info("Performing hybrid search...")
            response = (
                self.client.query
                .get(self.collection_name, [
                    "content",
                    "title",
                    "url",
                    "section_header",
                    "subsection_header",
                    "volume_number",
                    "part_letter",
                    "chapter_number"
                ])
                .with_hybrid(
                    query=question,
                    properties=["content", "title", "section_header", "subsection_header"],
                    alpha=0.75,  # Increase weight of semantic search
                )
                .with_limit(8)  # Increase number of results
                .with_additional(["distance", "score", "certainty"])  # Add more ranking signals
                .do()
            )
            
            chunks = []
            if (response and 'data' in response and 'Get' in response['data'] 
                and self.collection_name in response['data']['Get']):
                
                for obj in response['data']['Get'][self.collection_name]:
                    chunk = {
                        'content': obj['content'],
                        'title': obj['title'],
                        'url': obj.get('url'),
                        'section_header': obj.get('section_header'),
                        'subsection_header': obj.get('subsection_header'),
                        'volume_number': obj.get('volume_number'),
                        'part_letter': obj.get('part_letter'),
                        'chapter_number': obj.get('chapter_number'),
                        'score': obj.get('_additional', {}).get('score', 0),
                        'certainty': obj.get('_additional', {}).get('certainty', 0)
                    }
                    chunks.append(chunk)
            
            logger.info(f"Found {len(chunks)} chunks from hybrid search")
            return chunks
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            logger.error("Full error:", exc_info=True)
            return []

    def ask(self, question: str) -> str:
        """Main method to get answer for a question"""
        chunks = self.get_relevant_context(question)
        
        if not chunks:
            return "I couldn't find relevant information to answer your question."
        
        # Sort chunks by score and combine context
        context = "\n\n".join([
            f"[Vol {chunk['volume_number']}.{chunk['part_letter']}.{chunk['chapter_number']}] {chunk['title']}\n"
            f"{chunk.get('section_header', '')}: {chunk['content']}"
            for chunk in sorted(chunks, key=lambda x: float(x.get('score', 0)), reverse=True)
            if float(chunk.get('score', 0)) > 0.7  # Convert string to float for comparison
        ])
        
        # Build conversation history
        chat_context = "\n\n".join([
            f"Human: {q}\nAssistant: {a}" 
            for q, a in self.chat_history[-3:]
        ])
        
        prompt = f"""<s>[INST] You are an immigration expert specializing in USCIS policies and procedures. 
When answering questions:
1. Focus on providing structured, hierarchical information
2. Always cite specific volumes, parts, and chapters when available
3. Clearly distinguish between different categories and subcategories
4. If information is missing or incomplete, specify which aspects are not covered in the provided context
5. Use bullet points and clear formatting for better readability
6. If multiple sources provide conflicting information, note the discrepancy

Previous conversation:
{chat_context}

Current context from USCIS Policy Manual:
{context}

Question: {question} [/INST]</s>"""
        
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,  # Add some creativity while keeping responses focused
                    "top_p": 0.9  # Maintain good diversity in responses
                }
            )
            
            if response.status_code == 200:
                answer = response.json()['response']
                self.chat_history.append((question, answer))
                return answer
            else:
                return f"Error generating response: {response.status_code}"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return str(e)

    def clear_history(self):
        """Clear the chat history"""
        self.chat_history = []

def main():
    # Initialize Weaviate client
    client = weaviate.Client(
        url="http://localhost:8080"
    )
    
    querier = USCISPolicyQuerier(client)
    
    print("\nUSCIS Policy Assistant Ready!")
    print("--------------------------------")
    print("Ask any questions about immigration policies.")
    print("Type 'quit' to exit, 'clear' to start a new conversation.")
    
    while True:
        try:
            question = input("\nYour question: ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            elif question.lower() == 'clear':
                querier.clear_history()
                print("\nConversation history cleared.")
                continue
                
            print("\nSearching for answer...")
            answer = querier.ask(question)
            print("\nAnswer:", answer)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
    