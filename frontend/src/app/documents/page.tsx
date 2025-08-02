'use client'

import { useState } from 'react'
import DocumentUpload from '@/components/DocumentUpload'
import DocumentManager from '@/components/DocumentManager'
import { DocumentUploadResponse } from '@/types'

export default function DocumentsPage() {
  const [activeTab, setActiveTab] = useState<'upload' | 'manage'>('upload')
  const [refreshKey, setRefreshKey] = useState(0)

  const handleUploadComplete = (response: DocumentUploadResponse) => {
    // Switch to manage tab and refresh the list
    setActiveTab('manage')
    setRefreshKey(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">📚 Ethics Document Management</h1>
          <p className="mt-2 text-lg text-gray-600">
            Upload and manage documents for the federal ethics knowledge base
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="border border-gray-200 rounded-lg p-1 bg-white">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-6 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'upload'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              📤 Upload Document
            </button>
            <button
              onClick={() => setActiveTab('manage')}
              className={`px-6 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === 'manage'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              📋 Manage Documents
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex justify-center">
          {activeTab === 'upload' ? (
            <DocumentUpload onUploadComplete={handleUploadComplete} />
          ) : (
            <DocumentManager key={refreshKey} />
          )}
        </div>

        {/* Info Section */}
        <div className="mt-12 max-w-4xl mx-auto">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 How Document Upload Works</h3>
            <div className="space-y-2 text-sm text-blue-800">
              <p>• <strong>Automatic Processing:</strong> PDF documents are automatically split into searchable chunks</p>
              <p>• <strong>Vector Embedding:</strong> Text chunks are converted to embeddings for similarity search</p>
              <p>• <strong>Immediate Availability:</strong> Uploaded documents become available for ethics consultations instantly</p>
              <p>• <strong>Smart Retrieval:</strong> The system finds the most relevant document sections for each query</p>
            </div>
          </div>
        </div>

        {/* Navigation Back */}
        <div className="mt-8 text-center">
          <a
            href="/"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            ← Back to Ethics Consultation
          </a>
        </div>
      </div>
    </div>
  )
}