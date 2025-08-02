'use client'

import { useState, useEffect } from 'react'
import { listDocuments, deleteDocument } from '@/lib/api'
import { DocumentInfo } from '@/types'

export default function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      setError('')
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err) {
      setError(`Failed to load documents: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (documentId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
      return
    }

    try {
      setDeleting(documentId)
      await deleteDocument(documentId)
      setDocuments(docs => docs.filter(doc => doc.document_id !== documentId))
    } catch (err) {
      setError(`Failed to delete document: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setDeleting(null)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (timestamp: string): string => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getCategoryIcon = (category: string): string => {
    switch (category) {
      case 'ethics_guidance': return '⚖️'
      case 'regulations': return '📋'
      case 'case_studies': return '📖'
      case 'training_materials': return '🎓'
      default: return '📄'
    }
  }

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading documents...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">📚 Document Library</h2>
        <button
          onClick={loadDocuments}
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          🔄 Refresh
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">📂</div>
          <p className="text-gray-600">No documents uploaded yet</p>
          <p className="text-sm text-gray-500 mt-2">Upload your first ethics document to get started</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Chunks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Uploaded
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documents.map((doc) => (
                <tr key={doc.document_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-2xl mr-3">📄</div>
                      <div>
                        <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                          {doc.filename}
                        </div>
                        <div className="text-xs text-gray-500">
                          ID: {doc.document_id.substring(0, 8)}...
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-lg mr-2">{getCategoryIcon(doc.category)}</span>
                      <span className="text-sm text-gray-900 capitalize">
                        {doc.category.replace('_', ' ')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {doc.chunks_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(doc.upload_timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleDelete(doc.document_id, doc.filename)}
                      disabled={deleting === doc.document_id}
                      className="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {deleting === doc.document_id ? '⏳ Deleting...' : '🗑️ Delete'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-4 text-sm text-gray-500">
        Total: {documents.length} document{documents.length !== 1 ? 's' : ''}
        {documents.length > 0 && (
          <>
            {' • '}
            {documents.reduce((sum, doc) => sum + doc.chunks_count, 0)} total chunks
            {' • '}
            {formatFileSize(documents.reduce((sum, doc) => sum + doc.file_size, 0))} total size
          </>
        )}
      </div>
    </div>
  )
}