import os
from docgl import DocglClient, DocumentInput, GenerateRequest

def main():
    client = DocglClient(os.environ.get("DOCGL_API_TOKEN", "your-api-token"))

    # 1. Queue a document for generation
    response = client.generate(
        GenerateRequest(
            documents=[
                DocumentInput(
                    uuid="your-template-uuid",
                    filename="invoice.pdf",
                    data=[{"customer_name": "Acme Corp", "total": 1500}],
                )
            ]
        )
    )

    print("Queued jobs:", response.queued)
    if response.errors:
        print("Validation errors:", response.errors)

    # 2. Poll status for the first queued job
    if response.queued:
        status = client.get_status(response.queued[0].job_id)
        print("Job status:", status.status)

if __name__ == "__main__":
    main()
