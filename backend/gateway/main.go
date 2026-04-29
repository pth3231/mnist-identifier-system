package main

import (
	"context"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	pb "github.com/pth3231/mnist-identifier-system/gateway/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// GatewayServer handles HTTP to gRPC routing
type GatewayServer struct {
	mlServiceAddr  string
	mlConn         *grpc.ClientConn
	connLock       sync.RWMutex
	maxRetries     int
	requestTimeout time.Duration
}

// Request/Response types for prediction
type PredictionRequest struct {
	ImageData string `json:"image_data"` // Hex-encoded image bytes
	Width     int    `json:"image_width"`
	Height    int    `json:"image_height"`
}

type PredictionResult struct {
	Digit      int     `json:"digit"`
	Confidence float32 `json:"confidence"`
}

type PredictionResponse struct {
	Predictions      []PredictionResult `json:"predictions"`
	ProcessingTimeMs int64              `json:"processing_time_ms"`
	ModelVersion     string             `json:"model_version"`
}

// NewGatewayServer creates a new gateway instance
func NewGatewayServer(mlServiceAddr string, timeout time.Duration, maxRetries int) *GatewayServer {
	return &GatewayServer{
		mlServiceAddr:  mlServiceAddr,
		maxRetries:     maxRetries,
		requestTimeout: timeout,
	}
}

// Connect establishes gRPC connection to ML service
func (gs *GatewayServer) Connect(ctx context.Context) error {
	conn, err := grpc.NewClient(
		gs.mlServiceAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithDefaultCallOptions(grpc.MaxCallRecvMsgSize(10*1024*1024)),
	)
	if err != nil {
		return fmt.Errorf("failed to connect to ML service: %w", err)
	}

	gs.connLock.Lock()
	gs.mlConn = conn
	gs.connLock.Unlock()

	log.Printf("Connected to ML service at %s", gs.mlServiceAddr)
	return nil
}

// Close closes the gRPC connection
func (gs *GatewayServer) Close() error {
	gs.connLock.Lock()
	defer gs.connLock.Unlock()

	if gs.mlConn != nil {
		return gs.mlConn.Close()
	}
	return nil
}

// PredictHandler handles HTTP POST /predict requests
func (gs *GatewayServer) PredictHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse request
	var req PredictionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, fmt.Sprintf("Invalid request: %v", err), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Decode image data from hex
	imageData, err := hex.DecodeString(req.ImageData)
	if err != nil {
		http.Error(w, "Invalid image data encoding", http.StatusBadRequest)
		return
	}

	if len(imageData) == 0 {
		http.Error(w, "Image data is required", http.StatusBadRequest)
		return
	}

	// Auto-detect dimensions if not provided
	if req.Width == 0 || req.Height == 0 {
		size := len(imageData)
		if size == 784 {
			req.Width, req.Height = 28, 28
		} else if size == 9216 {
			req.Width, req.Height = 96, 96
		} else {
			http.Error(w, fmt.Sprintf("Unexpected image size: %d bytes", size), http.StatusBadRequest)
			return
		}
	}

	// Call ML service with retry
	grpcResp, err := gs.predictWithRetry(context.Background(), imageData, int32(req.Width), int32(req.Height))
	if err != nil {
		log.Printf("Prediction error: %v", err)
		http.Error(w, fmt.Sprintf("Prediction failed: %v", err), http.StatusInternalServerError)
		return
	}

	// Convert response
	predictions := make([]PredictionResult, len(grpcResp.Predictions))
	for i, pred := range grpcResp.Predictions {
		predictions[i] = PredictionResult{
			Digit:      int(pred.Digit),
			Confidence: pred.Confidence,
		}
	}

	resp := PredictionResponse{
		Predictions:      predictions,
		ProcessingTimeMs: grpcResp.ProcessingTimeMs,
		ModelVersion:     grpcResp.ModelVersion,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}

// predictWithRetry calls the ML service with retry logic
func (gs *GatewayServer) predictWithRetry(ctx context.Context, imageData []byte, width, height int32) (*pb.PredictionResponse, error) {
	var lastErr error

	for attempt := 0; attempt <= gs.maxRetries; attempt++ {
		if attempt > 0 {
			log.Printf("Retry attempt %d/%d", attempt, gs.maxRetries)
			time.Sleep(time.Duration(attempt*100) * time.Millisecond)
		}

		ctx, cancel := context.WithTimeout(ctx, gs.requestTimeout)
		defer cancel()

		resp, err := gs.predict(ctx, imageData, width, height)
		if err == nil {
			return resp, nil
		}

		lastErr = err
		log.Printf("Attempt %d failed: %v", attempt+1, err)
	}

	return nil, fmt.Errorf("prediction failed after %d retries: %w", gs.maxRetries+1, lastErr)
}

// predict calls the ML service once
func (gs *GatewayServer) predict(ctx context.Context, imageData []byte, width, height int32) (*pb.PredictionResponse, error) {
	gs.connLock.RLock()
	conn := gs.mlConn
	gs.connLock.RUnlock()

	if conn == nil {
		return nil, fmt.Errorf("ML service connection not available")
	}

	client := pb.NewMnistServiceClient(conn)
	req := &pb.PredictionRequest{
		ImageData:   imageData,
		ImageWidth:  width,
		ImageHeight: height,
	}
	return client.Predict(ctx, req)
}

// HealthHandler checks gateway and ML service health
func (gs *GatewayServer) HealthHandler(w http.ResponseWriter, r *http.Request) {
	gs.connLock.RLock()
	conn := gs.mlConn
	gs.connLock.RUnlock()

	if conn == nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]string{"status": "unhealthy", "reason": "ML service not connected"})
		return
	}

	// Check ML service health
	client := pb.NewMnistServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	resp, err := client.Health(ctx, &pb.HealthCheckRequest{})
	if err != nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]string{"status": "unhealthy", "reason": "ML service unreachable"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":        "healthy",
		"ml_service":    "serving",
		"model_version": resp.ModelVersion,
	})
}

// LivenessHandler for Kubernetes liveness probe
func (gs *GatewayServer) LivenessHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "alive"})
}

func main() {
	// Configuration from environment
	mlServiceAddr := os.Getenv("ML_SERVICE_ADDR")
	if mlServiceAddr == "" {
		mlServiceAddr = "localhost:50051"
	}

	gatewayPort := os.Getenv("GATEWAY_PORT")
	if gatewayPort == "" {
		gatewayPort = "8080"
	}

	requestTimeoutStr := os.Getenv("REQUEST_TIMEOUT_MS")
	requestTimeout := 5 * time.Second
	if requestTimeoutStr != "" {
		if ms, err := strconv.Atoi(requestTimeoutStr); err == nil {
			requestTimeout = time.Duration(ms) * time.Millisecond
		}
	}

	maxRetriesStr := os.Getenv("MAX_RETRIES")
	maxRetries := 2
	if maxRetriesStr != "" {
		if retries, err := strconv.Atoi(maxRetriesStr); err == nil {
			maxRetries = retries
		}
	}

	log.Printf("Starting gateway:")
	log.Printf("  ML Service: %s", mlServiceAddr)
	log.Printf("  Gateway Port: %s", gatewayPort)
	log.Printf("  Request Timeout: %s", requestTimeout)
	log.Printf("  Max Retries: %d", maxRetries)

	// Create gateway
	gateway := NewGatewayServer(mlServiceAddr, requestTimeout, maxRetries)

	// Connect to ML service
	if err := gateway.Connect(context.Background()); err != nil {
		log.Fatalf("Failed to connect to ML service: %v", err)
	}
	defer gateway.Close()

	// Register handlers
	http.HandleFunc("/health", gateway.HealthHandler)
	http.HandleFunc("/live", gateway.LivenessHandler)
	http.HandleFunc("/predict", gateway.PredictHandler)

	// Start server
	server := &http.Server{
		Addr:         ":" + gatewayPort,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	log.Printf("Gateway listening on %s", server.Addr)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v", err)
	}
}

// PredictHandler handles HTTP POST /predict requests
func (gs *GatewayServer) PredictHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse request
	var req PredictionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, fmt.Sprintf("Invalid request: %v", err), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Decode image data from hex
	imageData, err := hex.DecodeString(req.ImageData)
	if err != nil {
		http.Error(w, "Invalid image data encoding", http.StatusBadRequest)
		return
	}

	if len(imageData) == 0 {
		http.Error(w, "Image data is required", http.StatusBadRequest)
		return
	}

	// Auto-detect dimensions if not provided
	if req.Width == 0 || req.Height == 0 {
		size := len(imageData)
		if size == 784 {
			req.Width, req.Height = 28, 28
		} else if size == 9216 {
			req.Width, req.Height = 96, 96
		} else {
			http.Error(w, fmt.Sprintf("Unexpected image size: %d bytes", size), http.StatusBadRequest)
			return
		}
	}

	// Call ML service with retry
	grpcResp, err := gs.predictWithRetry(context.Background(), imageData, int32(req.Width), int32(req.Height))
	if err != nil {
		log.Printf("Prediction error: %v", err)
		http.Error(w, fmt.Sprintf("Prediction failed: %v", err), http.StatusInternalServerError)
		return
	}

	// Convert response
	predictions := make([]PredictionResult, len(grpcResp.Predictions))
	for i, pred := range grpcResp.Predictions {
		predictions[i] = PredictionResult{
			Digit:      int(pred.Digit),
			Confidence: pred.Confidence,
		}
	}

	resp := PredictionResponse{
		Predictions:      predictions,
		ProcessingTimeMs: grpcResp.ProcessingTimeMs,
		ModelVersion:     grpcResp.ModelVersion,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}

// predictWithRetry calls the ML service with retry logic
func (gs *GatewayServer) predictWithRetry(ctx context.Context, imageData []byte, width, height int32) (*pb.PredictionResponse, error) {
	var lastErr error

	for attempt := 0; attempt <= gs.maxRetries; attempt++ {
		if attempt > 0 {
			log.Printf("Retry attempt %d/%d", attempt, gs.maxRetries)
			time.Sleep(time.Duration(attempt*100) * time.Millisecond)
		}

		ctx, cancel := context.WithTimeout(ctx, gs.requestTimeout)
		defer cancel()

		resp, err := gs.predict(ctx, imageData, width, height)
		if err == nil {
			return resp, nil
		}

		lastErr = err
		log.Printf("Attempt %d failed: %v", attempt+1, err)
	}

	return nil, fmt.Errorf("prediction failed after %d retries: %w", gs.maxRetries+1, lastErr)
}

// predict calls the ML service once
func (gs *GatewayServer) predict(ctx context.Context, imageData []byte, width, height int32) (*pb.PredictionResponse, error) {
	gs.connLock.RLock()
	conn := gs.mlConn
	gs.connLock.RUnlock()

	if conn == nil {
		return nil, fmt.Errorf("ML service connection not available")
	}

	client := pb.NewMnistServiceClient(conn)
	req := &pb.PredictionRequest{
		ImageData:   imageData,
		ImageWidth:  width,
		ImageHeight: height,
	}
	return client.Predict(ctx, req)
}

// HealthHandler checks gateway and ML service health
func (gs *GatewayServer) HealthHandler(w http.ResponseWriter, r *http.Request) {
	gs.connLock.RLock()
	conn := gs.mlConn
	gs.connLock.RUnlock()

	if conn == nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]string{"status": "unhealthy", "reason": "ML service not connected"})
		return
	}

	// Check ML service health
	client := pb.NewMnistServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	resp, err := client.Health(ctx, &pb.HealthCheckRequest{})
	if err != nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]string{"status": "unhealthy", "reason": "ML service unreachable"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":        "healthy",
		"ml_service":    "serving",
		"model_version": resp.ModelVersion,
	})
}

// LivenessHandler for Kubernetes liveness probe
func (gs *GatewayServer) LivenessHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "alive"})
}

func main() {
	// Configuration from environment
	mlServiceAddr := os.Getenv("ML_SERVICE_ADDR")
	if mlServiceAddr == "" {
		mlServiceAddr = "localhost:50051"
	}

	gatewayPort := os.Getenv("GATEWAY_PORT")
	if gatewayPort == "" {
		gatewayPort = "8080"
	}

	requestTimeoutStr := os.Getenv("REQUEST_TIMEOUT_MS")
	requestTimeout := 5 * time.Second
	if requestTimeoutStr != "" {
		if ms, err := strconv.Atoi(requestTimeoutStr); err == nil {
			requestTimeout = time.Duration(ms) * time.Millisecond
		}
	}

	maxRetriesStr := os.Getenv("MAX_RETRIES")
	maxRetries := 2
	if maxRetriesStr != "" {
		if retries, err := strconv.Atoi(maxRetriesStr); err == nil {
			maxRetries = retries
		}
	}

	log.Printf("Starting gateway:")
	log.Printf("  ML Service: %s", mlServiceAddr)
	log.Printf("  Gateway Port: %s", gatewayPort)
	log.Printf("  Request Timeout: %s", requestTimeout)
	log.Printf("  Max Retries: %d", maxRetries)

	// Create gateway
	gateway := NewGatewayServer(mlServiceAddr, requestTimeout, maxRetries)

	// Connect to ML service
	if err := gateway.Connect(context.Background()); err != nil {
		log.Fatalf("Failed to connect to ML service: %v", err)
	}
	defer gateway.Close()

	// Register handlers
	http.HandleFunc("/health", gateway.HealthHandler)
	http.HandleFunc("/live", gateway.LivenessHandler)
	http.HandleFunc("/predict", gateway.PredictHandler)

	// Start server
	server := &http.Server{
		Addr:         ":" + gatewayPort,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	log.Printf("Gateway listening on %s", server.Addr)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v", err)
	}
}
