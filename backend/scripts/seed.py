"""Idempotently seed career goals, skill maps, projects, and trusted learning resources."""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    Career,
    CareerProject,
    CareerSkill,
    Project,
    ProjectSkill,
    Resource,
    Skill,
    SkillPrerequisite,
    SkillResource,
)

SKILLS = [
    ("Python", "Programming", "Write scripts, applications, and data tools in Python."),
    ("JavaScript", "Software Development", "Build interactive web and server applications."),
    ("TypeScript", "Software Development", "Write typed JavaScript for larger applications."),
    ("HTML & CSS", "Web Development", "Structure and style accessible web pages."),
    ("React", "Web Development", "Build reusable interfaces with components and state."),
    ("FastAPI", "Backend Development", "Create typed APIs and backend services."),
    ("SQL", "Data", "Query and design relational databases."),
    ("Git", "Software Development", "Track code changes and collaborate safely."),
    ("Data Structures", "Computer Science", "Choose efficient collections and algorithms."),
    ("Software Testing", "Quality Engineering", "Design tests that prevent regressions."),
    ("API Design", "Backend Development", "Design predictable, secure service interfaces."),
    ("Docker", "Cloud & Operations", "Package applications into repeatable containers."),
    ("Linux", "Cloud & Operations", "Work with Linux systems, processes, and permissions."),
    ("Networking", "Cloud & Security", "Understand network protocols, routing, and services."),
    ("Cloud Fundamentals", "Cloud & Operations", "Deploy and operate services on cloud platforms."),
    ("CI/CD", "Cloud & Operations", "Automate testing and application delivery."),
    ("Monitoring", "Cloud & Operations", "Use logs, metrics, and alerts to diagnose services."),
    ("Statistics", "Data & AI", "Use probability, sampling, and statistical reasoning."),
    ("Excel", "Business", "Analyze and communicate structured business data."),
    ("Data Visualization", "Data & AI", "Explain patterns with clear charts and dashboards."),
    ("Machine Learning", "Data & AI", "Train and evaluate models for data problems."),
    ("Generative AI", "Data & AI", "Build applications using generative AI models."),
    ("Prompt Design", "Data & AI", "Write and evaluate instructions for language models."),
    ("Figma", "Design", "Create interface designs and interactive prototypes."),
    ("UX Research", "Design", "Learn user needs through interviews and usability studies."),
    ("Accessibility", "Design & Web", "Make digital products usable by people with disabilities."),
    ("Product Strategy", "Product & Business", "Define customer problems, outcomes, and product direction."),
    ("Agile Delivery", "Product & Business", "Plan and deliver work in iterative team cycles."),
    ("Project Management", "Product & Business", "Coordinate scope, timelines, risks, and stakeholders."),
    ("Digital Marketing", "Marketing", "Plan and measure digital customer acquisition."),
    ("Content Strategy", "Marketing", "Plan useful content for a defined audience and purpose."),
    ("SEO", "Marketing", "Improve discoverability through search fundamentals."),
    ("Financial Modeling", "Finance", "Build and explain forecast and valuation models."),
    ("Business Analysis", "Product & Business", "Translate business problems into clear requirements."),
    ("Communication", "Professional Skills", "Explain work clearly and collaborate with others."),
    ("Technical Writing", "Communication", "Write clear product and technical documentation."),
    ("Kotlin", "Mobile Development", "Develop modern Android applications."),
    ("Cybersecurity Fundamentals", "Security", "Apply core security, risk, and incident concepts."),
    ("Data Engineering", "Data", "Build reliable pipelines for analytics and applications."),
    ("Troubleshooting", "IT Operations", "Diagnose technical problems methodically."),
    ("Windows Administration", "IT Operations", "Manage Windows users, devices, and services."),
    ("C#", "Game Development", "Build applications and gameplay systems in C#."),
    ("Game Design", "Game Development", "Shape game rules, feedback, and player experience."),
    ("Prototyping", "Design", "Turn ideas into testable product interactions."),
    ("People Analytics", "People & Business", "Use workforce data to understand people operations."),
]

# Each path is mapped to the skills commonly used in entry and mid-level role descriptions.
# Learners should treat these as a starting point and compare them with local job postings.
CAREERS = [
    ("Backend Developer", "Software Development", "Build APIs, business logic, and reliable data services.", 3, {"Python": 4, "SQL": 3, "API Design": 4, "FastAPI": 3, "Git": 3, "Software Testing": 3}),
    ("Frontend Developer", "Software Development", "Build accessible web interfaces that work across devices.", 3, {"HTML & CSS": 4, "JavaScript": 4, "TypeScript": 3, "React": 4, "Accessibility": 3, "Git": 3}),
    ("Full-Stack Developer", "Software Development", "Build connected frontend experiences and backend services.", 4, {"HTML & CSS": 3, "JavaScript": 3, "React": 3, "Python": 3, "SQL": 3, "API Design": 3, "Git": 3}),
    ("Mobile App Developer", "Software Development", "Create Android applications and connect them to services.", 4, {"Kotlin": 4, "API Design": 3, "Software Testing": 3, "Accessibility": 2, "Git": 3}),
    ("QA Automation Engineer", "Software Development", "Prevent defects with test plans and automated checks.", 3, {"Python": 3, "JavaScript": 2, "Software Testing": 4, "API Design": 3, "CI/CD": 3, "Git": 3}),
    ("Game Developer", "Software Development", "Build gameplay systems and interactive experiences.", 4, {"C#": 4, "Game Design": 3, "Data Structures": 3, "Software Testing": 2, "Git": 3}),
    ("Data Analyst", "Data & AI", "Turn business data into useful analysis and recommendations.", 2, {"SQL": 4, "Excel": 4, "Statistics": 3, "Data Visualization": 4, "Communication": 3}),
    ("Data Scientist", "Data & AI", "Use statistics and machine learning to answer data questions.", 4, {"Python": 4, "SQL": 3, "Statistics": 4, "Machine Learning": 3, "Data Visualization": 3}),
    ("Machine Learning Engineer", "Data & AI", "Build, evaluate, and deploy machine learning systems.", 5, {"Python": 4, "Machine Learning": 4, "Data Structures": 3, "Docker": 3, "Cloud Fundamentals": 3, "Software Testing": 3}),
    ("AI Application Developer", "Data & AI", "Build user-focused products that use generative AI models.", 4, {"Python": 4, "Generative AI": 4, "Prompt Design": 3, "API Design": 3, "Software Testing": 3}),
    ("Data Engineer", "Data & AI", "Build dependable pipelines and data platforms for analytics.", 4, {"Python": 4, "SQL": 4, "Data Engineering": 4, "Cloud Fundamentals": 3, "Docker": 3, "Git": 3}),
    ("Cloud Engineer", "Cloud & Security", "Deploy and operate applications on cloud infrastructure.", 4, {"Linux": 3, "Cloud Fundamentals": 4, "Networking": 3, "Docker": 3, "Monitoring": 3, "Git": 3}),
    ("DevOps Engineer", "Cloud & Security", "Automate software delivery and improve service reliability.", 4, {"Linux": 4, "Docker": 4, "CI/CD": 4, "Cloud Fundamentals": 3, "Monitoring": 4, "Git": 3}),
    ("Cybersecurity Analyst", "Cloud & Security", "Monitor systems, investigate threats, and reduce security risk.", 4, {"Networking": 4, "Linux": 3, "Cybersecurity Fundamentals": 4, "Python": 2, "SQL": 2}),
    ("IT Support Specialist", "Cloud & Security", "Help people resolve device, application, and account problems.", 2, {"Troubleshooting": 4, "Windows Administration": 4, "Networking": 3, "Communication": 4, "Cybersecurity Fundamentals": 2}),
    ("UX/UI Designer", "Design & Product", "Design and test clear, accessible digital experiences.", 3, {"Figma": 4, "UX Research": 4, "Prototyping": 4, "Accessibility": 3, "Communication": 3}),
    ("Product Manager", "Design & Product", "Set product direction and coordinate teams around user outcomes.", 4, {"Product Strategy": 4, "Agile Delivery": 3, "Business Analysis": 3, "UX Research": 3, "Communication": 4}),
    ("Project Manager", "Design & Product", "Coordinate project scope, delivery, risks, and stakeholders.", 3, {"Project Management": 4, "Agile Delivery": 4, "Communication": 4, "Excel": 2, "Business Analysis": 3}),
    ("Business Analyst", "Business & Marketing", "Clarify business needs and support evidence-based decisions.", 3, {"Business Analysis": 4, "SQL": 3, "Excel": 4, "Data Visualization": 3, "Communication": 4}),
    ("Digital Marketing Specialist", "Business & Marketing", "Plan digital campaigns and measure their results.", 2, {"Digital Marketing": 4, "Content Strategy": 4, "SEO": 3, "Data Visualization": 2, "Communication": 3}),
    ("Financial Analyst", "Business & Marketing", "Analyze financial performance and prepare forecasts.", 3, {"Excel": 4, "Financial Modeling": 4, "Statistics": 3, "SQL": 2, "Communication": 3}),
    ("Technical Writer", "Business & Marketing", "Create clear documentation for technical products and users.", 2, {"Technical Writing": 4, "API Design": 2, "Communication": 4, "UX Research": 2, "Git": 2}),
    ("People Analytics Specialist", "Business & Marketing", "Use people data to support fair, informed workforce decisions.", 3, {"People Analytics": 4, "Excel": 4, "Statistics": 3, "Data Visualization": 3, "Communication": 4}),
]

PREREQUISITES = [
    ("React", "JavaScript"), ("TypeScript", "JavaScript"), ("FastAPI", "Python"),
    ("Data Structures", "Python"), ("Machine Learning", "Statistics"),
    ("Machine Learning", "Python"), ("Data Visualization", "Statistics"),
    ("Cloud Fundamentals", "Networking"), ("Docker", "Linux"),
    ("CI/CD", "Git"), ("CI/CD", "Docker"), ("Generative AI", "Python"),
    ("Prompt Design", "Communication"), ("Prototyping", "UX Research"),
    ("Accessibility", "HTML & CSS"), ("Financial Modeling", "Excel"),
    ("SEO", "Digital Marketing"), ("Content Strategy", "Communication"),
    ("Technical Writing", "Communication"), ("Data Engineering", "SQL"),
    ("Data Engineering", "Python"), ("Cybersecurity Fundamentals", "Networking"),
]

PROJECTS = [
    ("Learning Progress API", "Build a secure API for accounts, tasks, and learning progress.", 3, 18, ["Python", "SQL", "FastAPI", "API Design", "Software Testing"], ["Backend Developer", "Full-Stack Developer"]),
    ("Accessible Career Portfolio", "Create a responsive portfolio and check it with keyboard and screen-reader basics.", 2, 12, ["HTML & CSS", "JavaScript", "Accessibility", "React"], ["Frontend Developer", "Full-Stack Developer", "UX/UI Designer"]),
    ("Career Insights Dashboard", "Analyze a public dataset and present clear findings in an interactive dashboard.", 2, 14, ["SQL", "Excel", "Statistics", "Data Visualization"], ["Data Analyst", "Business Analyst", "Financial Analyst"]),
    ("Model Evaluation Notebook", "Train a baseline model, compare metrics, and explain its limits.", 4, 22, ["Python", "Statistics", "Machine Learning", "Data Visualization"], ["Data Scientist", "Machine Learning Engineer"]),
    ("Containerized Web Service", "Package a small service and automate checks before deployment.", 3, 16, ["Docker", "Linux", "CI/CD", "Cloud Fundamentals"], ["Cloud Engineer", "DevOps Engineer", "Machine Learning Engineer"]),
    ("Security Monitoring Lab", "Review a safe sample log, document findings, and propose mitigations.", 3, 14, ["Networking", "Linux", "Cybersecurity Fundamentals", "Python"], ["Cybersecurity Analyst", "IT Support Specialist"]),
    ("Usability Research Sprint", "Interview a few volunteers and turn findings into a tested prototype.", 2, 10, ["UX Research", "Figma", "Prototyping", "Communication"], ["UX/UI Designer", "Product Manager"]),
    ("Digital Campaign Report", "Plan a small campaign and report on search, content, and engagement measures.", 2, 12, ["Digital Marketing", "Content Strategy", "SEO", "Data Visualization"], ["Digital Marketing Specialist"]),
    ("Budget and Forecast Model", "Build a transparent spreadsheet model and document assumptions.", 2, 10, ["Excel", "Financial Modeling", "Statistics", "Communication"], ["Financial Analyst", "Business Analyst"]),
    ("Workforce Trends Brief", "Summarize anonymized workforce data with careful definitions and caveats.", 2, 12, ["People Analytics", "Excel", "Statistics", "Data Visualization"], ["People Analytics Specialist", "Business Analyst"]),
    ("Technical Product Guide", "Write a getting-started guide and review it with a new user.", 2, 8, ["Technical Writing", "API Design", "UX Research", "Communication"], ["Technical Writer", "Backend Developer"]),
    ("Android Habit Tracker", "Build a simple habit tracker with local persistence and accessible forms.", 3, 18, ["Kotlin", "Software Testing", "Accessibility", "API Design"], ["Mobile App Developer"]),
    ("Small Puzzle Game", "Build a playable puzzle with clear feedback and a short test plan.", 3, 20, ["C#", "Game Design", "Data Structures", "Software Testing"], ["Game Developer"]),
    ("Requirements and Delivery Plan", "Turn stakeholder notes into requirements, risks, and an incremental plan.", 2, 8, ["Business Analysis", "Project Management", "Agile Delivery", "Communication"], ["Project Manager", "Product Manager", "Business Analyst"]),
    ("AI Study Assistant", "Create a small AI feature with input limits, structured output, and evaluation examples.", 3, 16, ["Python", "Generative AI", "Prompt Design", "API Design", "Software Testing"], ["AI Application Developer"]),
]

RESOURCES = [
    ("Python Tutorial", "https://docs.python.org/3/tutorial/", "documentation", "Official tutorial for the Python language.", "Python"),
    ("SQLBolt Lessons", "https://sqlbolt.com/", "practice", "Interactive SQL lessons for beginners.", "SQL"),
    ("Pro Git Book", "https://git-scm.com/book/en/v2", "book", "Free guide to Git fundamentals and collaboration.", "Git"),
    ("React Learn", "https://react.dev/learn", "documentation", "Official guide to building React interfaces.", "React"),
    ("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/", "documentation", "Official FastAPI tutorial and reference.", "FastAPI"),
    ("MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Learn", "documentation", "Learning paths for HTML, CSS, and JavaScript.", "HTML & CSS"),
    ("Kaggle Learn", "https://www.kaggle.com/learn", "practice", "Short courses and exercises for data skills.", "Data Visualization"),
    ("Google Cloud Skills Boost", "https://www.cloudskillsboost.google/", "course", "Hands-on learning paths for cloud technologies.", "Cloud Fundamentals"),
    ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613-Learn-design", "documentation", "Official design and prototyping learning resources.", "Figma"),
    ("Google Search Central SEO Guide", "https://developers.google.com/search/docs/fundamentals/seo-starter-guide", "documentation", "Google's SEO fundamentals for website owners.", "SEO"),
]


def main() -> None:
    db = SessionLocal()
    try:
        skills_by_name = {}
        for name, category, description in SKILLS:
            skill = db.scalar(select(Skill).where(Skill.name == name))
            if skill is None:
                skill = Skill(name=name, category=category, description=description)
                db.add(skill)
            else:
                skill.category, skill.description = category, description
            skills_by_name[name] = skill
        db.flush()

        careers_by_name = {}
        for name, category, description, difficulty, requirements in CAREERS:
            career = db.scalar(select(Career).where(Career.name == name))
            if career is None:
                career = Career(name=name)
                db.add(career)
            career.category = category
            career.description = description
            career.difficulty_level = difficulty
            db.flush()
            careers_by_name[name] = career
            for skill_name, level in requirements.items():
                mapping = db.get(CareerSkill, {"career_id": career.id, "skill_id": skills_by_name[skill_name].id})
                importance = 1.5 if level >= 4 else 1.2 if level == 3 else 1.0
                if mapping is None:
                    mapping = CareerSkill(career_id=career.id, skill_id=skills_by_name[skill_name].id)
                    db.add(mapping)
                mapping.required_level = level
                mapping.importance = importance
                mapping.relevance = 1.2 if level >= 4 else 1.0

        for skill_name, prerequisite_name in PREREQUISITES:
            values = {"skill_id": skills_by_name[skill_name].id, "prerequisite_skill_id": skills_by_name[prerequisite_name].id}
            if db.get(SkillPrerequisite, values) is None:
                db.add(SkillPrerequisite(**values))

        for name, description, difficulty, hours, skill_names, career_names in PROJECTS:
            project = db.scalar(select(Project).where(Project.name == name))
            if project is None:
                project = Project(name=name, description=description, difficulty_level=difficulty, estimated_hours=hours)
                db.add(project)
                db.flush()
            else:
                project.description, project.difficulty_level, project.estimated_hours = description, difficulty, hours
            for skill_name in skill_names:
                values = {"project_id": project.id, "skill_id": skills_by_name[skill_name].id}
                if db.get(ProjectSkill, values) is None:
                    db.add(ProjectSkill(**values, importance=1.2))
            for career_name in career_names:
                values = {"career_id": careers_by_name[career_name].id, "project_id": project.id}
                if db.get(CareerProject, values) is None:
                    db.add(CareerProject(**values, relevance=1.2))

        for title, url, resource_type, description, skill_name in RESOURCES:
            resource = db.scalar(select(Resource).where(Resource.title == title))
            if resource is None:
                resource = Resource(title=title, url=url, resource_type=resource_type, description=description)
                db.add(resource)
                db.flush()
            else:
                resource.url, resource.resource_type, resource.description = url, resource_type, description
            values = {"skill_id": skills_by_name[skill_name].id, "resource_id": resource.id}
            if db.get(SkillResource, values) is None:
                db.add(SkillResource(**values))

        db.commit()
        print(f"Seed complete: {len(SKILLS)} skills, {len(CAREERS)} career goals, {len(PROJECTS)} projects, {len(RESOURCES)} resources.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
