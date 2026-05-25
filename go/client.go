// Package docgl provides an official Go client for the Docgl document
// generation API.
//
// Example:
//
//	client := docgl.NewClient("your-api-token", nil)
//
//	resp, err := client.Generate(context.Background(), &docgl.GenerateRequest{
//	    Documents: []docgl.DocumentInput{
//	        {
//	            UUID:     "template-uuid",
//	            Filename: "invoice.pdf",
//	            Data: []docgl.DocumentVariables{
//	                {"customer_name": "Acme Corp", "total": 1500},
//	            },
//	        },
//	    },
//	})
//	if err != nil {
//	    log.Fatal(err)
//	}
//
//	status, err := client.GetStatus(context.Background(), resp.Queued[0].JobID)
package docgl

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const defaultBaseURL = "https://api.docgl.com"

// ClientOptions allows customising the DocglClient.
type ClientOptions struct {
	// HTTPClient is the underlying HTTP client to use.
	// When nil, a client with a 30-second timeout is used.
	HTTPClient *http.Client
}

// APIError is returned when the Docgl API responds with a non-2xx status.
type APIError struct {
	StatusCode int
	Body       string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("docgl: API error %d: %s", e.StatusCode, e.Body)
}

// Client is the Docgl API client.
type Client struct {
	baseURL    string
	token      string
	httpClient *http.Client
}

// NewClient creates a new DocglClient.
//
//   - token: your Docgl API token (required)
//   - opts: optional configuration; pass nil to use defaults
func NewClient(token string, opts *ClientOptions) *Client {
	if token == "" {
		panic("docgl: API token is required")
	}

	httpClient := &http.Client{Timeout: 30 * time.Second}

	if opts != nil && opts.HTTPClient != nil {
		httpClient = opts.HTTPClient
	}

	return &Client{
		baseURL:    defaultBaseURL,
		token:      token,
		httpClient: httpClient,
	}
}

func (c *Client) newRequest(ctx context.Context, method, path string, body interface{}) (*http.Request, error) {
	var buf bytes.Buffer
	if body != nil {
		if err := json.NewEncoder(&buf).Encode(body); err != nil {
			return nil, fmt.Errorf("docgl: failed to encode request body: %w", err)
		}
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, &buf)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	return req, nil
}

func (c *Client) do(req *http.Request, out interface{}) error {
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("docgl: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		var buf bytes.Buffer
		buf.ReadFrom(resp.Body)
		return &APIError{StatusCode: resp.StatusCode, Body: buf.String()}
	}

	if out != nil {
		if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
			return fmt.Errorf("docgl: failed to decode response: %w", err)
		}
	}

	return nil
}

// Generate queues one or more documents for PDF generation.
//
// The API responds immediately (HTTP 202). Use [Client.GetStatus] to poll
// each JobID until the status is "completed" or "failed".
func (c *Client) Generate(ctx context.Context, req *GenerateRequest) (*GenerateResponse, error) {
	httpReq, err := c.newRequest(ctx, http.MethodPost, "/api/generate", req)
	if err != nil {
		return nil, err
	}

	var resp GenerateResponse
	if err := c.do(httpReq, &resp); err != nil {
		return nil, err
	}

	return &resp, nil
}

// GetStatus returns the current status of a previously queued generation job.
//
//   - jobID: the JobID returned by [Client.Generate]
func (c *Client) GetStatus(ctx context.Context, jobID string) (*JobStatusResponse, error) {
	httpReq, err := c.newRequest(ctx, http.MethodGet, "/api/generate/"+jobID, nil)
	if err != nil {
		return nil, err
	}

	var resp JobStatusResponse
	if err := c.do(httpReq, &resp); err != nil {
		return nil, err
	}

	return &resp, nil
}
