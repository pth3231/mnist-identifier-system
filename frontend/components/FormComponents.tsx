'use client'

import { useFormStatus } from 'react-dom'
import { ReactNode } from 'react'

interface SubmitButtonProps {
  children: ReactNode
  loadingText?: string
  className?: string
}

export function SubmitButton({ 
  children, 
  loadingText = 'Loading...', 
  className = '' 
}: SubmitButtonProps) {
  const { pending } = useFormStatus()

  return (
    <button
      type="submit"
      disabled={pending}
      className={`w-full px-4 py-2.5 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95 ${className}`}
    >
      {pending ? loadingText : children}
    </button>
  )
}

interface FormInputProps {
  id: string
  label: string
  type: string
  name: string
  placeholder: string
  disabled?: boolean
}

export function FormInput({ 
  id, 
  label, 
  type, 
  name, 
  placeholder, 
  disabled = false 
}: FormInputProps) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-foreground mb-2">
        {label}
      </label>
      <input
        id={id}
        type={type}
        name={name}
        placeholder={placeholder}
        className="w-full px-4 py-2 rounded-lg border border-muted bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={disabled}
        required
      />
    </div>
  )
}
