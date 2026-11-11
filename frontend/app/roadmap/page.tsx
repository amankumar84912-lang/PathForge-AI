"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import AppShell from "@/components/AppShell";
import Protected from "@/components/Protected";
import { patch, post, request } from "@/lib/api";

type Resource = { id: string; title: string; url: string; resource_type: string; description: string };
type Task = { id: string; title: string; description: string; estimated_hours: number; order_index: number; status: "not_started" | "in_progress" | "completed" | "skipped"; resources: Resource[] };
type Roadmap = { id: string; title: string; summary: string; status: string; generation_mode?: string; phases: { id: string; title: string; description: string; milestones?: { id: string; title: string; description: string }[]; tasks: Task[] }[] };
type Profile = { target_career_id?: string; weekly_hours: number };

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [weeklyHours, setWeeklyHours] = useState(6);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const initialized = useRef(false);

  const load = useCallback(async () => {
    try {
      const [list, currentProfile] = await Promise.all([request<Roadmap[]>("/roadmaps"), request<Profile>("/profile")]);
      setRoadmap(list.find((item) => item.status === "active") ?? null);
      setProfile(currentProfile);
      if (!initialized.current) setWeeklyHours(currentProfile.weekly_hours);
      initialized.current = true;
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not load your roadmap"); }
  }, []);
  useEffect(() => { void load(); }, [load]);

  const totalHours = useMemo(() => roadmap?.phases.reduce((sum, phase) => sum + phase.tasks.filter((task) => task.status !== "completed" && task.status !== "skipped").reduce((phaseSum, task) => phaseSum + task.estimated_hours, 0), 0) ?? 0, [roadmap]);
  const remainingWeeks = totalHours ? Math.ceil(totalHours / Math.max(1, weeklyHours)) : 0;
  const finishDate = new Date(); finishDate.setDate(finishDate.getDate() + remainingWeeks * 7);

  async function generate() {
    if (!profile?.target_career_id) { setError("Choose a target career first; the roadmap is tailored to its skill requirements."); return; }
    setBusy(true); setError(""); setNotice("");
    try {
      const result = await post<Roadmap>("/roadmaps/generate", { career_id: profile.target_career_id, weekly_hours: weeklyHours });
      setRoadmap(result);
      if (result.generation_mode === "deterministic-local") setNotice("Your plan is ready using PathForge’s local planner. AI personalization is temporarily unavailable, but you can keep learning and tracking progress.");
      else setNotice("Your personalized roadmap is ready.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Could not generate your roadmap. Please try again."); }
    finally { setBusy(false); }
  }

  async function update(task: Task, status: Task["status"]) {
    try { await patch(`/tasks/${task.id}`, { status }); setError(""); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not update the task"); }
  }

  async function move(task: Task, direction: -1 | 1, siblings: Task[]) {
    const position = siblings.findIndex((item) => item.id === task.id) + 1 + direction;
    if (position < 1 || position > siblings.length) return;
    try { await patch(`/tasks/${task.id}/order`, { order_index: position }); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not rearrange tasks"); }
  }

  return <Protected><AppShell><div className="page-head roadmap-head"><div><div className="eyebrow">Your learning plan</div><h1>{roadmap?.title ?? "Your roadmap"}</h1><p>{roadmap?.summary ?? "Choose your pace, then build a step-by-step plan for your career goal."}</p></div></div>
    <section className="card pace-card"><div><span className="tag">MAKE IT FIT YOUR WEEK</span><h2>Choose a sustainable pace</h2><p className="muted">Your plan stays flexible. Adjust hours here, or save your default in Profile.</p></div><div className="pace-controls"><label htmlFor="weekly-hours">Study hours per week</label><div className="pace-input"><input id="weekly-hours" type="number" min={1} max={80} value={weeklyHours} onChange={(event) => setWeeklyHours(Math.max(1, Math.min(80, Number(event.target.value) || 1)))}/><span>hours / week</span></div>{roadmap && <p className="estimate">{remainingWeeks ? `About ${remainingWeeks} ${remainingWeeks === 1 ? "week" : "weeks"} to go · around ${finishDate.toLocaleDateString(undefined,{month:"short",day:"numeric"})}` : "All roadmap tasks are complete — fantastic work."}</p>}</div><button className="button" onClick={generate} disabled={busy}>{busy ? "Building your plan…" : roadmap ? "Refresh my plan" : "Create my roadmap"}</button></section>
    {error && <div className="notice" role="alert">{error}</div>}{notice && <div className="success-notice" role="status">{notice}</div>}
    {!roadmap ? <div className="empty roadmap-empty"><h3>Your next chapter starts here</h3><p>{profile?.target_career_id ? "Choose your weekly pace and create a roadmap. You can change task status and reorder steps as you learn." : "First pick a career direction and add a few skills so your plan can meet you where you are."}</p></div> : <section className="roadmap-phases">{roadmap.phases.map((phase, phaseIndex) => <article className="phase-card" key={phase.id}><div className="phase-top"><span className="tag">PHASE {String(phaseIndex + 1).padStart(2,"0")}</span><span className="muted">{phase.tasks.reduce((sum, task) => sum + task.estimated_hours, 0)}h total</span></div><h2>{phase.title}</h2><p className="muted">{phase.description}</p>{phase.milestones?.map((milestone) => <div key={milestone.id} className="milestone"><span aria-hidden="true">✦</span><div><strong>Milestone</strong><br/>{milestone.title}</div></div>)}<div className="phase-tasks">{phase.tasks.map((task, index) => <div className={`roadmap-task ${task.status === "completed" || task.status === "skipped" ? "task-done" : ""}`} key={task.id}><div className="task-main"><div className="task-label-row"><span className="task-index">{String(index + 1).padStart(2,"0")}</span><h3>{task.title}</h3></div><p>{task.description}</p><span className="task-hours">◷ {task.estimated_hours} estimated hours</span>{task.resources.length > 0 && <details className="resource-details"><summary>Learning resources <span>({task.resources.length})</span></summary><div className="resource-list">{task.resources.map((resource) => <a key={resource.id} href={resource.url} target="_blank" rel="noreferrer"><span className="resource-type">{resource.resource_type}</span><strong>{resource.title} ↗</strong>{resource.description && <small>{resource.description}</small>}</a>)}</div></details>}</div><div className="task-actions"><label className="sr-only" htmlFor={`task-${task.id}`}>Status for {task.title}</label><select id={`task-${task.id}`} value={task.status} onChange={(event) => update(task, event.target.value as Task["status"])}><option value="not_started">Not started</option><option value="in_progress">In progress</option><option value="completed">Completed</option><option value="skipped">Skip for now</option></select><div className="reorder-actions"><button className="icon-button" aria-label={`Move ${task.title} up`} title="Move up" disabled={index === 0} onClick={() => move(task, -1, phase.tasks)}>↑</button><button className="icon-button" aria-label={`Move ${task.title} down`} title="Move down" disabled={index === phase.tasks.length - 1} onClick={() => move(task, 1, phase.tasks)}>↓</button></div></div></div>)}</div></article>)}</section>}
  </AppShell></Protected>;
}
