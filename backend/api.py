import logging

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import weaviate
from typing import List, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize Weaviate client
client = weaviate.Client(
    url="http://localhost:8080"
)

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

    # Copy the get_relevant_context method from the original file
    # Lines 29-80 from the original file
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
                    alpha=0.75,
                )
                .with_limit(8)
                .with_additional(["distance", "score", "certainty"])
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

    # Copy the ask method from the original file
    # Lines 82-140 from the original file
    def ask(self, question: str) -> str:
        """Main method to get answer for a question"""
        chunks = self.get_relevant_context(question)
        
        if not chunks:
            return "<h2>No Information Found</h2><p>I couldn't find relevant information to answer your question.</p>"
        
        context = "\n\n".join([
            f"[Vol {chunk['volume_number']}.{chunk['part_letter']}.{chunk['chapter_number']}] {chunk['title']}\n"
            f"{chunk.get('section_header', '')}: {chunk['content']}"
            for chunk in sorted(chunks, key=lambda x: float(x.get('score', 0)), reverse=True)
            if float(chunk.get('score', 0)) > 0.7
        ])
        
        chat_context = "\n\n".join([
            f"Human: {q}\nAssistant: {a}" 
            for q, a in self.chat_history[-3:]
        ])
        
        prompt = f"""<s>[INST] You are an immigration expert specializing in USCIS policies and procedures. 
When answering questions:
1. Format your response in HTML
2. Use <h2> tags for main sections
3. ALWAYS use <ul> and <li> tags for lists - never use asterisks (*) or hyphens (-)
4. Use <strong> tags for important terms
5. For citations:
   - Use exact format: <a href="https://www.uscis.gov/policy-manual/volume-[X]-part-[Y]-chapter-[Z]#:~:text=[encoded_text]" target="_blank">Volume [X], Part [Y], Chapter [Z]</a>
   - Example: <a href="https://www.uscis.gov/policy-manual/volume-6-part-e-chapter-8#:~:text=The%20employer%20must%20demonstrate" target="_blank">Volume 6, Part E, Chapter 8</a>
   - Only include citations if they link directly to USCIS Policy Manual
   - Use lowercase letters in URLs
   - Use hyphens (-) between all parts of the URL path
   - Do not use spaces or URL encoding (%20) in the URL path
   - When referencing specific text, add #:~:text=[encoded_text] to highlight that text
6. Always cite specific volumes, parts, and chapters when available
7. Use <div> tags to separate different sections
8. If information is missing or incomplete, specify which aspects are not covered
9. If multiple sources provide conflicting information, note the discrepancy
10. Do not use markdown formatting - use proper HTML tags instead

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
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            )
            
            if response.status_code == 200:
                answer = response.json()['response']
                self.chat_history.append((question, answer))
                return answer
            else:
                return "<h2>Error</h2><p>Unable to generate response due to server error.</p>"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"<h2>Error</h2><p>{str(e)}</p>"

    def clear_history(self):
        """Clear the chat history"""
        self.chat_history = []

    def get_chat_history(self):
        """Get the current chat history"""
        return self.chat_history

# Initialize the querier
querier = USCISPolicyQuerier(client)

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get the current chat history"""
    return jsonify({
        'history': querier.get_chat_history()
    })

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """Clear the chat history"""
    querier.clear_history()
    return jsonify({
        'message': 'Chat history cleared successfully'
    })

@app.route('/api/chat/ask', methods=['POST'])
def ask_question():
    """Ask a question and get a response"""
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({
            'error': 'Question is required'
        }), 400
    
    question = data['question']
    answer = querier.ask(question)
    
    return jsonify({
        'question': question,
        'answer': answer,
        'history': querier.get_chat_history()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
