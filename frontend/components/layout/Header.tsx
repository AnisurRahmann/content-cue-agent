"use client";

import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

interface Brand {
  id: string;
  name: string;
  logo_url: string | null;
}

interface HeaderProps {
  className?: string;
}

export function Header({ className }: HeaderProps) {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    loadBrands();
    loadUser();
  }, []);

  const loadBrands = async () => {
    const supabase = createClient();
    const { data } = await supabase.from("brands").select("id, name, logo_url");
    if (data) {
      setBrands(data);
      if (data.length > 0) setSelectedBrand(data[0]);
    }
  };

  const loadUser = async () => {
    const supabase = createClient();
    const { data: { user } } = await supabase.auth.getUser();
    setUser(user);
  };

  const handleSignOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
  };

  return (
    <header className={className}>
      <div className="flex items-center justify-between">
        {/* Brand Switcher */}
        <div className="flex items-center gap-4">
          {selectedBrand ? (
            <div className="flex items-center gap-3 px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg">
              {selectedBrand.logo_url ? (
                <img
                  src={selectedBrand.logo_url}
                  alt={selectedBrand.name}
                  className="w-8 h-8 rounded-lg object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
                  {selectedBrand.name.charAt(0).toUpperCase()}
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-white">{selectedBrand.name}</p>
                <p className="text-xs text-slate-500">Active Brand</p>
              </div>
              <select
                value={selectedBrand.id}
                onChange={(e) => {
                  const brand = brands.find((b) => b.id === e.target.value);
                  if (brand) setSelectedBrand(brand);
                }}
                className="ml-2 bg-slate-700 text-white text-sm rounded px-2 py-1 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <button
              onClick={() => router.push("/dashboard/brands/new")}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-all"
            >
              <span>+</span>
              <span>Create Brand</span>
            </button>
          )}
        </div>

        {/* User Menu */}
        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-white">
                  {user.user_metadata?.name || "User"}
                </p>
                <p className="text-xs text-slate-500">{user.email}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                {(user.user_metadata?.name || "U").charAt(0).toUpperCase()}
              </div>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-lg border border-slate-700 transition-all"
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
