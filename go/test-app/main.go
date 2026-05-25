package main

import (
	"context"
	"fmt"
	"log"
	"os"

	docgl "github.com/docgl/sdk-go"
)

func main() {
	token := os.Getenv("DOCGL_API_TOKEN")
	if token == "" {
		token = "your-api-token"
	}

	client := docgl.NewClient(token, nil)
	ctx := context.Background()

	// 1. Queue a document for generation
	resp, err := client.Generate(ctx, &docgl.GenerateRequest{
		Documents: []docgl.DocumentInput{
			{
				UUID:     "7646347b-6e35-4966-a4c7-ee156e1fe86a",
				Filename: "test-sdk-go",
				Data: []docgl.DocumentVariables{
					{"myVariable": "Acme Corp"},
				},
			},
		},
	})
	if err != nil {
		log.Fatal("generate error:", err)
	}

	fmt.Println("Queued jobs:", resp.Queued)
	if len(resp.Errors) > 0 {
		fmt.Println("Validation errors:", resp.Errors)
	}

	// 2. Poll status for the first queued job
	if len(resp.Queued) > 0 {
		status, err := client.GetStatus(ctx, resp.Queued[0].JobID)
		if err != nil {
			log.Fatal("get status error:", err)
		}
		fmt.Println("Job status:", status.Status)
	}
}
