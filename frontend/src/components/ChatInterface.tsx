'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatMessage as ChatMessageType, UserContext } from '@/types'
import { assessEthicsViolation } from '@/lib/api'
import { generateId, cn } from '@/lib/utils'
import ChatMessage from './ChatMessage'
import { Send, Loader2, AlertCircle } from 'lucide-react'

interface ChatInterfaceProps {
  userContext: UserContext
  className?: string
}

export default function ChatInterface({ userContext, className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([
    {
      id: generateId(),
      role: 'assistant',
      content: `Hello! I'm IntegriBot, your federal ethics compliance assistant. I'm here to help you understand potential ethics violations, penalties, and reporting requirements.

**I can help with:**
- Gift acceptance and restrictions
- Financial conflicts of interest
- Outside employment and post-employment rules
- Procurement ethics violations
- Political activities restrictions

Please describe your ethics question or scenario, and I'll provide comprehensive guidance based on federal ethics laws.`,
      timestamp: new Date(),
    },
  ])
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessageType = {
      id: generateId(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await assessEthicsViolation({
        question: userMessage.content,
        userContext,
      })

      const assistantMessage: ChatMessageType = {
        id: generateId(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])

      if (response.error) {
        setError(response.error)
      }
    } catch (err) {
      setError('Failed to get response. Please try again.')
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex items-center gap-3 mb-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <Loader2 className="w-4 h-4 text-primary-600 animate-spin" />
            </div>
            <div className="chat-bubble chat-bubble-assistant">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm text-gray-600">
                  Analyzing your ethics question...
                </span>
              </div>
            </div>
          </div>
        )}
        
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your ethics question or scenario..."
              className="input-field resize-none"
              rows={3}
              disabled={isLoading}
            />
          </div>
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary flex items-center gap-2 self-end disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
        
        <p className="text-xs text-gray-500 mt-2">
          This guidance is for informational purposes only and does not constitute legal advice.
        </p>
      </div>
    </div>
  )
}