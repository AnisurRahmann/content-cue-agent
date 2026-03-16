-- CampaignCraft AI - Auth Trigger
-- Migration: 003_auth_trigger.sql

-- This trigger automatically creates a user profile in public.users
-- when a new user signs up through Supabase Auth

-- ============================================================================
-- FUNCTION: Handle new user signup
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- TRIGGER: Auto-create user profile on signup
-- ============================================================================
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
-- Grant usage on schemas
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT USAGE ON SCHEMA auth TO anon, authenticated;

-- Grant select on tables for anon (public access)
GRANT SELECT ON TABLE public.users TO anon;
GRANT SELECT ON TABLE public.brands TO anon;
GRANT SELECT ON TABLE public.products TO anon;
GRANT SELECT ON TABLE public.campaigns TO anon;
GRANT SELECT ON TABLE public.content_pieces TO anon;

-- Grant full permissions on tables for authenticated users
GRANT ALL ON TABLE public.users TO authenticated;
GRANT ALL ON TABLE public.brands TO authenticated;
GRANT ALL ON TABLE public.products TO authenticated;
GRANT ALL ON TABLE public.campaigns TO authenticated;
GRANT ALL ON TABLE public.content_pieces TO authenticated;
GRANT ALL ON TABLE public.social_connections TO authenticated;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
