# docgl-go — Go SDK

Official Go client for the [Docgl](https://docgl.com) document generation API.

## Requirements

- Go **≥ 1.21**
- No external dependencies — uses only the standard library

## Installation

```bash
go get github.com/docgl/sdk-go
```

## Quick start

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/docgl/sdk-go"
)

func main() {
    client := docgl.NewClient("your-api-token", nil)

    resp, err := client.Generate(context.Background(), &docgl.GenerateRequest{
        Documents: []docgl.DocumentInput{
            {
                UUID:     "your-template-uuid",
                Filename: "invoice-001.pdf",
                Data: []docgl.DocumentVariables{
                    {
                        "customer_name":   "Acme Corp",
                        "invoice_number":  "INV-001",
                        "total":           1500,
                    },
                },
            },
        },
        // Optional: route output to your own storage bucket
        // StorageConfigUUID: "your-storage-config-uuid",
    })
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println("Queued:", resp.Queued)
    // [{JobID:42 Filename:invoice-001.pdf}]

    status, err := client.GetStatus(context.Background(), resp.Queued[0].JobID)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Status:", status.Status) // "waiting" | "active" | "completed" | "failed"
}
```

## API

### `docgl.NewClient(token string, opts *ClientOptions) *Client`

| Field | Type | Default | Description |
|---|---|---|---|
| `token` | `string` | — | Your Docgl API token |
| `opts.HTTPClient` | `*http.Client` | 30s timeout | Custom HTTP client |

### `client.Generate(ctx, *GenerateRequest) (*GenerateResponse, error)`

Queues one or more documents for PDF generation. Returns immediately (HTTP 202).

### `client.GetStatus(ctx, jobID string) (*JobStatusResponse, error)`

Returns the current status of a queued generation job.

#### Job status values

| Value | Description |
|---|---|
| `waiting` | In the queue, not yet started |
| `active` | Currently being processed |
| `completed` | PDF rendered successfully |
| `failed` | Generation failed — check `FailedReason` |
| `delayed` | Scheduled to run later |
| `unknown` | Job not found (may have been cleaned up) |

## Error handling

```go
status, err := client.GetStatus(ctx, "42")
if err != nil {
    var apiErr *docgl.APIError
    if errors.As(err, &apiErr) {
        fmt.Println(apiErr.StatusCode, apiErr.Body)
    }
    log.Fatal(err)
}
```
