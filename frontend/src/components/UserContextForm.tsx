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

const AGENCY_OPTIONS = [
  { value: 'Department of Defense', label: 'Department of Defense (DoD)' },
  { value: 'Department of Homeland Security', label: 'Department of Homeland Security (DHS)' },
  { value: 'Department of Justice', label: 'Department of Justice (DOJ)' },
  { value: 'Department of Treasury', label: 'Department of Treasury' },
  { value: 'Department of State', label: 'Department of State' },
  { value: 'Department of Health and Human Services', label: 'Department of Health and Human Services (HHS)' },
  { value: 'General Services Administration', label: 'General Services Administration (GSA)' },
  { value: 'Environmental Protection Agency', label: 'Environmental Protection Agency (EPA)' },
  { value: 'National Aeronautics and Space Administration', label: 'National Aeronautics and Space Administration (NASA)' },
  { value: 'Social Security Administration', label: 'Social Security Administration (SSA)' },
  { value: 'Department of Veterans Affairs', label: 'Department of Veterans Affairs (VA)' },
  { value: 'Department of Education', label: 'Department of Education' },
  { value: 'Department of Transportation', label: 'Department of Transportation (DOT)' },
  { value: 'Department of Energy', label: 'Department of Energy (DOE)' },
  { value: 'Department of Agriculture', label: 'Department of Agriculture (USDA)' },
  { value: 'Other', label: 'Other Agency' },
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
      agency: 'Department of Defense',
      seniority: 'mid_level',
      clearance: 'none',
    }
  )
  const [customAgency, setCustomAgency] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const finalContext = {
      ...context,
      agency: context.agency === 'Other' ? customAgency : context.agency
    }
    onSubmit(finalContext)
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
        <select
          id="agency"
          value={context.agency}
          onChange={(e) => updateContext('agency', e.target.value)}
          className="input-field"
          required
        >
          {AGENCY_OPTIONS.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        
        {context.agency === 'Other' && (
          <div className="mt-2">
            <input
              type="text"
              value={customAgency}
              onChange={(e) => setCustomAgency(e.target.value)}
              className="input-field"
              placeholder="Enter your agency name"
              required
            />
          </div>
        )}
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