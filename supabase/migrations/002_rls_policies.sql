-- CampaignCraft AI - Row Level Security Policies
-- Migration: 002_rls_policies.sql

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_pieces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_connections ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USERS TABLE POLICIES
-- ============================================================================
-- Users can read their own profile
CREATE POLICY "Users can view own profile"
  ON public.users FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON public.users FOR UPDATE
  USING (auth.uid() = id);

-- Service role can insert users (trigger only)
CREATE POLICY "Service role can insert users"
  ON public.users FOR INSERT
  WITH CHECK (true);

-- ============================================================================
-- BRANDS TABLE POLICIES
-- ============================================================================
-- Users can view their own brands
CREATE POLICY "Users can view own brands"
  ON public.brands FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own brands
CREATE POLICY "Users can insert own brands"
  ON public.brands FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own brands
CREATE POLICY "Users can update own brands"
  ON public.brands FOR UPDATE
  USING (auth.uid() = user_id);

-- Users can delete their own brands
CREATE POLICY "Users can delete own brands"
  ON public.brands FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- PRODUCTS TABLE POLICIES
-- ============================================================================
-- Users can view products from their brands (via brands table)
CREATE POLICY "Users can view own brand products"
  ON public.products FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.brands
      WHERE brands.id = products.brand_id
      AND brands.user_id = auth.uid()
    )
  );

-- Users can insert products for their brands
CREATE POLICY "Users can insert products for own brands"
  ON public.products FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.brands
      WHERE brands.id = products.brand_id
      AND brands.user_id = auth.uid()
    )
  );

-- Users can update products for their brands
CREATE POLICY "Users can update products for own brands"
  ON public.products FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.brands
      WHERE brands.id = products.brand_id
      AND brands.user_id = auth.uid()
    )
  );

-- Users can delete products for their brands
CREATE POLICY "Users can delete products for own brands"
  ON public.products FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.brands
      WHERE brands.id = products.brand_id
      AND brands.user_id = auth.uid()
    )
  );

-- ============================================================================
-- CAMPAIGNS TABLE POLICIES
-- ============================================================================
-- Users can view their own campaigns
CREATE POLICY "Users can view own campaigns"
  ON public.campaigns FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert campaigns for their brands
CREATE POLICY "Users can insert campaigns for own brands"
  ON public.campaigns FOR INSERT
  WITH CHECK (
    auth.uid() = user_id
    AND EXISTS (
      SELECT 1 FROM public.brands
      WHERE brands.id = campaigns.brand_id
      AND brands.user_id = auth.uid()
    )
  );

-- Users can update their own campaigns
CREATE POLICY "Users can update own campaigns"
  ON public.campaigns FOR UPDATE
  USING (auth.uid() = user_id);

-- Users can delete their own campaigns
CREATE POLICY "Users can delete own campaigns"
  ON public.campaigns FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- CONTENT PIECES TABLE POLICIES
-- ============================================================================
-- Users can view content pieces from their campaigns
CREATE POLICY "Users can view own campaign content"
  ON public.content_pieces FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = content_pieces.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

-- Users can insert content pieces for their campaigns
CREATE POLICY "Users can insert content for own campaigns"
  ON public.content_pieces FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = content_pieces.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

-- Users can update content pieces for their campaigns
CREATE POLICY "Users can update content for own campaigns"
  ON public.content_pieces FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = content_pieces.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

-- Users can delete content pieces for their campaigns
CREATE POLICY "Users can delete content for own campaigns"
  ON public.content_pieces FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.campaigns
      WHERE campaigns.id = content_pieces.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

-- ============================================================================
-- SOCIAL CONNECTIONS TABLE POLICIES
-- ============================================================================
-- Users can view their own social connections
CREATE POLICY "Users can view own social connections"
  ON public.social_connections FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own social connections
CREATE POLICY "Users can insert own social connections"
  ON public.social_connections FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own social connections
CREATE POLICY "Users can update own social connections"
  ON public.social_connections FOR UPDATE
  USING (auth.uid() = user_id);

-- Users can delete their own social connections
CREATE POLICY "Users can delete own social connections"
  ON public.social_connections FOR DELETE
  USING (auth.uid() = user_id);
