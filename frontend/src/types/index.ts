export interface UserContext {
  role: string
  agency: string
  seniority: string
  clearance: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface EthicsAssessmentRequest {
  question: string
  userContext: UserContext
}

export interface EthicsAssessmentResponse {
  response: string
  searchPlan?: string
  sources?: {
    federalLawChunks: number
    webSources: number
  }
  error?: string
}

export interface ChatSession {
  id: string
  messages: ChatMessage[]
  userContext: UserContext
  createdAt: Date
  updatedAt: Date
}