// Simple auth utility - replace with actual auth solution (NextAuth.js, Supabase, etc.)

export interface User {
  name?: string
  email: string
}

export const getUser = (): User | null => {
  if (typeof window === 'undefined') return null
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

export const setUser = (user: User) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user', JSON.stringify(user))
  }
}

export const logout = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('user')
  }
}

export const isAuthenticated = (): boolean => {
  return getUser() !== null
}
