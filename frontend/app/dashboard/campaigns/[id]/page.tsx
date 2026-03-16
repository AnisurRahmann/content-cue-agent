import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = 'force-dynamic';

export default async function CampaignDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { data: campaign } = await supabase
    .from("campaigns")
    .select(
      `
      *,
      brands(name, logo_url),
      content_pieces(*)
    `
    )
    .eq("id", params.id)
    .eq("user_id", user?.id)
    .single();

  if (!campaign) {
    notFound();
  }

  const brief = JSON.parse(campaign.brief);
  const costBreakdown = campaign.cost_breakdown || {};

  const getStatusColor = (status: string) => {
    switch (status) {
      case "published":
        return "bg-green-500/10 text-green-400 border-green-500/20";
      case "review":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20";
      case "failed":
        return "bg-red-500/10 text-red-400 border-red-500/20";
      default:
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
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
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white">Campaign Details</h1>
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                  campaign.status
                )}`}
              >
                {campaign.status}
              </span>
            </div>
            <p className="text-slate-500">
              Created on {new Date(campaign.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        {campaign.status === "review" && (
          <Link
            href={`/dashboard/campaigns/${campaign.id}/review`}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-all"
          >
            <span>Review Content</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Brief */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Campaign Brief</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-slate-400 mb-1">Brief</p>
                <p className="text-white">{brief.brief}</p>
              </div>
              {brief.target_audience && (
                <div>
                  <p className="text-sm font-medium text-slate-400 mb-1">Target Audience</p>
                  <p className="text-white">{brief.target_audience}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-slate-400 mb-1">Platforms</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {brief.platforms?.map((platform: string) => (
                    <span
                      key={platform}
                      className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm"
                    >
                      {platform}
                    </span>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generated Content */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Generated Content</CardTitle>
              <CardDescription>
                {campaign.content_pieces?.length || 0} pieces created
              </CardDescription>
            </CardHeader>
            <CardContent>
              {campaign.content_pieces && campaign.content_pieces.length > 0 ? (
                <div className="space-y-4">
                  {campaign.content_pieces.map((piece: any) => (
                    <div
                      key={piece.id}
                      className="p-4 bg-slate-800/50 rounded-lg border border-slate-700"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded text-purple-400 text-xs font-medium">
                          {piece.platform}
                        </span>
                        {piece.status === "approved" && (
                          <span className="text-green-400 text-xs">✓ Approved</span>
                        )}
                      </div>
                      <p className="text-white text-sm whitespace-pre-wrap line-clamp-3">
                        {piece.content}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-slate-500">
                    {campaign.status === "generating"
                      ? "Content is being generated..."
                      : "No content generated yet"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Brand Info */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Brand</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                {campaign.brands?.logo_url ? (
                  <img
                    src={campaign.brands.logo_url}
                    alt={campaign.brands.name}
                    className="w-12 h-12 rounded-lg object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {campaign.brands?.name?.charAt(0).toUpperCase()}
                  </div>
                )}
                <div>
                  <p className="text-white font-medium">{campaign.brands?.name}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Cost Breakdown */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Cost Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Total Cost</span>
                <span className="text-white font-semibold">
                  ${campaign.total_cost_usd?.toFixed(4) || "0.0000"}
                </span>
              </div>
              {costBreakdown.tier_1_tokens && (
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500">Tier 1 Tokens</span>
                  <span className="text-slate-400">{costBreakdown.tier_1_tokens}</span>
                </div>
              )}
              {costBreakdown.tier_2_tokens && (
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500">Tier 2 Tokens</span>
                  <span className="text-slate-400">{costBreakdown.tier_2_tokens}</span>
                </div>
              )}
              {costBreakdown.tier_3_tokens && (
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500">Tier 3 Tokens</span>
                  <span className="text-slate-400">{costBreakdown.tier_3_tokens}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          {campaign.status === "review" && (
            <Card className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20">
              <CardHeader>
                <CardTitle className="text-white">Ready to Publish?</CardTitle>
              </CardHeader>
              <CardContent>
                <Link
                  href={`/dashboard/campaigns/${campaign.id}/review`}
                  className="block w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-center transition-all"
                >
                  Review & Approve
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
