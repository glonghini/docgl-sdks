# @docgl/sdk — TypeScript / JavaScript SDK

Official TypeScript SDK for the [Docgl](https://docgl.com) document generation API.

## Requirements

- Node.js **≥ 18** (uses the built-in `fetch` API)
- TypeScript **≥ 5** (optional but recommended)

## Installation

```bash
npm install @docgl/sdk
# or
yarn add @docgl/sdk
# or
pnpm add @docgl/sdk
```

## Quick start

```ts
import { DocglClient } from "@docgl/sdk";

const docgl = new DocglClient(process.env.DOCGL_API_TOKEN!);

// 1. Queue document generation
const { queued, errors } = await docgl.generate({
  documents: [
    {
      uuid: "your-template-uuid",
      filename: "invoice-001.pdf",
      data: [
        {
          customer_name: "Acme Corp",
          invoice_number: "INV-001",
          total: 1500,
        },
      ],
    },
  ],
  // Optional: route output to your own storage bucket
  // storageConfigUuid: "your-storage-config-uuid",
});

console.log("Queued:", queued);
// [{ jobId: "42", filename: "invoice-001.pdf" }]

// 2. Poll for status
const status = await docgl.getStatus(queued[0].jobId);
console.log(status.status); // "waiting" | "active" | "completed" | "failed"
```

## API

### `new DocglClient(token, options?)`

| Param | Type | Description |
|---|---|---|
| `token` | `string` | Your Docgl API token |
| `options.baseUrl` | `string` | Override the API base URL (default: `https://api.docgl.com`) |

### `client.generate(request)`

Queues one or more documents for PDF generation. Returns `202 Accepted` immediately.

**Returns:** `Promise<GenerateResponse>`

### `client.getStatus(jobId)`

Returns the current status of a queued generation job.

**Returns:** `Promise<JobStatusResponse>`

#### Job status values

| Value | Description |
|---|---|
| `waiting` | In the queue, not yet started |
| `active` | Currently being processed |
| `completed` | PDF rendered successfully |
| `failed` | Generation failed — check `failedReason` |
| `delayed` | Scheduled to run later |
| `unknown` | Job not found (may have been cleaned up) |

## Error handling

```ts
import { DocglClient, DocglError } from "@docgl/sdk";

try {
  await docgl.generate({ documents: [] });
} catch (err) {
  if (err instanceof DocglError) {
    console.error(err.status, err.body);
  }
}
```
