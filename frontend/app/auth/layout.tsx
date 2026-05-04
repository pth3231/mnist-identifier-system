import Link from 'next/link'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo/Title */}
        <div className="mb-8 text-center">
          <Link href="/">
            <h1 className="text-3xl font-bold text-foreground mb-2">MNIST Identifier</h1>
          </Link>
          <p className="text-sm text-muted-foreground">Identify handwritten digits</p>
        </div>

        {/* Auth Card */}
        <div className="rounded-xl border border-muted bg-card overflow-hidden shadow-lg">
          {children}
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-6">
          Protected by industry-standard security
        </p>
      </div>
    </div>
  )
}
