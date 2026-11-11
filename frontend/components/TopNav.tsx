"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { post, request, setToken } from "@/lib/api";

export default function TopNav() {
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);
  const router = useRouter();

  useEffect(() => {
    let active = true;
    const onAuthChange = (event: Event) => {
      setSignedIn((event as CustomEvent<boolean>).detail);
    };
    window.addEventListener("pathforge:auth-change", onAuthChange);
    request("/auth/me")
      .then(() => { if (active) setSignedIn(true); })
      .catch(() => { if (active) setSignedIn(false); });
    return () => {
      active = false;
      window.removeEventListener("pathforge:auth-change", onAuthChange);
    };
  }, []);

  async function logout() {
    setLoggingOut(true);
    try { await post("/auth/logout"); }
    finally {
      setToken(null);
      setSignedIn(false);
      setLoggingOut(false);
      router.replace("/login");
    }
  }

  return <nav className="nav" aria-label="Main navigation">
    <Link href="/careers">Explore careers</Link>
    {signedIn === true ? <>
      <Link href="/dashboard">Dashboard</Link>
      <Link href="/profile">Profile</Link>
      <button className="button nav-logout" type="button" onClick={logout} disabled={loggingOut}>{loggingOut ? "Logging out…" : "Log out"}</button>
    </> : signedIn === false ? <>
      <Link href="/login">Log in</Link>
      <Link className="button" href="/register">Get started</Link>
    </> : null}
  </nav>;
}
