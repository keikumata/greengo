'use client'

import { useState, useEffect, useRef } from "react"
import Image from "next/image"
import { Link } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import ReactMarkdown from 'react-markdown'
import { chatApi } from '@/services/api'
import { MarkdownContent } from "./markdown"
import { TipTapEditor } from "./ui/TipTapEditor"

interface Message {
  role: 'user' | 'assistant'
  content: string
}


const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  const content = isUser
    ? message.content
    : message.content.replace(/\\n/g, '\n');

  return (
    <div className={`flex gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="flex flex-col gap-1 max-w-[80%]">
        <span className={`text-sm ${isUser ? 'text-right' : 'text-left'} text-muted-foreground`}>
          {isUser ? 'You' : 'Assistant'}
        </span>
        <div className={`rounded-lg p-4 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
          {isUser ? (
            <p>{content}</p>
          ) : (
            <TipTapEditor
              variant={"body"}
              defaultAlign={"center"}
              cursor={"text"}
              content={content}
              editable={false}
          />
          )}
        </div>
      </div>
    </div>
  );
};

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadChatHistory()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadChatHistory = async () => {
    try {
      const history = await chatApi.getChatHistory()
      setMessages(history.map((pair: [string, string]) => ({
        role: 'user',
        content: pair[0]
      })).flatMap((userMessage, index) => [
        userMessage,
        {
          role: 'assistant',
          content: history[index][1]
        }
      ]))
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await chatApi.askQuestion(userMessage)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.answer 
      }])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm sorry, I encountered an error processing your request. Please try again later."
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickQuestion = (question: string) => {
    setInput(question)
  }

  return (
    <div className="flex h-screen bg-background font-['Inter']">
      {/* Sidebar */}
      <div className="w-[300px] border-r flex flex-col">
        <div className="p-4 border-b">
          <div className="flex items-center gap-2">
            <Image
              src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Greengo%20logo-UsfyJSD9ZTUYnGjyWYxGIl5oHQABEG.png"
              alt="Greengo Logo"
              width={32}
              height={32}
              className="rounded-lg"
            />
            <span className="text-xl font-semibold">Greengo</span>
          </div>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="p-4 space-y-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-primary"
              >
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              </svg>
              <span>Chat History</span>
            </div>
          </div>
        </ScrollArea>

        <div className="p-4 border-t">
          <Button 
            variant="outline" 
            className="w-full justify-start gap-2"
            onClick={() => chatApi.clearHistory().then(loadChatHistory)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-primary"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" x2="12" y1="3" y2="15" />
            </svg>
            Clear Chat
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="space-y-4">
              <h1 className="text-3xl font-bold">
                Need help with your Green Card process?
              </h1>
              <div className="flex flex-wrap gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-[#F8FCF8] hover:bg-[#E9F1E5] font-normal font-['Inter']"
                  onClick={() => handleQuickQuestion("What are the different ways you get an employment-based Green Card?")}
                >
                  Tell me about the employment-based Green Card
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="bg-[#F8FCF8] hover:bg-[#E9F1E5] font-normal font-['Inter']"
                  onClick={() => handleQuickQuestion("Walk me through the process of applying for an EB3 Green Card, including I-140 and I-485.")}
                >
                  Walk me through the EB3 Green Card process
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, i) => (
                <MessageBubble key={i} message={message} />
              ))}
              {isLoading && (
                <MessageBubble 
                  message={{
                    role: 'assistant',
                    content: 'Thinking...'
                  }}
                />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                className="pr-12"
                placeholder="Message Greengo"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
              />
              <button 
                type="submit"
                disabled={isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 disabled:opacity-50"
              >
                <svg width="32" height="32" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="40" height="40" rx="20" fill={isLoading ? "#9CA3AF" : "#5D7246"}/>
                  <path d="M25.9853 19.2629L25.9853 19.2628L21.1581 14.4356L21.0781 14.3556V14.4688V28.25C21.0781 28.536 20.9645 28.8102 20.7623 29.0124C20.5601 29.2146 20.2859 29.3282 20 29.3282C19.714 29.3282 19.4398 29.2146 19.2376 29.0124C19.0354 28.8102 18.9218 28.536 18.9218 28.25V14.4688V14.3557L18.8418 14.4356L14.0128 19.2628L14.0128 19.2628C13.8102 19.4654 13.5355 19.5792 13.249 19.5792C12.9626 19.5792 12.6878 19.4654 12.4853 19.2628C12.2827 19.0603 12.1689 18.7856 12.1689 18.4991C12.1689 18.2126 12.2827 17.9379 12.4853 17.7354L19.2353 10.9854L19.2353 10.9853C19.3355 10.8848 19.4545 10.8051 19.5856 10.7506C19.7166 10.6962 19.8571 10.6682 19.999 10.6682C20.1409 10.6682 20.2814 10.6962 20.4125 10.7506C20.5435 10.8051 20.6625 10.8848 20.7627 10.9853L20.7628 10.9854L27.5128 17.7354L27.5128 17.7354C27.6133 17.8356 27.6931 17.9546 27.7475 18.0857C27.8019 18.2167 27.8299 18.3572 27.8299 18.4991C27.8299 18.641 27.8019 18.7815 27.7475 18.9125C27.6931 19.0436 27.6133 19.1626 27.5128 19.2628L27.5127 19.2629C27.4125 19.3634 27.2935 19.4431 27.1625 19.4976C27.0314 19.552 26.8909 19.58 26.749 19.58C26.6071 19.58 26.4666 19.552 26.3356 19.4976C26.2045 19.4431 26.0855 19.3634 25.9853 19.2629Z" fill="white" stroke="white" strokeWidth="0.09375"/>
                </svg>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}