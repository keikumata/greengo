export interface ChatMessage {
    question: string;
    answer: string;
  }
  
  export interface ChatResponse {
    question: string;
    answer: string;
    history: [string, string][];
  }