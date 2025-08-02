'use client'

import { useState, useRef } from 'react'
import { uploadDocument } from '@/lib/api'
import { DocumentUploadResponse } from '@/types'

interface DocumentUploadProps {
  onUploadComplete?: (response: DocumentUploadResponse) => void
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string>('')
  const [dragActive, setDragActive] = useState(false)
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('ethics_guidance')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    if (!file.type.includes('pdf')) {
      setUploadProgress('❌ Only PDF files are supported')
      return
    }

    if (file.size > 50 * 1024 * 1024) {
      setUploadProgress('❌ File size must be less than 50MB')
      return
    }

    setIsUploading(true)
    setUploadProgress('📄 Processing document...')

    try {
      const response = await uploadDocument(file, description, category)
      setUploadProgress(
        `✅ Successfully uploaded ${response.filename} (${response.chunks_created} chunks created)`
      )
      
      if (onUploadComplete) {
        onUploadComplete(response)
      }

      // Reset form
      setDescription('')
      setCategory('ethics_guidance')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (error) {
      console.error('Upload error:', error)
      setUploadProgress(`❌ Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsUploading(false)
    }
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">📚 Upload Ethics Document</h2>
      
      <div className="space-y-4">
        {/* Description Input */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description (optional)
          </label>
          <input
            type="text"
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief description of the document"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isUploading}
          />
        </div>

        {/* Category Select */}
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isUploading}
          >
            <option value="ethics_guidance">Ethics Guidance</option>
            <option value="regulations">Regulations</option>
            <option value="case_studies">Case Studies</option>
            <option value="training_materials">Training Materials</option>
          </select>
        </div>

        {/* File Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            multiple={false}
            onChange={handleFileInput}
            className="hidden"
            disabled={isUploading}
          />

          <div className="space-y-4">
            <div className="text-6xl">📄</div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                {dragActive ? 'Drop your PDF here' : 'Upload a PDF document'}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Drag and drop or click to select a file (max 50MB)
              </p>
            </div>
            
            <button
              type="button"
              onClick={openFileDialog}
              disabled={isUploading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
            >
              {isUploading ? 'Processing...' : 'Select PDF File'}
            </button>
          </div>
        </div>

        {/* Upload Progress */}
        {uploadProgress && (
          <div className={`p-3 rounded-md text-sm ${
            uploadProgress.startsWith('✅') 
              ? 'bg-green-50 text-green-800 border border-green-200'
              : uploadProgress.startsWith('❌')
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'bg-blue-50 text-blue-800 border border-blue-200'
          }`}>
            {uploadProgress}
          </div>
        )}

        {/* Info */}
        <div className="text-xs text-gray-500 mt-4">
          <p>• Only PDF files are supported</p>
          <p>• Maximum file size: 50MB</p>
          <p>• Documents are processed and added to the knowledge base automatically</p>
        </div>
      </div>
    </div>
  )
}