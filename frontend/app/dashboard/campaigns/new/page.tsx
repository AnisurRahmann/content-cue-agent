"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

interface Brand {
  id: string;
  name: string;
}

interface Product {
  id: string;
  name: string;
}

export default function NewCampaignPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [brief, setBrief] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [platforms, setPlatforms] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const platformOptions = [
    { id: "twitter", label: "Twitter/X", icon: "𝕏" },
    { id: "linkedin", label: "LinkedIn", icon: "in" },
    { id: "instagram", label: "Instagram", icon: "📷" },
    { id: "facebook", label: "Facebook", icon: "f" },
    { id: "tiktok", label: "TikTok", icon: "🎵" },
    { id: "blog", label: "Blog Post", icon: "📝" },
  ];

  useEffect(() => {
    loadBrands();
  }, []);

  useEffect(() => {
    if (selectedBrand) {
      loadProducts(selectedBrand);
    }
  }, [selectedBrand]);

  const loadBrands = async () => {
    const supabase = createClient();
    const { data } = await supabase.from("brands").select("id, name");
    if (data) setBrands(data);
  };

  const loadProducts = async (brandId: string) => {
    const supabase = createClient();
    const { data } = await supabase
      .from("products")
      .select("id, name")
      .eq("brand_id", brandId);
    if (data) setProducts(data);
  };

  const togglePlatform = (platformId: string) => {
    setPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((p) => p !== platformId)
        : [...prev, platformId]
    );
  };

  const toggleProduct = (productId: string) => {
    setSelectedProducts((prev) =>
      prev.includes(productId)
        ? prev.filter((p) => p !== productId)
        : [...prev, productId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!selectedBrand) throw new Error("Please select a brand");
      if (platforms.length === 0) throw new Error("Please select at least one platform");

      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) throw new Error("Not authenticated");

      const { data: campaign, error } = await supabase
        .from("campaigns")
        .insert({
          user_id: session.user.id,
          brand_id: selectedBrand,
          brief: JSON.stringify({
            brief,
            target_audience: targetAudience,
            platforms,
            product_ids: selectedProducts,
          }),
          status: "generating",
        })
        .select()
        .single();

      if (error) throw error;

      // Call backend API to start LangGraph workflow
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/campaigns`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          campaign_id: campaign.id,
          brief: {
            brief,
            target_audience: targetAudience,
            platforms,
            product_ids: selectedProducts,
          },
        }),
      });

      if (!response.ok) throw new Error("Failed to start campaign generation");

      router.push(`/dashboard/campaigns/${campaign.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create campaign");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard/campaigns"
          className="p-2 hover:bg-slate-800 rounded-lg transition-all"
        >
          <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">New Campaign</h1>
          <p className="text-slate-400">Create an AI-powered marketing campaign</p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Brand Selection */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">1. Select Brand</CardTitle>
            <CardDescription>Choose the brand for this campaign</CardDescription>
          </CardHeader>
          <CardContent>
            <select
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
              required
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="">Select a brand...</option>
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.name}
                </option>
              ))}
            </select>
          </CardContent>
        </Card>

        {/* Products */}
        {products.length > 0 && (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">2. Select Products</CardTitle>
              <CardDescription>Choose products to feature (optional)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {products.map((product) => (
                  <button
                    key={product.id}
                    type="button"
                    onClick={() => toggleProduct(product.id)}
                    className={`p-4 rounded-lg border transition-all text-left ${
                      selectedProducts.includes(product.id)
                        ? "bg-blue-500/10 border-blue-500 text-blue-400"
                        : "bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-600"
                    }`}
                  >
                    <span className="font-medium">{product.name}</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Campaign Brief */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">3. Campaign Brief</CardTitle>
            <CardDescription>Describe what you want to promote</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label htmlFor="brief" className="block text-sm font-medium text-slate-300 mb-2">
                Brief *
              </label>
              <textarea
                id="brief"
                value={brief}
                onChange={(e) => setBrief(e.target.value)}
                required
                rows={4}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                placeholder="e.g., Launch our new AI-powered marketing tool targeting small business owners..."
              />
            </div>

            <div>
              <label htmlFor="targetAudience" className="block text-sm font-medium text-slate-300 mb-2">
                Target Audience
              </label>
              <textarea
                id="targetAudience"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                rows={2}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                placeholder="e.g., Small business owners, marketing professionals, aged 25-45..."
              />
            </div>
          </CardContent>
        </Card>

        {/* Platforms */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">4. Select Platforms</CardTitle>
            <CardDescription>Choose where to publish content</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {platformOptions.map((platform) => (
                <button
                  key={platform.id}
                  type="button"
                  onClick={() => togglePlatform(platform.id)}
                  className={`p-4 rounded-lg border transition-all ${
                    platforms.includes(platform.id)
                      ? "bg-blue-500/10 border-blue-500 text-blue-400"
                      : "bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  <div className="text-2xl mb-2">{platform.icon}</div>
                  <div className="font-medium">{platform.label}</div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 text-white font-medium rounded-lg transition-all"
          >
            {loading ? "Creating Campaign..." : "Generate Campaign"}
          </button>
          <Link
            href="/dashboard/campaigns"
            className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-lg border border-slate-700 transition-all"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
