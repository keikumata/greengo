# GreenGo - AI-Powered Immigration Assistant

GreenGo is an AI-powered chatbot that helps immigrants navigate the complex U.S. immigration system by providing easy access to USCIS policy information. Built during the Llama Impact Hackathon, this tool aims to make immigration information more accessible and reduce stress for immigrants going through various immigration processes.

## 🎯 Problem Statement

Immigrants face significant challenges when:
- Navigating complex USCIS policies and procedures
- Understanding how to proceed with their applications
- Getting reliable information without access to legal counsel
- Self-filing applications without professional guidance
- Waiting for work authorization and other critical documents

## 💡 Solution

GreenGo leverages AI to:
- Parse and understand USCIS policy manuals
- Provide accurate, source-backed answers to immigration questions
- Help users understand their options and next steps
- Make immigration information more accessible

## 🏗️ Architecture

The application consists of three main components:

1. **Frontend**: Next.js application providing the chat interface
2. **Backend**: Flask API server handling chat interactions
3. **AI Engine**: 
   - Weaviate vector database for storing USCIS policy data
   - Llama 3.2 model for generating responses
   - RAG (Retrieval Augmented Generation) for accurate information retrieval

## 🚀 Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Start Weaviate:
```bash
docker-compose up -d
```

3. Install Python dependencies:
```bash
pip install flask flask-cors weaviate-client requests
```

4. Start Ollama with llama3.2:
```bash
ollama run llama3.2
```

5. Run the Flask server:
```bash
python api.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## 🔮 Future Plans

- Expand data sources to include:
  - Reddit discussions and community experiences
  - Immigration court cases
  - Latest policy updates
- Add form generation capabilities
- Implement action recommendations
- Cloud deployment:
  - Migrate to Weaviate Cloud
  - Host backend on cloud platform
  - Deploy frontend on Vercel

## 👥 Team

Built by immigrants for immigrants during the Llama Impact Hackathon.

## 🎥 Demo

[Watch the full demo video](link-to-video) to see GreenGo in action and learn more about its features and development process.

## ⚠️ Disclaimer

This tool is meant to provide general information and should not be considered as legal advice. For specific legal matters, please consult with an immigration attorney.