'use client'

import { useState, useRef, useEffect } from 'react'
import DrawingCanvas from '@/components/DrawingCanvas'
import RecommendationBox from '@/components/RecommendationBox'
import ReadOnlyBox from '@/components/ReadOnlyBox'
import AuthHeader from '@/components/AuthHeader'

interface T_Prediction {
  character: string,
  confidence: number
}

export default function Home() {
  const [predictions, setPredictions] = useState<Array<T_Prediction>>([])
  const [selectedText, setSelectedText] = useState<string[]>([])
  const drawingCanvasRef = useRef<{
    clear: () => void
    undo: () => void
    redo: () => void
    getImageData: () => ImageData | null
  } | null>(null)

  const handlePrediction = (newPredictions: Array<T_Prediction>) => {
    setPredictions(newPredictions)
  }

  const handleCharacterSelect = (character: string) => {
    setSelectedText(prev => [...prev, character])
    setPredictions([])
    // Clear canvas
    if (drawingCanvasRef.current) {
      drawingCanvasRef.current.clear()
    }
  }

  const handleExport = () => {
    if (drawingCanvasRef.current) {
      const imageData = drawingCanvasRef.current.getImageData()
      if (imageData) {
        const canvas = document.createElement('canvas')
        canvas.width = imageData.width
        canvas.height = imageData.height
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.putImageData(imageData, 0, 0)
          const dataUrl = canvas.toDataURL('image/jpeg')
          const link = document.createElement('a')
          link.download = 'japanese-character.jpg'
          link.href = dataUrl
          link.click()
        }
      }
    }
  }

  return (
    <main className="container mx-auto bg-background text-foreground min-w-2xl">
      {/* Header */}
      <header className="border-b border-muted bg-muted/10 backdrop-blur-sm sticky top-0 z-50">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-foreground">MNIST Identifier</h1>
              <p className="text-sm text-muted-foreground">Draw & identify handwritten digits</p>
            </div>
            <AuthHeader />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <div className="grid grid-cols-1 gap-6">
            <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-6">
              {/* Left Column: Drawing Canvas */}
              <div className="flex flex-col">
                <DrawingCanvas
                  ref={drawingCanvasRef}
                  onPrediction={handlePrediction}
                  width={96}
                  height={96}
                />
                <button
                  onClick={handleExport}
                  className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2.5 rounded-md font-medium w-full mt-4 transition-colors"
                >
                  Export Image
                </button>
              </div>

              <div className="flex flex-col gap-4">
                <RecommendationBox
                  predictions={predictions}
                  onCharacterSelect={handleCharacterSelect}
                />
                <ReadOnlyBox text={selectedText} onClear={() => setSelectedText([])} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}