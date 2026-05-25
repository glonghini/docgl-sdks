// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------

/** A single cell value inside a table row */
export type TableRow = Record<string, string | number>;

/** All allowed values for a document variable */
export type VariableValue = string | number | TableRow[];

/** Key-value map of variables for one document render */
export type DocumentVariables = Record<string, VariableValue>;

/** A single document to be rendered */
export interface DocumentInput {
  /** UUID of the template registered in Docgl */
  uuid: string;
  /** Output filename (e.g. "invoice-001.pdf") */
  filename: string;
  /**
   * Array of variable maps. Each entry produces one rendered PDF.
   * Provide multiple entries to batch-render the same template with
   * different data in a single request.
   */
  data: DocumentVariables[];
}

/** Body sent to POST /api/generate */
export interface GenerateRequest {
  documents: DocumentInput[];
  /**
   * UUID of a storage configuration registered in Docgl.
   * When provided, the generated PDF is uploaded to your storage bucket.
   */
  storageConfigUuid?: string;
}

// ---------------------------------------------------------------------------
// Response types
// ---------------------------------------------------------------------------

/** A successfully queued job entry */
export interface QueuedJob {
  jobId: string;
  filename: string;
}

/** A document that failed validation */
export interface ValidationError {
  filename: string;
  errors: string[];
}

/** Response from POST /api/generate (HTTP 202) */
export interface GenerateResponse {
  message: string;
  queued: QueuedJob[];
  errors?: ValidationError[];
}

/** Possible states of a generation job */
export type JobStatus =
  | "waiting"
  | "active"
  | "completed"
  | "failed"
  | "delayed"
  | "unknown";

/** Response from GET /api/generate/:jobId (HTTP 200) */
export interface JobStatusResponse {
  jobId: string;
  filename: string | null;
  status: JobStatus;
  result: unknown | null;
  failedReason: string | null;
}
