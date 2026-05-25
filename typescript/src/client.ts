import type {
  GenerateRequest,
  GenerateResponse,
  JobStatusResponse,
} from "./types";

/** Options accepted by the DocglClient constructor */
export interface DocglClientOptions {
  /**
   * Override the default API base URL.
   * @default "https://api.docgl.com"
   */
  baseUrl?: string;
}

/** Error thrown when the Docgl API returns a non-2xx response */
export class DocglError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown
  ) {
    super(`Docgl API error ${status}: ${JSON.stringify(body)}`);
    this.name = "DocglError";
  }
}

/**
 * Official Docgl API client.
 *
 * @example
 * ```ts
 * const docgl = new DocglClient("your-api-token");
 *
 * const { queued } = await docgl.generate({
 *   documents: [{
 *     uuid: "template-uuid",
 *     filename: "invoice.pdf",
 *     data: [{ customer_name: "Acme Corp", total: 1500 }],
 *   }],
 * });
 *
 * const status = await docgl.getStatus(queued[0].jobId);
 * console.log(status.status); // "completed"
 * ```
 */
export class DocglClient {
  private readonly baseUrl: string;
  private readonly token: string;

  constructor(token: string, options: DocglClientOptions = {}) {
    if (!token) throw new Error("Docgl API token is required");
    this.token = token;
    this.baseUrl = (options.baseUrl ?? "https://api.docgl.com").replace(/\/$/, "");
  }

  private get authHeaders(): Record<string, string> {
    return {
      Authorization: `Bearer ${this.token}`,
    };
  }

  private async handleResponse<T>(res: Response): Promise<T> {
    if (res.ok) {
      return res.json() as Promise<T>;
    }
    const body = await res.json().catch(() => ({ message: res.statusText }));
    throw new DocglError(res.status, body);
  }

  /**
   * Queue one or more documents for generation.
   *
   * The API returns immediately with HTTP 202. Use {@link getStatus} to poll
   * each `jobId` until `status` is `"completed"` or `"failed"`.
   */
  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    const res = await fetch(`${this.baseUrl}/api/generate`, {
      method: "POST",
      headers: {
        ...this.authHeaders,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
    return this.handleResponse<GenerateResponse>(res);
  }

  /**
   * Poll the status of a previously queued generation job.
   *
   * @param jobId - The `jobId` returned by {@link generate}
   */
  async getStatus(jobId: string): Promise<JobStatusResponse> {
    const res = await fetch(
      `${this.baseUrl}/api/generate/${encodeURIComponent(jobId)}`,
      { headers: this.authHeaders }
    );
    return this.handleResponse<JobStatusResponse>(res);
  }
}
