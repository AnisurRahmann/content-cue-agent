import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = 'force-dynamic';

export default async function BrandDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { data: brand } = await supabase
    .from("brands")
    .select("*")
    .eq("id", params.id)
    .eq("user_id", user?.id)
    .single();

  if (!brand) {
    notFound();
  }

  const { data: products } = await supabase
    .from("products")
    .select("*")
    .eq("brand_id", params.id)
    .order("created_at", { ascending: false });

  const { data: campaigns } = await supabase
    .from("campaigns")
    .select("id, brief, status, created_at")
    .eq("brand_id", params.id)
    .order("created_at", { ascending: false })
    .limit(5);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link
            href="/dashboard/brands"
            className="p-2 hover:bg-slate-800 rounded-lg transition-all"
          >
            <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          {brand.logo_url ? (
            <img
              src={brand.logo_url}
              alt={brand.name}
              className="w-20 h-20 rounded-xl object-cover"
            />
          ) : (
            <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-3xl font-bold">
              {brand.name.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">{brand.name}</h1>
            {brand.website && (
              <a
                href={brand.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 text-sm"
              >
                {brand.website}
              </a>
            )}
          </div>
        </div>
        <Link
          href={`/dashboard/brands/${brand.id}/edit`}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded-lg border border-slate-700 transition-all"
        >
          Edit Brand
        </Link>
      </div>

      {/* Description */}
      {brand.description && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">About</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400">{brand.description}</p>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Products */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white">Products</CardTitle>
                <CardDescription>{products?.length || 0} products</CardDescription>
              </div>
              <Link
                href={`/dashboard/brands/${brand.id}/products/new`}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-all"
              >
                Add Product
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {products && products.length > 0 ? (
              <div className="space-y-3">
                {products.map((product) => (
                  <Link
                    key={product.id}
                    href={`/dashboard/products/${product.id}`}
                    className="block p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-blue-500/50 transition-all"
                  >
                    <h4 className="text-white font-medium">{product.name}</h4>
                    <p className="text-sm text-slate-500 mt-1 line-clamp-1">
                      {product.description}
                    </p>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-500 text-sm">No products yet</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Campaigns */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white">Recent Campaigns</CardTitle>
                <CardDescription>Last 5 campaigns</CardDescription>
              </div>
              <Link
                href="/dashboard/campaigns"
                className="text-blue-400 hover:text-blue-300 text-sm font-medium"
              >
                View All
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {campaigns && campaigns.length > 0 ? (
              <div className="space-y-3">
                {campaigns.map((campaign: any) => (
                  <Link
                    key={campaign.id}
                    href={`/dashboard/campaigns/${campaign.id}`}
                    className="block p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-blue-500/50 transition-all"
                  >
                    <h4 className="text-white font-medium line-clamp-1">
                      {campaign.brief}
                    </h4>
                    <div className="flex items-center gap-2 mt-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          campaign.status === "published"
                            ? "bg-green-500/10 text-green-400 border border-green-500/20"
                            : campaign.status === "review"
                            ? "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20"
                            : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                        }`}
                      >
                        {campaign.status}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-500 text-sm">No campaigns yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
