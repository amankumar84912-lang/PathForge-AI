"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { put, request } from "@/lib/api";

type Career = { id: string; name: string; category: string; description: string; difficulty_level: number };
type Row = { skill_id: string; required_level: number; importance: number; relevance: number; skill: { name: string; description: string } };
type Profile = { full_name: string; education?: string; experience_level: string; weekly_hours: number; bio?: string; target_career_id?: string };

export default function CareerDetail() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [career, setCareer] = useState<Career | null>(null);
  const [skills, setSkills] = useState<Row[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([request<Career>(`/careers/${params.id}`), request<Row[]>(`/careers/${params.id}/skills`)])
      .then(([item, requirements]) => { if (active) { setCareer(item); setSkills(requirements); } })
      .catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : "Could not load this career path"); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [params.id]);

  async function select() {
    setBusy(true);
    setError("");
    try {
      const profile = await request<Profile>("/profile");
      await put("/profile", { ...profile, target_career_id: params.id });
      router.push("/skills");
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : "Could not select career";
      if (message === "Authentication is required" || message === "Invalid or expired token") {
        router.push(`/register?careerId=${encodeURIComponent(params.id)}`);
      } else {
        setError(message);
      }
    } finally {
      setBusy(false);
    }
  }

  return <main className="container public-career-page">
    <Link href="/careers" className="inline-link back-link">← All career goals</Link>
    {error && <div className="notice" role="alert">{error}</div>}
    {loading ? <div className="skeleton" aria-label="Loading career path"/> : !career ? <div className="empty"><h2>Career path not found</h2><p>It may have been removed from the catalog.</p><Link className="button" href="/careers">Browse career goals</Link></div> : <>
      <section className="career-detail-hero">
        <div><span className="tag category-tag">{career.category}</span><div className="eyebrow" style={{ marginTop: 18 }}>Career path</div><h1>{career.name}</h1><p>{career.description}</p><span className="muted">Typical entry level · {career.difficulty_level}/5</span></div>
        <button className="button" onClick={select} disabled={busy}>{busy ? "Saving your path…" : "Choose this goal"}</button>
      </section>
      <section className="career-requirements card"><div className="requirements-heading"><div><h2>Skills used in this path</h2><p className="muted">These are starting benchmarks. Your roadmap will prioritize the gaps you choose to work on.</p></div><span className="tag">{skills.length} skills</span></div>
        {skills.map((item) => <div className="requirement-row" key={item.skill_id}><div><strong>{item.skill.name}</strong><p className="muted">{item.skill.description}</p></div><div className="requirement-level"><div className="bar"><i style={{ width: `${item.required_level * 20}%` }}/></div><strong>{item.required_level}/5</strong></div></div>)}
      </section>
      <div className="career-detail-next"><p>Create an account to assess your current skills and get a plan for this role.</p><Link href={`/register?careerId=${encodeURIComponent(career.id)}`} className="inline-link">Start with this goal →</Link></div>
    </>}
  </main>;
}
