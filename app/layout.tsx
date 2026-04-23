import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Japanese Character Identifier',
  description: 'Draw Japanese characters and get real-time identification',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  )
}