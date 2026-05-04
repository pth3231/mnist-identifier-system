'use server'

import { redirect } from 'next/navigation'
import { setAuth, setToken, setUser, logout as clearAuth } from '@/utils/auth'

const API_URL = process.env.BACKEND_API

export interface AuthResult {
  success: boolean
  error?: string
  user?: {
    id?: number
    username?: string
    email: string
  }
}

export async function signInAction(formData: FormData): Promise<AuthResult> {
  const username = formData.get('username') as string
  const password = formData.get('password') as string

  // Validation
  if (!username || !password) {
    return { success: false, error: 'Please fill in all fields' }
  }

  if (username.length < 3) {
    return { success: false, error: 'Username must be at least 3 characters' }
  }

  if (password.length < 6) {
    return { success: false, error: 'Password must be at least 6 characters' }
  }

  try {
    const response = await fetch(`${API_URL}/api/auth/sign-in`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      return { 
        success: false, 
        error: errorData.detail || 'Invalid username or password' 
      }
    }

    const data = await response.json()
    
    // Store auth data on the client side
    setAuth(data.access_token, data.user)

    redirect('/')
  } catch (error) {
    return { 
      success: false, 
      error: 'Failed to sign in. Please try again.' 
    }
  }
}

export async function signUpAction(formData: FormData): Promise<AuthResult> {
  const username = formData.get('username') as string
  const email = formData.get('email') as string
  const password = formData.get('password') as string
  const confirmPassword = formData.get('confirmPassword') as string

  // Validation
  if (!username || !email || !password || !confirmPassword) {
    return { success: false, error: 'Please fill in all fields' }
  }

  if (username.length < 3) {
    return { success: false, error: 'Username must be at least 3 characters' }
  }

  if (email.length < 5) {
    return { success: false, error: 'Invalid email address' }
  }

  if (password.length < 6) {
    return { success: false, error: 'Password must be at least 6 characters' }
  }

  if (password !== confirmPassword) {
    return { success: false, error: 'Passwords do not match' }
  }

  try {
    const response = await fetch(`${API_URL}/api/auth/sign-up`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      return { 
        success: false, 
        error: errorData.detail || 'Failed to create account' 
      }
    }

    const data = await response.json()
    
    // Auto sign-in after signup
    setAuth(data.access_token || '', data)

    redirect('/')
  } catch (error) {
    return { 
      success: false, 
      error: 'Failed to create account. Please try again.' 
    }
  }
}

export async function signOutAction(): Promise<void> {
  try {
    const token = getServerToken()
    if (token) {
      await fetch(`${API_URL}/api/auth/sign-out`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
    }
  } catch (error) {
    console.error('Sign-out error:', error)
  } finally {
    clearAuth()
  }
}

// Helper to get token on server side (for API calls)
function getServerToken(): string | null {
  // In a real app, you'd get this from cookies or session
  return null
}
