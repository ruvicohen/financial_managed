# Document Worker

Not implemented yet. This will become the asynchronous worker that consumes a
job queue (Redis-backed, per the master plan) to run OCR, extraction, and
embedding jobs for uploaded financial documents without blocking HTTP
requests.

See `docs/family_financial_platform_master_plan.md` sections 18-20 for the
target document processing pipeline. Introduced starting Phase 6 (Document
Infrastructure).
