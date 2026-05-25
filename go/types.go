// Package docgl provides types for the Docgl document generation API.
package docgl

// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------

// TableRow represents a single row inside a table variable.
type TableRow map[string]interface{}

// DocumentVariables is a key/value map of variables for one document render.
// Values may be strings, numbers, or slices of TableRow.
type DocumentVariables map[string]interface{}

// DocumentInput describes a single document to be rendered.
type DocumentInput struct {
	// UUID is the template UUID registered in Docgl.
	UUID string `json:"uuid"`

	// Filename is the output filename, e.g. "invoice-001.pdf".
	Filename string `json:"filename"`

	// Data is a list of variable maps. Each entry produces one PDF.
	// Provide multiple entries to batch-render the same template with
	// different data in a single request.
	Data []DocumentVariables `json:"data"`
}

// GenerateRequest is the body sent to POST /api/generate.
type GenerateRequest struct {
	Documents []DocumentInput `json:"documents"`

	// StorageConfigUUID is an optional UUID of a storage configuration
	// registered in Docgl. When set, the generated PDF is uploaded to
	// your configured storage bucket.
	StorageConfigUUID string `json:"storageConfigUuid,omitempty"`
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

// QueuedJob represents a successfully queued generation job.
type QueuedJob struct {
	JobID    string `json:"jobId"`
	Filename string `json:"filename"`
}

// ValidationError describes a document that failed validation.
type ValidationError struct {
	Filename string   `json:"filename"`
	Errors   []string `json:"errors"`
}

// GenerateResponse is returned by POST /api/generate (HTTP 202).
type GenerateResponse struct {
	Message string            `json:"message"`
	Queued  []QueuedJob       `json:"queued"`
	Errors  []ValidationError `json:"errors,omitempty"`
}

// JobStatusResponse is returned by GET /api/generate/:jobId (HTTP 200).
type JobStatusResponse struct {
	JobID    string  `json:"jobId"`
	Filename *string `json:"filename"`
	// Status is one of: waiting, active, completed, failed, delayed, unknown.
	Status       string      `json:"status"`
	Result       interface{} `json:"result"`
	FailedReason *string     `json:"failedReason"`
}
