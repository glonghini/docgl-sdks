# docgl — Python SDK

Official Python SDK for the [Docgl](https://docgl.com) document generation API.

## Requirements

- Python **≥ 3.9**
- [`httpx`](https://www.python-httpx.org/) **≥ 0.27**

## Installation

```bash
pip install docgl
```

## Quick start (sync)

```python
from docgl import DocglClient, DocumentInput, GenerateRequest
import os

client = DocglClient(os.environ["DOCGL_API_TOKEN"])

response = client.generate(
    GenerateRequest(
        documents=[
            DocumentInput(
                uuid="your-template-uuid",
                filename="invoice-001.pdf",
                data=[
                    {
                        "customer_name": "Acme Corp",
                        "invoice_number": "INV-001",
                        "total": 1500,
                    }
                ],
            )
        ],
        # Optional: route output to your own storage bucket
        # storage_config_uuid="your-storage-config-uuid",
    )
)

print(response.queued)
# [QueuedJob(job_id='42', filename='invoice-001.pdf')]

status = client.get_status(response.queued[0].job_id)
print(status.status)  # "waiting" | "active" | "completed" | "failed"
```

## Quick start (async)

```python
import asyncio
import os
from docgl import AsyncDocglClient, DocumentInput, GenerateRequest

async def main():
    async with AsyncDocglClient(os.environ["DOCGL_API_TOKEN"]) as client:
        response = await client.generate(
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
        status = await client.get_status(response.queued[0].job_id)
        print(status.status)

asyncio.run(main())
```

## API

### `DocglClient(token, *, base_url?, timeout?)`

| Param | Type | Default | Description |
|---|---|---|---|
| `token` | `str` | — | Your Docgl API token |
| `base_url` | `str` | `https://api.docgl.com` | Override the API base URL |
| `timeout` | `float` | `30.0` | Request timeout in seconds |

### `client.generate(request)` → `GenerateResponse`

Queues one or more documents for PDF generation. Returns immediately (202).

### `client.get_status(job_id)` → `JobStatusResponse`

Returns the current status of a queued generation job.

#### Job status values

| Value | Description |
|---|---|
| `waiting` | In the queue, not yet started |
| `active` | Currently being processed |
| `completed` | PDF rendered successfully |
| `failed` | Generation failed — check `failed_reason` |
| `delayed` | Scheduled to run later |
| `unknown` | Job not found (may have been cleaned up) |

## Error handling

```python
from docgl import DocglClient, DocglError

try:
    client.generate(...)
except DocglError as e:
    print(e.status_code, e.body)
```
