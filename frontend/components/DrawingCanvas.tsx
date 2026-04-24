'use client'

import { forwardRef, useImperativeHandle, useRef, useEffect, useState } from 'react'

interface DrawingCanvasProps {
  width: number
  height: number
  onPrediction: (predictions: Array<{ character: string, confidence: number }>) => void
}

interface DrawingCanvasHandle {
  clear: () => void
  undo: () => void
  redo: () => void
  getImageData: () => ImageData | null
}

interface Point {
  x: number
  y: number
}

interface Stroke {
  points: Point[]
}

const DrawingCanvas = forwardRef<DrawingCanvasHandle, DrawingCanvasProps>(
  ({ width, height, onPrediction }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const [isDrawing, setIsDrawing] = useState(false)
    const [currentStroke, setCurrentStroke] = useState<Point[]>([])
    const [strokeHistory, setStrokeHistory] = useState<Stroke[]>([])
    const [redoStack, setRedoStack] = useState<Stroke[]>([])

    // Initialize canvas with black background
    useEffect(() => {
      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.fillStyle = '#000000'
          ctx.fillRect(0, 0, width, height)
          ctx.strokeStyle = '#ffffff'
          ctx.lineWidth = 3
          ctx.lineCap = 'round'
          ctx.lineJoin = 'round'
        }
      }
    }, [width, height])

    // Redraw all strokes from history
    const redrawCanvas = (strokes: Stroke[]) => {
      const canvas = canvasRef.current
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      // Clear canvas
      ctx.fillStyle = '#000000'
      ctx.fillRect(0, 0, width, height)
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 3
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'

      // Redraw all strokes
      strokes.forEach(stroke => {
        if (stroke.points.length === 0) return

        ctx.beginPath()
        ctx.moveTo(stroke.points[0].x, stroke.points[0].y)

        // Draw dot at start
        ctx.arc(stroke.points[0].x, stroke.points[0].y, ctx.lineWidth / 2, 0, Math.PI * 2)
        ctx.fill()

        // Draw lines for rest of stroke
        for (let i = 1; i < stroke.points.length; i++) {
          ctx.beginPath()
          ctx.moveTo(stroke.points[i - 1].x, stroke.points[i - 1].y)
          ctx.lineTo(stroke.points[i].x, stroke.points[i].y)
          ctx.stroke()
        }
      })
    }

    // Undo removes the last stroke
    const undoCanvas = () => {
      if (strokeHistory.length === 0) return

      const newHistory = [...strokeHistory]
      const removed = newHistory.pop()

      if (removed) {
        setStrokeHistory(newHistory)
        setRedoStack(prev => [...prev, removed])
        redrawCanvas(newHistory)
      }
    }

    // Redo adds back the last removed stroke
    const redoCanvas = () => {
      if (redoStack.length === 0) return

      const newRedo = [...redoStack]
      const stroke = newRedo.pop()

      if (stroke) {
        const newHistory = [...strokeHistory, stroke]
        setStrokeHistory(newHistory)
        setRedoStack(newRedo)
        redrawCanvas(newHistory)
      }
    }

    // Clear all strokes
    const clearCanvas = () => {
      setStrokeHistory([])
      setRedoStack([])
      setCurrentStroke([])

      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        if (ctx) {
          ctx.fillStyle = '#000000'
          ctx.fillRect(0, 0, width, height)
        }
      }
    }

    useImperativeHandle(ref, () => ({
      clear: clearCanvas,
      undo: undoCanvas,
      redo: redoCanvas,
      getImageData: () => {
        const canvas = canvasRef.current
        if (canvas) {
          const ctx = canvas.getContext('2d')
          if (ctx) {
            return ctx.getImageData(0, 0, width, height)
          }
        }
        return null
      }
    }))

    const getScaledCoordinates = (clientX: number, clientY: number) => {
      const canvas = canvasRef.current
      if (!canvas) return { x: 0, y: 0 }

      const rect = canvas.getBoundingClientRect()
      const scaleX = canvas.width / rect.width
      const scaleY = canvas.height / rect.height

      return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY
      }
    }

    const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current
      if (!canvas) return

      const { x, y } = getScaledCoordinates(e.clientX, e.clientY)

      setIsDrawing(true)
      setCurrentStroke([{ x, y }])
      setRedoStack([]) // Clear redo stack on new stroke

      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.arc(x, y, ctx.lineWidth / 2, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!isDrawing || currentStroke.length === 0) return

      const canvas = canvasRef.current
      if (!canvas) return

      const { x, y } = getScaledCoordinates(e.clientX, e.clientY)

      setCurrentStroke(prev => [...prev, { x, y }])

      const ctx = canvas.getContext('2d')
      if (ctx && currentStroke.length > 0) {
        const lastPoint = currentStroke[currentStroke.length - 1]
        ctx.beginPath()
        ctx.moveTo(lastPoint.x, lastPoint.y)
        ctx.lineTo(x, y)
        ctx.stroke()
      }

      // Simulate prediction
      simulatePrediction()
    }

    const stopDrawing = () => {
      if (currentStroke.length > 0) {
        // Save stroke to history
        setStrokeHistory(prev => [...prev, { points: currentStroke }])
      }

      setIsDrawing(false)
      setCurrentStroke([])
    }

    const simulatePrediction = () => {
      const samplePredictions = [
        { character: 'あ', confidence: 0.85 },
        { character: 'ア', confidence: 0.12 },
        { character: '阿', confidence: 0.03 },
      ]
      onPrediction(samplePredictions)
    }

    return (
      <div className="rounded-xl border border-muted bg-card overflow-hidden shadow-sm">
        {/* Header with controls */}
        <div className="border-b border-muted bg-muted/10 backdrop-blur-sm px-4 py-3 flex items-center justify-between">
          <h2 className="text-base font-semibold text-foreground">Draw Character</h2>
          <div className="flex items-center gap-1">
            <button
              onClick={() => {
                if (ref && 'current' in ref && ref.current) {
                  ref.current.undo()
                }
              }}
              className="inline-flex items-center justify-center w-9 h-9 p-2 rounded-lg border border-transparent text-muted-foreground bg-muted/5 hover:bg-muted/20 hover:text-foreground hover:border-muted transition-all active:scale-95"
              aria-label="Undo"
              title="Undo (Ctrl+Z)"
              type="button"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
              </svg>
            </button>
            <button
              onClick={() => {
                if (ref && 'current' in ref && ref.current) {
                  ref.current.redo()
                }
              }}
              className="inline-flex items-center justify-center w-9 h-9 p-2 rounded-lg border border-transparent text-muted-foreground bg-muted/5 hover:bg-muted/20 hover:text-foreground hover:border-muted transition-all active:scale-95"
              aria-label="Redo"
              title="Redo (Ctrl+Shift+Z)"
              type="button"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l6-6m0 0l-6-6m6 6H9a6 6 0 000 12h3" />
              </svg>
            </button>
            <div className="w-px h-5 bg-muted opacity-30 mx-1"></div>
            <button
              onClick={() => {
                if (ref && 'current' in ref && ref.current) {
                  ref.current.clear()
                }
              }}
              className="inline-flex items-center justify-center w-9 h-9 p-2 rounded-lg border border-transparent text-red/70 bg-muted/5 hover:bg-red/15 hover:text-red hover:border-red/30 transition-all active:scale-95"
              aria-label="Clear all"
              title="Clear canvas"
              type="button"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="bg-linear-to-b from-white to-gray-100 dark:from-background dark:to-muted/20 p-6 flex items-center justify-center">
          <div className="w-full max-w-sm relative">
            <canvas
              ref={canvasRef}
              width={width}
              height={height}
              className="w-full cursor-crosshair aspect-square image-rendering-pixelated bg-black border-2 border-muted/50 rounded-lg shadow-lg transition-shadow"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={(e) => {
                e.preventDefault()
                startDrawing(e as unknown as React.MouseEvent<HTMLCanvasElement>)
              }}
              onTouchMove={(e) => {
                e.preventDefault()
                draw(e as unknown as React.MouseEvent<HTMLCanvasElement>)
              }}
              onTouchEnd={stopDrawing}
            />
            {/* Center crosshair - only visible as visual guide */}
            <svg
              className="absolute inset-0 pointer-events-none w-full h-full"
            >
              <line x1="50%" y1="15%" x2="50%" y2="85%" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
              <line x1="15%" y1="50%" x2="85%" y2="50%" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
            </svg>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-muted bg-muted/10 backdrop-blur-sm px-4 py-3 text-sm text-muted-foreground text-center">
          Click and drag to draw • Touch to draw on mobile
        </div>
      </div>
    )
  }
)

// DrawingCanvas.displayName = 'DrawingCanvas'

export default DrawingCanvas