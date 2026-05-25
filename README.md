# docgl-sdks

Official SDK monorepo for the [Docgl](https://docgl.com) document generation API.

## SDKs

| Language | Directory | Package / Registry |
|---|---|---|
| TypeScript / JavaScript | [`typescript/`](./typescript) | npm: `@docgl/sdk` |
| Python | [`python/`](./python) | PyPI: `docgl` |
| Go | [`go/`](./go) | `github.com/docgl/sdk-go` |

## Available methods

All SDKs expose the same two core methods:

| Method | Endpoint | Description |
|---|---|---|
| `generate` | `POST /api/generate` | Queue one or more documents for PDF generation |
| `getStatus` / `get_status` / `GetStatus` | `GET /api/generate/:jobId` | Poll the status of a queued generation job |

## Authentication

All SDKs use a **Bearer API token** passed to the client constructor. Create tokens under **Account → API Tokens** in the Docgl dashboard.

## Quickstart per language

### TypeScript

```ts
import { DocglClient } from "@docgl/sdk";

const docgl = new DocglClient(process.env.DOCGL_API_TOKEN!);
const { queued } = await docgl.generate({ documents: [{ uuid: "...", filename: "out.pdf", data: [{ name: "Alice" }] }] });
const status = await docgl.getStatus(queued[0].jobId);
```

### Python

```python
from docgl import DocglClient, DocumentInput, GenerateRequest

client = DocglClient("your-token")
response = client.generate(GenerateRequest(documents=[DocumentInput(uuid="...", filename="out.pdf", data=[{"name": "Alice"}])]))
status = client.get_status(response.queued[0].job_id)
```

### Go

```go
client := docgl.NewClient("your-token", nil)
resp, _ := client.Generate(ctx, &docgl.GenerateRequest{Documents: []docgl.DocumentInput{{UUID: "...", Filename: "out.pdf", Data: []docgl.DocumentVariables{{"name": "Alice"}}}}})
status, _ := client.GetStatus(ctx, resp.Queued[0].JobID)
```

## API reference

See the [Docgl API docs](https://docgl.com/docs/api/generate) for the full endpoint reference.
