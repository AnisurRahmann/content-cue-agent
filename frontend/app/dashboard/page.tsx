import { createClient } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Fetch stats
  const { data: brands } = await supabase
    .from("brands")
    .select("id")
    .eq("user_id", user?.id);

  const { data: campaigns } = await supabase
    .from("campaigns")
    .select("id, status, total_cost_usd")
    .eq("user_id", user?.id);

  const totalCampaigns = campaigns?.length || 0;
  const totalCost = campaigns?.reduce((sum, c) => sum + (c.total_cost_usd || 0), 0) || 0;
  const publishedCampaigns = campaigns?.filter(c => c.status === "published").length || 0;

  const recentCampaigns = await supabase
    .from("campaigns")
    .select("id, brief, status, created_at, brands(name)")
    .eq("user_id", user?.id)
    .order("created_at", { ascending: false })
    .limit(5);

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome back, {user?.user_metadata?.name || "User"}!
        </h1>
        <p className="text-slate-400">Here's what's happening with your campaigns</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Total Campaigns</CardTitle>
            <CardDescription>All time campaigns</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-white">{totalCampaigns}</div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Published</CardTitle>
            <CardDescription>Live campaigns</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-400">{publishedCampaigns}</div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Total Spend</CardTitle>
            <CardDescription>AI generation costs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-blue-400">
              ${totalCost.toFixed(4)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Campaigns */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Recent Campaigns</CardTitle>
          <CardDescription>Your latest marketing campaigns</CardDescription>
        </CardHeader>
        <CardContent>
          {recentCampaigns.data && recentCampaigns.data.length > 0 ? (
            <div className="space-y-4">
              {recentCampaigns.data.map((campaign: any) => (
                <div
                  key={campaign.id}
                  className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700"
                >
                  <div className="flex-1">
                    <p className="text-white font-medium line-clamp-1">
                      {campaign.brief}
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      {campaign.brands?.name || "Unknown Brand"}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
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
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-slate-500">No campaigns yet</p>
              <p className="text-sm text-slate-600 mt-1">
                Create your first campaign to get started
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-blue-500/20">
          <CardHeader>
            <CardTitle className="text-white">Create Campaign</CardTitle>
            <CardDescription className="text-slate-400">
              Generate AI-powered marketing content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <a
              href="/dashboard/campaigns/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-all"
            >
              <span>Start Creating</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5 5H6" />
              </svg>
            </a>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20">
          <CardHeader>
            <CardTitle className="text-white">Manage Brands</CardTitle>
            <CardDescription className="text-slate-400">
              Add and manage your brand profiles
            </CardDescription>
          </CardHeader>
          <CardContent>
            <a
              href="/dashboard/brands"
              className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-all"
            >
              <span>View Brands</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5 5H6" />
              </svg>
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
