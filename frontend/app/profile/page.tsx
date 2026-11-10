"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import AppShell from "@/components/AppShell";
import Protected from "@/components/Protected";
import { put, request } from "@/lib/api";

type Career = { id: string; name: string; category: string };
type Profile = { full_name: string; education?: string; experience_level: string; weekly_hours: number; bio?: string; target_career_id?: string };

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [careers, setCareers] = useState<Career[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([request<Profile>("/profile"), request<Career[]>("/careers")])
      .then(([current, catalog]) => { setProfile(current); setCareers(catalog); })
      .catch((reason) => setMessage(reason instanceof Error ? reason.message : "Could not load your profile"))
      .finally(() => setLoading(false));
  }, []);

  const groupedCareers = useMemo(() => careers.reduce<Record<string, Career[]>>((groups, career) => {
    (groups[career.category] ??= []).push(career);
    return groups;
  }, {}), [careers]);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSaving(true);
    setMessage("");
    try {
      const updated = await put<Profile>("/profile", {
        full_name: form.get("full_name"), education: form.get("education") || null,
        experience_level: form.get("experience_level"), weekly_hours: Number(form.get("weekly_hours")),
        bio: form.get("bio") || null, target_career_id: form.get("target_career_id") || null,
      });
      setProfile(updated);
      setMessage("Profile saved. Your roadmap will use these preferences.");
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "Could not save your profile");
    } finally {
      setSaving(false);
    }
  }

  return <Protected><AppShell><div className="page-head"><div><div className="eyebrow">Make the plan fit you</div><h1>Profile & preferences</h1><p>Share your learning context and choose from career goals across different fields.</p></div></div>
    {loading ? <div className="skeleton" aria-label="Loading your profile"/> : !profile ? <div className="notice" role="alert">{message}</div> : <form className="form-card profile-form" onSubmit={save}>
      <div className="grid two">
        <div className="field"><label htmlFor="full_name">Name</label><input id="full_name" name="full_name" defaultValue={profile.full_name} maxLength={120} required/></div>
        <div className="field"><label htmlFor="education">Education</label><input id="education" name="education" defaultValue={profile.education ?? ""} maxLength={200} placeholder="e.g. B.Tech Computer Science"/></div>
        <div className="field"><label htmlFor="experience_level">Experience level</label><select id="experience_level" name="experience_level" defaultValue={profile.experience_level}><option value="beginner">Beginner</option><option value="student">Student</option><option value="junior">Junior</option><option value="mid">Mid-level</option><option value="senior">Senior</option></select></div>
        <div className="field"><label htmlFor="weekly_hours">Weekly study hours</label><input id="weekly_hours" name="weekly_hours" defaultValue={profile.weekly_hours} type="number" min={1} max={80} required/><small className="muted">Choose time you can keep up with most weeks.</small></div>
      </div>
      <div className="field"><label htmlFor="target_career_id">Target career goal</label><select id="target_career_id" name="target_career_id" defaultValue={profile.target_career_id ?? ""}><option value="">Choose a career goal</option>{Object.entries(groupedCareers).map(([category, items]) => <optgroup label={category} key={category}>{items.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</optgroup>)}</select></div>
      <div className="field"><label htmlFor="bio">Learning preferences and constraints <span className="muted">(optional)</span></label><textarea id="bio" name="bio" defaultValue={profile.bio ?? ""} rows={4} maxLength={2000} placeholder="For example: I learn best by building projects, have 5 hours per week, and need to finish exams in May."/><small className="muted">The roadmap planner uses this to make suggestions more practical.</small></div>
      {message && <p className={message.startsWith("Profile saved") ? "success-notice" : "notice"} role={message.startsWith("Profile saved") ? "status" : "alert"}>{message}</p>}
      <button className="button" disabled={saving}>{saving ? "Saving…" : "Save preferences"}</button>
    </form>}
  </AppShell></Protected>;
}
