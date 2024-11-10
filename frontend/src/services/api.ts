const API_BASE_URL = 'http://localhost:5555/api';

export const chatApi = {
  async getChatHistory() {
    const response = await fetch(`${API_BASE_URL}/chat/history`);
    const data = await response.json();
    return data.history;
  },

  async askQuestion(question: string) {
    const response = await fetch(`${API_BASE_URL}/chat/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    return await response.json();
  },

  async clearHistory() {
    const response = await fetch(`${API_BASE_URL}/chat/clear`, {
      method: 'POST',
    });
    return await response.json();
  },
};