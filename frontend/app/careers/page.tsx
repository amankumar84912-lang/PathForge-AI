"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { post, request } from "@/lib/api";

type Career = {
  id: string;
  name: string;
  category: string;
  description: string;
  difficulty_level: number;
  compatibility?: number;
};

export default function Careers() {
  const [items, setItems] = useState<Career[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All goals");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const careers = await request<Career[]>("/careers");
        if (active) setItems(careers);
        try {
          const recommendations = await post<(Career & { compatibility: number })[]>("/recommendations/careers");
          if (active) {
            const scores = new Map(recommendations.map((item) => [item.id, item.compatibility]));
            setItems(careers.map((career) => ({ ...career, compatibility: scores.get(career.id) })));
          }
        } catch {
          // Public visitors can browse the full catalog without signing in for match scores.
        }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "Could not load career paths");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  const categories = useMemo(() => ["All goals", ...new Set(items.map((item) => item.category))], [items]);
  const filtered = useMemo(() => items.filter((item) => {
    const matchesCategory = category === "All goals" || item.category === category;
    const matchesQuery = `${item.name} ${item.description} ${item.category}`.toLowerCase().includes(query.trim().toLowerCase());
    return matchesCategory && matchesQuery;
  }), [items, category, query]);
  const topMatch = items.reduce<Career | null>((best, item) => item.compatibility !== undefined && (!best || item.compatibility > (best.compatibility ?? 0)) ? item : best, null);

  return <main className="container public-career-page">
    <div className="page-head public-career-heading">
      <div><div className="eyebrow">Find your direction</div><h1>Explore career goals</h1><p>Browse different fields, compare the skills each path uses, and choose a direction that fits your interests.</p></div>
      <Link className="button" href="/register">Build my roadmap</Link>
    </div>
    <div className="career-tools">
      <label className="search-control"><span aria-hidden="true">⌕</span><span className="sr-only">Search career goals</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search goals, fields, or skills"/></label>
      <span className="muted">{filtered.length} {filtered.length === 1 ? "goal" : "goals"}</span>
    </div>
    <div className="goal-categories" aria-label="Filter career goals">
      {categories.map((item) => <button key={item} type="button" className={`goal-category ${category === item ? "selected" : ""}`} aria-pressed={category === item} onClick={() => setCategory(item)}>{item}</button>)}
    </div>
    {error ? <div className="notice" role="alert">{error}</div> : loading ? <div className="skeleton" aria-label="Loading career goals"/> : filtered.length === 0 ? <div className="empty"><h3>No matching goals</h3><p>Try a different search or choose another field.</p><button className="text-button" onClick={() => { setQuery(""); setCategory("All goals"); }}>Clear filters</button></div> : <div className="grid three">
      {filtered.map((career) => <article className="card career-card" key={career.id}>
        {career.id === topMatch?.id && <span className="tag">BEST CURRENT MATCH</span>}
        <div className="career-meta"><span className="tag category-tag">{career.category}</span>{career.compatibility !== undefined && <span className="match-score">{career.compatibility}% match</span>}</div>
        <h2>{career.name}</h2><p>{career.description}</p>
        <div className="career-card-foot"><span className="muted">Typical entry level · {career.difficulty_level}/5</span><Link href={`/careers/${career.id}`} className="inline-link">View skills and path <span aria-hidden="true">→</span></Link></div>
      </article>)}
    </div>}
    {!loading && !error && !items.some((item) => item.compatibility !== undefined) && <p className="career-footnote">Sign in to see how each path matches your current skills.</p>}
  </main>;
}
