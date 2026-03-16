-- CampaignCraft AI - Initial Schema
-- Migration: 001_initial_schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS (extends Supabase auth.users)
-- ============================================================================
CREATE TABLE public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- BRANDS
-- ============================================================================
CREATE TABLE public.brands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  brand_type TEXT NOT NULL CHECK (brand_type IN ('business', 'personal')),
  description TEXT,
  industry TEXT,
  voice_tone TEXT DEFAULT 'casual',
  voice_description TEXT,
  languages TEXT[] DEFAULT '{en}',
  primary_language TEXT DEFAULT 'en',
  brand_colors JSONB,
  logo_url TEXT,
  guidelines_text TEXT,
  target_audiences JSONB,
  default_platforms TEXT[] DEFAULT '{facebook,instagram,linkedin}',
  whatsapp_number TEXT,
  website_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- PRODUCTS
-- ============================================================================
CREATE TABLE public.products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES public.brands(id) ON DELETE CASCADE NOT NULL,
  slug TEXT NOT NULL,
  name TEXT NOT NULL,
  category TEXT,
  price DECIMAL(10,2),
  price_currency TEXT DEFAULT 'BDT',
  original_price DECIMAL(10,2),
  original_currency TEXT DEFAULT 'USD',
  duration TEXT,
  description TEXT,
  features TEXT[],
  target_audience TEXT,
  activation_steps TEXT[],
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(brand_id, slug)
);

-- ============================================================================
-- CAMPAIGNS
-- ============================================================================
CREATE TABLE public.campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  brand_id UUID REFERENCES public.brands(id) ON DELETE CASCADE NOT NULL,
  title TEXT,
  brief TEXT NOT NULL,
  campaign_type TEXT,
  target_audience TEXT,
  tone TEXT,
  platforms TEXT[] NOT NULL,
  status TEXT DEFAULT 'generating' CHECK (status IN ('generating','review','approved','published','failed')),
  current_phase TEXT DEFAULT 'planning',
  langgraph_thread_id TEXT,
  execution_plan JSONB,
  retry_count INT DEFAULT 0,
  total_cost_usd DECIMAL(10,6) DEFAULT 0,
  cost_breakdown JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  published_at TIMESTAMPTZ
);

-- ============================================================================
-- CONTENT PIECES
-- ============================================================================
CREATE TABLE public.content_pieces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID REFERENCES public.campaigns(id) ON DELETE CASCADE NOT NULL,
  platform TEXT NOT NULL,
  content_type TEXT NOT NULL,
  copy TEXT NOT NULL,
  hashtags TEXT[],
  image_urls TEXT[],
  image_prompts TEXT[],
  video_url TEXT,
  cta_link TEXT,
  metadata JSONB,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft','review','approved','rejected','published')),
  feedback TEXT,
  llm_tier_used TEXT,
  published_at TIMESTAMPTZ,
  platform_post_id TEXT,
  publish_error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- SOCIAL CONNECTIONS
-- ============================================================================
CREATE TABLE public.social_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  brand_id UUID REFERENCES public.brands(id) ON DELETE CASCADE NOT NULL,
  platform TEXT NOT NULL,
  platform_id TEXT NOT NULL,
  platform_name TEXT,
  access_token TEXT NOT NULL,
  refresh_token TEXT,
  token_expires_at TIMESTAMPTZ,
  scopes TEXT[],
  is_active BOOLEAN DEFAULT true,
  connected_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(brand_id, platform, platform_id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_brands_user_id ON public.brands(user_id);
CREATE INDEX idx_products_brand_id ON public.products(brand_id);
CREATE INDEX idx_campaigns_user_id ON public.campaigns(user_id);
CREATE INDEX idx_campaigns_brand_id ON public.campaigns(brand_id);
CREATE INDEX idx_campaigns_status ON public.campaigns(status);
CREATE INDEX idx_content_pieces_campaign_id ON public.content_pieces(campaign_id);
CREATE INDEX idx_social_connections_user_id ON public.social_connections(user_id);
CREATE INDEX idx_social_connections_brand_id ON public.social_connections(brand_id);

-- ============================================================================
-- UPDATED AT TRIGGERS
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_brands_updated_at BEFORE UPDATE ON public.brands
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON public.campaigns
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_pieces_updated_at BEFORE UPDATE ON public.content_pieces
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
