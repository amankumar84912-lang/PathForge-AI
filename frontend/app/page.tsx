import Link from "next/link";

const previewTasks = [
  { title: "Strengthen the foundations", detail: "Practice core concepts before moving on", state: "In progress", progress: 68 },
  { title: "Build a portfolio project", detail: "Turn your learning into something you can show", state: "Up next", progress: 34 },
  { title: "Prepare for interviews", detail: "Review, explain, and apply what you know", state: "Later", progress: 12 },
];

const features = [
  { number: "01", title: "Know where to begin", text: "Compare your current skills with the skills a career path asks for, so your first step is clear." },
  { number: "02", title: "Learn in the right order", text: "Build fundamentals first, then move through the topics and projects that depend on them." },
  { number: "03", title: "Fit learning into real life", text: "Get a focused plan shaped around your experience and the hours you can study each week." },
  { number: "04", title: "See your progress", text: "Track tasks as you go and keep your next action visible whenever you return." },
];

const steps = [
  { number: "1", title: "Choose a direction", text: "Explore career goals and pick the one you want to work toward." },
  { number: "2", title: "Share your starting point", text: "Add your skills, experience, and the time you can realistically study." },
  { number: "3", title: "Follow your roadmap", text: "Work through clear phases, useful projects, and manageable weekly tasks." },
];

const questions = [
  { question: "What does PathForge do?", answer: "PathForge helps you compare your current skills with a career goal and organize the next learning steps into a roadmap." },
  { question: "Do I need an account?", answer: "You can explore career paths without signing in. Create an account to save your profile, roadmap, and progress." },
  { question: "Can I change my goal or study hours?", answer: "Yes. You can update your preferences and refresh your roadmap when your priorities or available study time change." },
  { question: "Does PathForge guarantee a job or internship?", answer: "No. The roadmap is a planning aid to help you learn and prepare. Outcomes depend on your work, experience, and the opportunities you pursue." },
];

export default function Home() {
  return (
    <main className="landing">
      <section className="landing-hero">
        <div className="container landing-hero-grid">
          <div className="landing-copy">
            <div className="eyebrow"><span className="eyebrow-mark" /> A practical coach for your next step</div>
            <h1>Stop guessing.<br />Start building your path.</h1>
            <p className="landing-lede">PathForge turns your career goal, current skills, and available time into a learning roadmap you can actually follow.</p>
            <div className="hero-actions">
              <Link className="button landing-primary" href="/register">Build my roadmap <span aria-hidden="true">↗</span></Link>
              <Link className="button secondary" href="/careers">Explore career paths</Link>
            </div>
            <div className="landing-promises" aria-label="PathForge benefits">
              <span><span aria-hidden="true">✓</span> A plan shaped around you</span>
              <span><span aria-hidden="true">✓</span> Clear, manageable next steps</span>
              <span><span aria-hidden="true">✓</span> Progress you can track</span>
            </div>
          </div>

          <div className="roadmap-preview" aria-label="Example roadmap preview">
            <div className="preview-topline"><span className="preview-dot" /> YOUR ROADMAP PREVIEW <span className="preview-menu" aria-hidden="true">···</span></div>
            <div className="preview-heading">
              <div><span className="tag">EXAMPLE PLAN</span><h2>A little progress, every week.</h2><p>A sample of how your learning plan could be organized.</p></div>
              <div className="preview-ring"><strong>12</strong><span>weeks</span></div>
            </div>
            <div className="preview-progress-label"><span>Plan overview</span><span>3 learning phases</span></div>
            <div className="preview-progress"><i /></div>
            <div className="preview-tasks">
              {previewTasks.map((task, index) => (
                <div className="preview-task" key={task.title}>
                  <span className={`preview-check preview-check-${index}`} aria-hidden="true">{index === 0 ? "✓" : String(index + 1).padStart(2, "0")}</span>
                  <div className="preview-task-copy"><strong>{task.title}</strong><span>{task.detail}</span><div className="preview-task-bar"><i style={{ width: `${task.progress}%` }} /></div></div>
                  <span className={`preview-state preview-state-${index}`}>{task.state}</span>
                </div>
              ))}
            </div>
            <div className="preview-foot"><span className="preview-avatar" aria-hidden="true">↗</span><span>Your plan starts with <strong>your goal</strong> and <strong>your schedule</strong>.</span></div>
          </div>
        </div>
        <div className="hero-bottom-rule" />
      </section>

      <section className="landing-section landing-features" id="features">
        <div className="container">
          <div className="section-intro">
            <span className="eyebrow">LESS NOISE. MORE DIRECTION.</span>
            <h2>A clear next step beats<br className="desktop-break" /> another open tab.</h2>
            <p>Skip the scattered advice. Focus on what to learn, why it matters, and what to do next.</p>
          </div>
          <div className="landing-feature-grid">
            {features.map((feature) => (
              <article className="landing-feature" key={feature.number}>
                <span className="feature-number">{feature.number}</span>
                <div className="feature-arrow" aria-hidden="true">↗</div>
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-section landing-how" id="how-it-works">
        <div className="container how-grid">
          <div className="how-intro">
            <span className="eyebrow">HOW IT WORKS</span>
            <h2>From “where do I start?” to a plan you can follow.</h2>
            <p>Set a direction, make the plan fit your week, and keep moving at a sustainable pace.</p>
            <Link className="inline-link" href="/careers">See all career paths <span aria-hidden="true">→</span></Link>
          </div>
          <div className="how-steps">
            {steps.map((step) => (
              <article className="how-step" key={step.number}>
                <span className="how-step-number">{step.number}</span>
                <div><h3>{step.title}</h3><p>{step.text}</p></div>
                <span className="how-step-line" aria-hidden="true" />
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-section landing-faq" id="faq">
        <div className="container faq-grid">
          <div className="section-intro faq-intro"><span className="eyebrow">GOOD TO KNOW</span><h2>Questions, answered.</h2><p>Understand what the roadmap can help with before you get started.</p></div>
          <div className="faq-list">
            {questions.map((item) => <details className="faq-item" key={item.question}><summary>{item.question}<span aria-hidden="true">+</span></summary><p>{item.answer}</p></details>)}
          </div>
        </div>
      </section>

      <section className="landing-cta">
        <div className="container cta-inner">
          <div><span className="eyebrow">YOUR NEXT STEP STARTS HERE</span><h2>Make a plan. Then make it yours.</h2><p>Choose a career direction and build a roadmap around your goals and time.</p></div>
          <Link className="button cta-button" href="/register">Get started <span aria-hidden="true">↗</span></Link>
        </div>
      </section>
      <footer className="landing-footer"><div className="container footer-inner"><Link className="brand" href="/"><span className="brand-mark">↗</span>PathForge AI</Link><span>Personalized learning plans for your next career step.</span><div><Link href="/careers">Explore careers</Link><Link href="/login">Log in</Link><Link href="/register">Get started</Link></div><small>© {new Date().getFullYear()} PathForge AI</small></div></footer>
    </main>
  );
}
