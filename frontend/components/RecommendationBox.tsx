'use client'

interface Prediction {
  character: string
  confidence: number
}

interface RecommendationBoxProps {
  predictions: Prediction[]
  onCharacterSelect: (character: string) => void
}

export default function RecommendationBox({ predictions, onCharacterSelect }: RecommendationBoxProps) {
  return (
    <div className="rounded-xl border border-muted bg-card overflow-hidden shadow-sm">
      {/* Header */}
      <div className="border-b border-muted bg-muted/10 backdrop-blur-sm px-4 py-3">
        <h2 className="text-base font-semibold text-foreground">Recommendations</h2>
      </div>

      {/* Content */}
      <div className="p-4">
        {predictions.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-center">
            <p className="text-sm text-muted-foreground">Draw a character to see predictions</p>
          </div>
        ) : (
          <div className="space-y-2">
            {predictions.map((prediction, index) => (
              <button
                key={index}
                onClick={() => onCharacterSelect(prediction.character)}
                className="w-full flex items-center justify-between border border-muted bg-muted/5 hover:bg-muted/20 rounded-lg px-4 py-3 mb-2 transition-all active:scale-95"
                title={`Confidence: ${(prediction.confidence * 100).toFixed(1)}%`}
              >
                <span className="text-[1.5rem] font-semibold">{prediction.character}</span>
                <span className="text-xs font-medium text-muted-foreground bg-muted/30 px-2 py-1 rounded">
                  {(prediction.confidence * 100).toFixed(0)}%
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}