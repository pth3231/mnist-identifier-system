'use client'

import { useState } from 'react'
import Link from 'next/link'
import { signUpAction } from '@/app/auth/actions'
import { FormInput, SubmitButton } from '@/components/FormComponents'

export default function SignUp() {
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(formData: FormData) {
    setError(null)
    const result = await signUpAction(formData)
    if (!result.success && result.error) {
      setError(result.error)
    }
  }

  return (
    <div className="p-6 sm:p-8">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">Create account</h2>
        <p className="text-sm text-muted-foreground">Sign up to start learning Japanese</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red/15 border border-red/30 rounded-lg">
          <p className="text-sm text-red">{error}</p>
        </div>
      )}

      {/* Form */}
      <form action={handleSubmit} className="space-y-4">
        <FormInput
          id="name"
          name="name"
          label="Full name"
          type="text"
          placeholder="John Doe"
        />

        <FormInput
          id="email"
          name="email"
          label="Email address"
          type="email"
          placeholder="you@example.com"
        />

        <FormInput
          id="password"
          name="password"
          label="Password"
          type="password"
          placeholder="••••••"
        />

        <FormInput
          id="confirmPassword"
          name="confirmPassword"
          label="Confirm password"
          type="password"
          placeholder="••••••"
        />

        {/* Submit Button */}
        <SubmitButton loadingText="Creating account...">
          Sign up
        </SubmitButton>
      </form>

      {/* Divider */}
      <div className="my-6 flex items-center gap-4">
        <div className="flex-1 h-px bg-muted"></div>
        <span className="text-xs text-muted-foreground">or</span>
        <div className="flex-1 h-px bg-muted"></div>
      </div>

      {/* Sign In Link */}
      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link href="/auth/signin" className="text-primary hover:underline font-medium">
          Sign in
        </Link>
      </p>
    </div>
  )
}
