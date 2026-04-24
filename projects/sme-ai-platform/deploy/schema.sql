-- SME AI Platform — Supabase Schema
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor)

-- Enable pgvector extension
create extension if not exists vector;

-- Clients table
create table if not exists clients (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  access_code text unique,
  plan text default 'free',  -- 'free' | 'starter' | 'pro'
  created_at timestamptz default now()
);

-- Audits table
create table if not exists audits (
  id uuid primary key default gen_random_uuid(),
  client_id uuid references clients(id) on delete set null,
  company_name text not null,
  geo_score int,
  breakdown jsonb,
  recommendations jsonb,
  website_url text,
  pdf_path text,
  created_at timestamptz default now()
);

-- Embeddings table (for AI Inquiry Responder)
create table if not exists embeddings (
  id uuid primary key default gen_random_uuid(),
  client_id uuid references clients(id) on delete cascade,
  content text not null,
  embedding vector(1536),
  metadata jsonb,
  created_at timestamptz default now()
);

-- Index for fast vector search
create index if not exists embeddings_vector_idx
  on embeddings using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Row Level Security (enable after testing)
-- alter table audits enable row level security;
-- alter table embeddings enable row level security;
