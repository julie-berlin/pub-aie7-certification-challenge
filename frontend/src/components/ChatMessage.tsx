'use client'

import { ChatMessage as ChatMessageType, EthicsAssessment } from '@/types'
import { cn, formatTimestamp } from '@/lib/utils'
import { User, Bot, Download } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import AssessmentCard from './AssessmentCard'

interface ChatMessageProps {
  message: ChatMessageType
  assessment?: EthicsAssessment
  className?: string
}

export default function ChatMessage({ message, assessment, className }: ChatMessageProps) {
  const isUser = message.role === 'user'

  const downloadMarkdown = () => {
    const blob = new Blob([message.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ethics-guidance-${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className={cn('flex gap-3 mb-4', isUser ? 'justify-end' : 'justify-start', className)}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
          <Bot className="w-4 h-4 text-primary-600" />
        </div>
      )}
      
      <div className={cn('flex flex-col', isUser ? 'items-end' : 'items-start')}>
        <div className={cn(
          'chat-bubble relative group',
          isUser ? 'chat-bubble-user' : 'chat-bubble-assistant'
        )}>
          {!isUser && (
            <button
              onClick={downloadMarkdown}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-gray-100 text-gray-500 hover:text-gray-700"
              title="Download as Markdown"
            >
              <Download className="w-4 h-4" />
            </button>
          )}
          
          {/* Only show verbose text response if no assessment is available */}
          {!assessment && (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: (props) => <h1 className="text-lg font-bold mb-2 mt-3" {...props} />,
                  h2: (props) => <h2 className="text-base font-bold mb-2 mt-3" {...props} />,
                  h3: (props) => <h3 className="text-sm font-bold mb-1 mt-2" {...props} />,
                  h4: (props) => <h4 className="text-sm font-semibold mb-1 mt-2" {...props} />,
                  p: (props) => <p className="text-sm mb-2" {...props} />,
                  ul: (props) => <ul className="list-disc ml-4 mb-2 space-y-1" {...props} />,
                  ol: (props) => <ol className="list-decimal ml-4 mb-2 space-y-1" {...props} />,
                  li: (props) => <li className="text-sm" {...props} />,
                  strong: (props) => <strong className="font-semibold" {...props} />,
                  em: (props) => <em className="italic" {...props} />,
                  code: (props) => <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono" {...props} />,
                  blockquote: (props) => <blockquote className="border-l-4 border-gray-300 pl-3 italic text-gray-600" {...props} />,
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
          
          {/* Show assessment card for assistant messages with assessment */}
          {!isUser && assessment && (
            <div className="mt-4">
              <AssessmentCard assessment={assessment} />
            </div>
          )}
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