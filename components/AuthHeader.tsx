'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getUser, logout } from '@/lib/auth'

interface User {
  name?: string
  email: string
}

export default function AuthHeader() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    setUser(getUser())
  }, [])

  const handleLogout = () => {
    logout()
    setUser(null)
    setIsOpen(false)
    router.push('/')
  }

  return (
    <div className="flex items-center gap-4">
      {user ? (
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-muted hover:bg-muted/10 transition-all"
          >
            <span className="text-sm font-medium text-foreground">
              {user.name || user.email.split('@')[0]}
            </span>
            <svg
              className={`w-4 h-4 text-muted-foreground transition-transform ${
                isOpen ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>

          {/* Dropdown Menu */}
          {isOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-lg border border-muted bg-card shadow-lg overflow-hidden z-50">
              <div className="p-3 border-b border-muted bg-muted/5">
                <p className="text-sm font-medium text-foreground">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted/10 transition-all"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <Link
            href="/auth/signin"
            className="px-3 py-2 text-sm font-medium text-foreground hover:text-primary transition-colors"
          >
            Sign in
          </Link>
          <Link
            href="/auth/signup"
            className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-all"
          >
            Sign up
          </Link>
        </div>
      )}
    </div>
  )
}
