"""
Supabase table schemas (reference only — tables are created via Supabase SQL editor).

Run the SQL in deploy/schema.sql to create these tables.
"""

# Table: clients
# id: uuid (PK, default gen_random_uuid())
# email: text (unique)
# access_code: text (unique) -- for code-gated access
# created_at: timestamptz (default now())
# plan: text (default 'free') -- 'free' | 'starter' | 'pro'

# Table: audits
# id: uuid (PK)
# client_id: uuid (FK -> clients.id, nullable for anonymous free audits)
# company_name: text
# geo_score: int
# breakdown: jsonb
# recommendations: jsonb (list of strings)
# website_url: text
# pdf_path: text (storage path)
# created_at: timestamptz (default now())

# Table: embeddings (for AI Inquiry Responder)
# id: uuid (PK)
# client_id: uuid (FK -> clients.id)
# content: text (original FAQ text chunk)
# embedding: vector(1536) (OpenAI text-embedding-3-small)
# metadata: jsonb (source filename, chunk index)
# created_at: timestamptz
