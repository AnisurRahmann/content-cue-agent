"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

interface ContentPiece {
  id: string;
  platform: string;
  content: string;
  status: string;
}

export default function CampaignReviewPage() {
  const params = useParams();
  const router = useRouter();
  const [contentPieces, setContentPieces] = useState<ContentPiece[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [campaign, setCampaign] = useState<any>(null);

  useEffect(() => {
    loadCampaign();
  }, [params.id]);

  const loadCampaign = async () => {
    const supabase = createClient();
    const { data, error } = await supabase
      .from("campaigns")
      .select(
        `
        *,
        brands(name)
      `
      )
      .eq("id", params.id)
      .single();

    if (error) {
      console.error("Error loading campaign:", error);
      return;
    }

    setCampaign(data);

    const { data: pieces } = await supabase
      .from("content_pieces")
      .select("*")
      .eq("campaign_id", params.id);

    if (pieces) {
      setContentPieces(pieces);
    }
    setLoading(false);
  };

  const handleApprove = async (pieceId: string) => {
    const supabase = createClient();
    const { error } = await supabase
      .from("content_pieces")
      .update({ status: "approved" })
      .eq("id", pieceId);

    if (!error) {
      setContentPieces((prev) =>
        prev.map((p) => (p.id === pieceId ? { ...p, status: "approved" } : p))
      );
    }
  };

  const handleReject = async (pieceId: string) => {
    const supabase = createClient();
    const { error } = await supabase
      .from("content_pieces")
      .update({ status: "rejected" })
      .eq("id", pieceId);

    if (!error) {
      setContentPieces((prev) =>
        prev.map((p) => (p.id === pieceId ? { ...p, status: "rejected" } : p))
      );
    }
  };

  const handlePublish = async () => {
    setSubmitting(true);
    try {
      const supabase = createClient();
      // Update campaign status to published
      const { error } = await supabase
        .from("campaigns")
        .update({ status: "published" })
        .eq("id", params.id);

      if (error) throw error;

      router.push("/dashboard/campaigns");
    } catch (err) {
      console.error("Error publishing campaign:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const allApproved = contentPieces.length > 0 &&
    contentPieces.every((p) => p.status === "approved");

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading campaign...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href={`/dashboard/campaigns/${params.id}`}
            className="p-2 hover:bg-slate-800 rounded-lg transition-all"
          >
            <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Review Campaign</h1>
            <p className="text-slate-400">Review and approve AI-generated content</p>
          </div>
        </div>
        {allApproved && (
          <button
            onClick={handlePublish}
            disabled={submitting}
            className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-slate-700 text-white font-medium rounded-lg transition-all"
          >
            {submitting ? "Publishing..." : "Publish Campaign"}
          </button>
        )}
      </div>

      {/* Content Pieces */}
      <div className="space-y-6">
        {contentPieces.length === 0 ? (
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="py-16 text-center">
              <p className="text-slate-500">No content generated yet</p>
            </CardContent>
          </Card>
        ) : (
          contentPieces.map((piece) => (
            <Card key={piece.id} className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-white capitalize">{piece.platform}</CardTitle>
                    <CardDescription>AI-generated content for {piece.platform}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    {piece.status === "approved" && (
                      <span className="px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full text-green-400 text-sm">
                        ✓ Approved
                      </span>
                    )}
                    {piece.status === "rejected" && (
                      <span className="px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-full text-red-400 text-sm">
                        ✗ Rejected
                      </span>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 mb-4">
                  <p className="text-white whitespace-pre-wrap">{piece.content}</p>
                </div>
                <div className="flex gap-3">
                  {piece.status !== "approved" && (
                    <button
                      onClick={() => handleApprove(piece.id)}
                      className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-all"
                    >
                      Approve
                    </button>
                  )}
                  {piece.status !== "rejected" && (
                    <button
                      onClick={() => handleReject(piece.id)}
                      className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-all"
                    >
                      Reject
                    </button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Publish Summary */}
      {contentPieces.length > 0 && (
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-white">{contentPieces.length}</p>
                <p className="text-sm text-slate-500">Total Pieces</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-400">
                  {contentPieces.filter((p) => p.status === "approved").length}
                </p>
                <p className="text-sm text-slate-500">Approved</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-400">
                  {contentPieces.filter((p) => p.status === "rejected").length}
                </p>
                <p className="text-sm text-slate-500">Rejected</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
