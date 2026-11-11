"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import Protected from "@/components/Protected";
import { request } from "@/lib/api";

type DashboardData = {
  target_career?: { name: string };
  progress: { completion_percentage: number; completed_tasks: number; total_tasks: number };
  key_skill_gaps: { skill_name: string; gap: number; priority: number }[];
  next_task?: { title: string; description: string };
  recommended_projects: { id: string; name: string; description: string }[];
  roadmap?: { id: string };
  weekly_goal_hours: number;
  weekly_completed_hours: number;
  estimated_weeks_remaining: number;
  estimated_finish_date?: string;
  setup_steps: { career_selected: boolean; skills_added: boolean; roadmap_created: boolean };
};

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    request<DashboardData>("/dashboard")
      .then(setData)
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Could not load your workspace"))
      .finally(() => setLoading(false));
  }, []);

  const steps = data ? [
    { label: "Choose a career direction", done: data.setup_steps.career_selected, href: "/careers" },
    { label: "Add your current skills", done: data.setup_steps.skills_added, href: "/skills" },
    { label: "Create your first roadmap", done: data.setup_steps.roadmap_created, href: "/roadmap" },
  ] : [];

  return <Protected><AppShell><div className="page-head">
    <div><div className="eyebrow">Your workspace</div><h1>Good to see you.</h1><p>{data?.target_career ? `Working toward ${data.target_career.name}.` : "A few small steps will turn your career goal into a clear plan."}</p></div>
    {data && <Link href={data.roadmap ? "/roadmap" : "/careers"} className="button">{data.roadmap ? "Continue roadmap" : "Get started"}</Link>}
  </div>
  {error ? <div className="notice" role="alert">{error}<button className="text-button" onClick={() => { setError(""); setLoading(true); request<DashboardData>("/dashboard").then(setData).catch((e) => setError(e.message)).finally(() => setLoading(false)); }}>Try again</button></div> : loading || !data ? <div className="skeleton" aria-label="Loading your dashboard"/> : <>
    {!data.setup_steps.roadmap_created && <section className="card setup-card"><div className="setup-heading"><div><span className="tag">START HERE</span><h2>Your path, one step at a time</h2><p>Finish these quick steps to get a plan that fits your goals and experience.</p></div><span className="setup-count">{steps.filter((step) => step.done).length} / 3</span></div><div className="setup-steps">{steps.map((step, index) => <Link href={step.href} className={`setup-step ${step.done ? "is-done" : ""}`} key={step.label}><span className="step-number">{step.done ? "✓" : `0${index + 1}`}</span><span>{step.label}</span><span aria-hidden="true">{step.done ? "Done" : "→"}</span></Link>)}</div></section>}
    <div className="grid three dashboard-grid">
      <section className="card"><p className="muted">Roadmap progress</p><div className="metric">{data.progress.completion_percentage}%</div><div className="progress" role="progressbar" aria-label="Roadmap completion" aria-valuenow={data.progress.completion_percentage} aria-valuemin={0} aria-valuemax={100}><span style={{width:`${data.progress.completion_percentage}%`}}/></div><p className="card-foot">{data.progress.completed_tasks} of {data.progress.total_tasks} tasks complete</p></section>
      <section className="card"><p className="muted">Your next action</p><h3>{data.next_task?.title ?? "Choose your career goal"}</h3><p>{data.next_task?.description ?? "Start with a career direction, then add the skills you already have."}</p>{data.next_task && <Link className="inline-link" href="/roadmap">Open your roadmap →</Link>}</section>
      <section className="card"><p className="muted">Skills to focus on</p><div className="metric">{data.key_skill_gaps.filter((skill) => skill.gap > 0).length}</div><p>Priority gaps based on your chosen career.</p><Link className="inline-link" href="/skills">Review skills →</Link></section>
    </div>
    <div className="grid two dashboard-grid">
      <section className="card"><div className="card-title-row"><div><p className="muted">A steady pace adds up</p><h3>This week’s learning goal</h3></div><span className="tag">{data.weekly_completed_hours} / {data.weekly_goal_hours} h</span></div><div className="progress" role="progressbar" aria-label="Weekly study goal" aria-valuenow={Math.min(100, Math.round(100 * data.weekly_completed_hours / data.weekly_goal_hours))} aria-valuemin={0} aria-valuemax={100}><span style={{width:`${Math.min(100, 100 * data.weekly_completed_hours / data.weekly_goal_hours)}%`}}/></div><p className="card-foot">Counted from tasks completed in the last 7 days. You can tune your weekly hours in <Link className="inline-link" href="/profile">preferences</Link>.</p>{data.estimated_finish_date && <div className="estimate">At this pace, about {data.estimated_weeks_remaining} {data.estimated_weeks_remaining === 1 ? "week" : "weeks"} left · estimated finish {new Date(`${data.estimated_finish_date}T12:00:00`).toLocaleDateString(undefined, {month:"short",day:"numeric",year:"numeric"})}</div>}</section>
      <section className="card"><h3>Highest-impact skills</h3>{data.key_skill_gaps.length === 0 ? <p className="muted">Add a career goal and skills to see your personalized analysis.</p> : data.key_skill_gaps.map((skill) => <div className="bar-row" key={skill.skill_name}><span>{skill.skill_name}</span><div className="bar"><i style={{width:`${Math.min(100,skill.priority*10)}%`}}/></div><strong>{skill.gap>0?`+${skill.gap}`:"Met"}</strong></div>)}</section>
      <section className="card project-card"><h3>Suggested projects</h3>{data.recommended_projects.length === 0 ? <p className="muted">Project ideas will appear after your career and skill assessment are set.</p> : <>{data.recommended_projects.map((project) => <div className="task" key={project.id}><div><h4>{project.name}</h4><p>{project.description}</p></div></div>)}<Link className="inline-link" href="/projects">Explore project ideas →</Link></>}</section>
    </div>
  </>}</AppShell></Protected>;
}
