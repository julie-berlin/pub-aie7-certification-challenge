'use client'

import { useState } from 'react'
import { UserContext } from '@/types'
import UserContextForm from '@/components/UserContextForm'
import ChatInterface from '@/components/ChatInterface'
import { Shield, Scale, Users, AlertTriangle } from 'lucide-react'

export default function HomePage() {
  const [userContext, setUserContext] = useState<UserContext | null>(null)
  const [showChat, setShowChat] = useState(false)

  const handleContextSubmit = (context: UserContext) => {
    setUserContext(context)
    setShowChat(true)
  }

  const handleNewSession = () => {
    setUserContext(null)
    setShowChat(false)
  }

  if (showChat && userContext) {
    return (
      <div className="h-screen flex flex-col">
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">IntegriBot</h1>
                <p className="text-sm text-gray-600">
                  {userContext.agency} • {userContext.role.replace('_', ' ')}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <a
                href="/documents"
                className="btn-secondary text-sm"
              >
                📚 Manage Documents
              </a>
              <button
                onClick={handleNewSession}
                className="btn-secondary text-sm"
              >
                New Session
              </button>
            </div>
          </div>
        </header>
        
        <main className="flex-1 max-w-4xl mx-auto w-full">
          <ChatInterface userContext={userContext} className="h-full" />
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center">
              <Shield className="w-8 h-8 text-white" />
            </div>
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to IntegriBot
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Your AI-powered federal ethics compliance assistant. Get comprehensive guidance 
            on ethics violations, penalties, and reporting requirements.
          </p>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="card p-6 text-center">
              <Scale className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Legal Analysis</h3>
              <p className="text-sm text-gray-600">
                Federal ethics law interpretation and violation assessment
              </p>
            </div>
            
            <div className="card p-6 text-center">
              <AlertTriangle className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Risk Assessment</h3>
              <p className="text-sm text-gray-600">
                Severity analysis and potential penalty identification
              </p>
            </div>
            
            <div className="card p-6 text-center">
              <Users className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Personalized Guidance</h3>
              <p className="text-sm text-gray-600">
                Tailored advice based on your role and agency
              </p>
            </div>
          </div>
        </div>

        <div className="max-w-md mx-auto">
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Tell us about yourself
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              This information helps us provide more accurate and relevant ethics guidance.
            </p>
            
            <UserContextForm onSubmit={handleContextSubmit} />
          </div>
        </div>

        <div className="mt-8 text-center">
          <a
            href="/documents"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mb-4"
          >
            📚 Manage Ethics Documents →
          </a>
        </div>

        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-yellow-600" />
            <span className="text-sm text-yellow-800">
              This system provides guidance only and does not constitute legal advice
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}