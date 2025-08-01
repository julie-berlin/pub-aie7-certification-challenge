'use client'

import { ChatMessage as ChatMessageType } from '@/types'
import { cn, formatTimestamp } from '@/lib/utils'
import { User, Bot } from 'lucide-react'

interface ChatMessageProps {
  message: ChatMessageType
  className?: string
}

export default function ChatMessage({ message, className }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex gap-3 mb-4', isUser ? 'justify-end' : 'justify-start', className)}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
          <Bot className="w-4 h-4 text-primary-600" />
        </div>
      )}
      
      <div className={cn('flex flex-col', isUser ? 'items-end' : 'items-start')}>
        <div className={cn(
          'chat-bubble',
          isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'
        )}>
          <div className="prose prose-sm max-w-none">
            {message.content.split('\n').map((line, index) => {
              if (line.startsWith('**') && line.endsWith('**')) {
                return (
                  <h4 key={index} className="font-semibold text-sm mb-1 mt-2">
                    {line.slice(2, -2)}
                  </h4>
                )
              }
              if (line.startsWith('- ')) {
                return (
                  <li key={index} className="text-sm ml-4">
                    {line.slice(2)}
                  </li>
                )
              }
              if (line.trim() === '') {
                return <br key={index} />
              }
              return (
                <p key={index} className="text-sm mb-1">
                  {line}
                </p>
              )
            })}
          </div>
        </div>
        
        <span className="text-xs text-gray-500 mt-1">
          {formatTimestamp(message.timestamp)}
        </span>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  )
}