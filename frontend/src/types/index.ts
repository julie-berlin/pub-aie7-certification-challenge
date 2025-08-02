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

export interface DocumentInfo {
  document_id: string
  filename: string
  file_size: number
  upload_timestamp: string
  chunks_count: number
  category: string
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  file_size: number
  chunks_created: number
  processing_time_seconds: number
  status: string
}