import { DocglClient } from "../src";

const client = new DocglClient(process.env.DOCGL_API_TOKEN ?? "your-api-token");

async function main() {
  // 1. Queue a document for generation
  const { queued, errors } = await client.generate({
    documents: [
      {
        uuid: "your-template-uuid",
        filename: "invoice.pdf",
        data: [{ customer_name: "Acme Corp", total: 1500 }],
      },
    ],
  });

  console.log("Queued jobs:", queued);
  if (errors?.length) console.warn("Validation errors:", errors);

  // 2. Poll status for the first queued job
  if (queued.length > 0) {
    const status = await client.getStatus(queued[0].jobId);
    console.log("Job status:", status.status);
  }
}

main().catch(console.error);
