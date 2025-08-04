'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatMessage as ChatMessageType, UserContext } from '@/types'
import { assessEthicsViolation, streamEthicsAssessment } from '@/lib/api'
import { generateId, cn } from '@/lib/utils'
import ChatMessage from './ChatMessage'
import { Send, Loader2, AlertCircle, Bot } from 'lucide-react'

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
  const [streamingStatus, setStreamingStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastUserQuestion, setLastUserQuestion] = useState<string | null>(null)
  
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
    setStreamingStatus(null)
    setError(null)
    setLastUserQuestion(userMessage.content)

    // Create a placeholder message for the assistant response
    const assistantMessageId = generateId()
    const placeholderMessage: ChatMessageType = {
      id: assistantMessageId,
      role: 'assistant', 
      content: '',
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, placeholderMessage])

    try {
      const stream = streamEthicsAssessment({
        question: userMessage.content,
        userContext,
      })

      let finalResponse = ''

      for await (const chunk of stream) {
        if (chunk.status === 'error') {
          setError(chunk.error || 'An error occurred')
          break
        }
        
        if (chunk.message) {
          setStreamingStatus(chunk.message)
        }
        
        if (chunk.status === 'complete' && chunk.response) {
          finalResponse = chunk.response
          setStreamingStatus(null)
          
          // Update the placeholder message with final response
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessageId 
              ? { ...msg, content: finalResponse }
              : msg
          ))
          break
        }
      }

      if (!finalResponse) {
        // Fallback to non-streaming if streaming fails
        const response = await assessEthicsViolation({
          question: userMessage.content,
          userContext,
        })

        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: response.response }
            : msg
        ))

        if (response.error) {
          setError(response.error)
        }
      }
    } catch (err) {
      setError('Failed to get response. Please try again.')
      console.error('Chat error:', err)
      
      // Remove placeholder message on error
      setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId))
    } finally {
      setIsLoading(false)
      setStreamingStatus(null)
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
          <ChatMessage 
            key={message.id} 
            message={message}
            userContext={message.role === 'assistant' ? userContext : undefined}
            originalQuestion={message.role === 'assistant' ? lastUserQuestion || undefined : undefined}
          />
        ))}
        
        {isLoading && (
          <div className="flex items-center gap-3 mb-4">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-primary-600" />
            </div>
            <div className="chat-bubble chat-bubble-assistant">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                <span className="text-sm text-gray-700">
                  {streamingStatus || "🔍 Analyzing your ethics question..."}
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