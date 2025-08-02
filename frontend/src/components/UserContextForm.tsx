'use client'

import { useState } from 'react'
import { UserContext } from '@/types'
import { cn } from '@/lib/utils'

interface UserContextFormProps {
  initialContext?: UserContext
  onSubmit: (context: UserContext) => void
  className?: string
}

const ROLE_OPTIONS = [
  { value: 'federal_employee', label: 'Federal Employee' },
  { value: 'contractor', label: 'Government Contractor' },
  { value: 'appointed_official', label: 'Appointed Official' },
  { value: 'elected_official', label: 'Elected Official' },
]

const SENIORITY_OPTIONS = [
  { value: 'entry_level', label: 'Entry Level (GS 1-7)' },
  { value: 'mid_level', label: 'Mid Level (GS 8-12)' },
  { value: 'senior_level', label: 'Senior Level (GS 13-15)' },
  { value: 'executive', label: 'Executive (SES/Political)' },
]

const CLEARANCE_OPTIONS = [
  { value: 'none', label: 'No Clearance' },
  { value: 'public_trust', label: 'Public Trust' },
  { value: 'secret', label: 'Secret' },
  { value: 'top_secret', label: 'Top Secret' },
]

export default function UserContextForm({ 
  initialContext, 
  onSubmit, 
  className 
}: UserContextFormProps) {
  const [context, setContext] = useState<UserContext>(
    initialContext || {
      role: 'federal_employee',
      agency: '',
      seniority: 'mid_level',
      clearance: 'none',
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(context)
  }

  const updateContext = (field: keyof UserContext, value: string) => {
    setContext(prev => ({ ...prev, [field]: value }))
  }

  return (
    <form onSubmit={handleSubmit} className={cn('space-y-4', className)}>
      <div>
        <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
          Role
        </label>
        <select
          id="role"
          value={context.role}
          onChange={(e) => updateContext('role', e.target.value)}
          className="input-field"
          required
        >
          {ROLE_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="agency" className="block text-sm font-medium text-gray-700 mb-1">
          Agency/Department
        </label>
        <input
          type="text"
          id="agency"
          value={context.agency}
          onChange={(e) => updateContext('agency', e.target.value)}
          className="input-field"
          placeholder="e.g., Department of Defense, EPA, GSA"
          required
        />
      </div>

      <div>
        <label htmlFor="seniority" className="block text-sm font-medium text-gray-700 mb-1">
          Seniority Level
        </label>
        <select
          id="seniority"
          value={context.seniority}
          onChange={(e) => updateContext('seniority', e.target.value)}
          className="input-field"
          required
        >
          {SENIORITY_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="clearance" className="block text-sm font-medium text-gray-700 mb-1">
          Security Clearance
        </label>
        <select
          id="clearance"
          value={context.clearance}
          onChange={(e) => updateContext('clearance', e.target.value)}
          className="input-field"
          required
        >
          {CLEARANCE_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <button type="submit" className="btn-primary w-full">
        Continue to Chat
      </button>
    </form>
  )
}