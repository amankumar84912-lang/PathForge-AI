"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { post, put, request, setToken } from "@/lib/api";

type Profile = { full_name: string; education?: string; experience_level: string; weekly_hours: number; bio?: string; target_career_id?: string };

export default function Login() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [careerId, setCareerId] = useState("");
  const router = useRouter();

  useEffect(() => {
    setCareerId(new URLSearchParams(window.location.search).get("careerId") ?? "");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const data = await post<{ access_token: string }>("/auth/login", { email: form.get("email"), password: form.get("password") });
      setToken(data.access_token);
      if (careerId) {
        try {
          const profile = await request<Profile>("/profile");
          await put("/profile", { ...profile, target_career_id: careerId });
          router.push("/skills");
          return;
        } catch {
          setError("You’re signed in, but we could not save that goal. You can select it from Profile.");
        }
      }
      router.push("/dashboard");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to log in.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="auth-wrap">
    <Link href="/" className="auth-back">← PathForge AI</Link>
    <h1>Welcome back</h1><p className="muted">Continue building your career path.</p>
    <form className="form-card" onSubmit={submit}>
      {error && <div className="notice" role="alert">{error}</div>}
      <div className="field"><label htmlFor="email">Email</label><input id="email" name="email" type="email" required autoComplete="email" maxLength={320}/></div>
      <div className="field"><label htmlFor="password">Password</label><input id="password" name="password" type="password" required autoComplete="current-password" maxLength={128}/></div>
      <button className="button auth-submit" disabled={loading}>{loading ? "Signing in…" : "Log in"}</button>
      <p className="muted auth-switch">New to PathForge? <Link href={careerId ? `/register?careerId=${encodeURIComponent(careerId)}` : "/register"}>Create an account</Link></p>
    </form>
  </main>;
}
