'use client'

interface ReadOnlyBoxProps {
  text: string[]
  onClear?: () => void
}

export default function ReadOnlyBox({ text, onClear }: ReadOnlyBoxProps) {
  return (
    <div className="rounded-xl border border-muted bg-card overflow-hidden shadow-sm">
      {/* Header */}
      <div className="border-b border-muted bg-muted/10 backdrop-blur-sm px-4 py-3">
        <h2 className="text-base font-semibold text-foreground">Output</h2>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Text Display Area */}
        <div className="rounded-lg border border-muted bg-muted/5 p-4 mb-4 min-h-25 flex items-center justify-center">
          {text.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center">Selected characters will appear here</p>
          ) : (
            <div className="text-[2.25rem] font-bold text-center leading-relaxed break-all">
              {text.join('')}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => navigator.clipboard.writeText(text.join(''))}
            disabled={text.length === 0}
            className="flex-1 inline-flex items-center justify-center rounded-lg px-3 py-2 text-sm font-medium border border-muted bg-muted/5 hover:bg-muted/20 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
          >
            Copy
          </button>
          <button
            onClick={() => onClear && onClear()}
            className="flex-1 inline-flex items-center justify-center rounded-lg px-3 py-2 text-sm font-medium border border-muted bg-muted/5 hover:bg-muted/20 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  )
}