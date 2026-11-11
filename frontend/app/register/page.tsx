"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { post, put, request, setToken } from "@/lib/api";

type Profile = { full_name: string; education?: string; experience_level: string; weekly_hours: number; bio?: string; target_career_id?: string };
type Career = { id: string; name: string };

export default function Register() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [career, setCareer] = useState<Career | null>(null);
  const [careerId, setCareerId] = useState("");
  const router = useRouter();

  useEffect(() => {
    const careerId = new URLSearchParams(window.location.search).get("careerId");
    if (!careerId) return;
    setCareerId(careerId);
    request<Career>(`/careers/${encodeURIComponent(careerId)}`)
      .then(setCareer)
      .catch(() => setError("That career goal is unavailable. You can choose one after creating your account."));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    if (form.get("password") !== form.get("confirm")) { setError("Passwords do not match."); return; }
    setLoading(true);
    setError("");
    try {
      const result = await post<{ access_token: string }>("/auth/register", {
        full_name: form.get("full_name"), email: form.get("email"), password: form.get("password"),
      });
      setToken(result.access_token);
      if (careerId) {
        try {
          const profile = await request<Profile>("/profile");
          await put("/profile", { ...profile, target_career_id: careerId });
          router.push("/skills");
          return;
        } catch {
          setError("Your account is ready, but we could not save the selected goal. You can choose it in Profile.");
          router.push("/profile");
          return;
        }
      }
      router.push("/profile");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create your account.");
    } finally {
      setLoading(false);
    }
  }

  return <main className="auth-wrap">
    <Link href="/" className="auth-back">← PathForge AI</Link>
    <h1>Start your path</h1><p className="muted">A few details, then a roadmap shaped around you.</p>
    {career && <div className="selected-goal" role="status"><span className="tag">YOUR SELECTED GOAL</span><strong>{career.name}</strong><Link href="/careers">Change</Link></div>}
    <form className="form-card" onSubmit={submit}>
      {error && <div className="notice" role="alert">{error}</div>}
      <div className="field"><label htmlFor="full_name">Name</label><input id="full_name" name="full_name" required autoComplete="name" maxLength={120}/></div>
      <div className="field"><label htmlFor="email">Email</label><input id="email" name="email" type="email" required autoComplete="email" maxLength={320}/></div>
      <div className="field"><label htmlFor="password">Password</label><input id="password" name="password" type="password" minLength={10} maxLength={128} required autoComplete="new-password"/><small className="muted">Use at least 10 characters, including uppercase, lowercase, and a number.</small></div>
      <div className="field"><label htmlFor="confirm">Confirm password</label><input id="confirm" name="confirm" type="password" minLength={10} maxLength={128} required autoComplete="new-password"/></div>
      <button className="button auth-submit" disabled={loading}>{loading ? "Creating your account…" : "Create account"}</button>
      <p className="muted auth-switch">Already have an account? <Link href={careerId ? `/login?careerId=${encodeURIComponent(careerId)}` : "/login"}>Log in</Link></p>
    </form>
  </main>;
}
