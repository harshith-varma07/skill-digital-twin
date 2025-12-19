"""
Database seeding script for initial data.
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.skill import Skill, SkillCategory
from app.models.career import CareerRole, CareerSkillRequirement, ExperienceLevel


async def seed_skill_categories(db: AsyncSession):
    """Seed skill categories."""
    categories = [
        {"name": "Programming Languages", "description": "Core programming languages"},
        {"name": "Web Development", "description": "Web technologies and frameworks"},
        {"name": "Data Science & ML", "description": "Data science and machine learning"},
        {"name": "Databases", "description": "Database technologies"},
        {"name": "Cloud & DevOps", "description": "Cloud platforms and DevOps tools"},
        {"name": "Soft Skills", "description": "Professional soft skills"},
        {"name": "Project Management", "description": "Project management methodologies"},
        {"name": "Design", "description": "UI/UX and design skills"},
    ]
    
    for cat_data in categories:
        result = await db.execute(select(SkillCategory).where(SkillCategory.name == cat_data["name"]))
        if not result.scalar_one_or_none():
            category = SkillCategory(**cat_data)
            db.add(category)
    
    await db.commit()
    print("Skill categories seeded.")


async def seed_skills(db: AsyncSession):
    """Seed skills."""
    # Get category IDs
    result = await db.execute(select(SkillCategory))
    categories = {cat.name: cat.id for cat in result.scalars().all()}
    
    skills = [
        # Programming Languages
        {"name": "Python", "category_id": categories.get("Programming Languages"), "keywords": ["python", "py", "python3"], "description": "General-purpose programming language"},
        {"name": "JavaScript", "category_id": categories.get("Programming Languages"), "keywords": ["js", "javascript", "ecmascript"], "description": "Web scripting language"},
        {"name": "TypeScript", "category_id": categories.get("Programming Languages"), "keywords": ["ts", "typescript"], "description": "Typed superset of JavaScript"},
        {"name": "Java", "category_id": categories.get("Programming Languages"), "keywords": ["java", "jvm"], "description": "Object-oriented programming language"},
        {"name": "C++", "category_id": categories.get("Programming Languages"), "keywords": ["cpp", "c++", "cplusplus"], "description": "High-performance programming language"},
        {"name": "Go", "category_id": categories.get("Programming Languages"), "keywords": ["golang", "go"], "description": "Systems programming language"},
        {"name": "Rust", "category_id": categories.get("Programming Languages"), "keywords": ["rust"], "description": "Memory-safe systems language"},
        {"name": "SQL", "category_id": categories.get("Programming Languages"), "keywords": ["sql", "structured query language"], "description": "Database query language"},
        
        # Web Development
        {"name": "React", "category_id": categories.get("Web Development"), "keywords": ["react", "reactjs", "react.js"], "description": "JavaScript UI library"},
        {"name": "Angular", "category_id": categories.get("Web Development"), "keywords": ["angular", "angularjs"], "description": "TypeScript web framework"},
        {"name": "Vue.js", "category_id": categories.get("Web Development"), "keywords": ["vue", "vuejs", "vue.js"], "description": "Progressive JavaScript framework"},
        {"name": "Node.js", "category_id": categories.get("Web Development"), "keywords": ["node", "nodejs", "node.js"], "description": "JavaScript runtime"},
        {"name": "Django", "category_id": categories.get("Web Development"), "keywords": ["django"], "description": "Python web framework"},
        {"name": "FastAPI", "category_id": categories.get("Web Development"), "keywords": ["fastapi", "fast api"], "description": "Modern Python API framework"},
        {"name": "HTML/CSS", "category_id": categories.get("Web Development"), "keywords": ["html", "css", "html5", "css3"], "description": "Web markup and styling"},
        {"name": "REST APIs", "category_id": categories.get("Web Development"), "keywords": ["rest", "restful", "api"], "description": "RESTful API design"},
        {"name": "GraphQL", "category_id": categories.get("Web Development"), "keywords": ["graphql"], "description": "API query language"},
        
        # Data Science & ML
        {"name": "Machine Learning", "category_id": categories.get("Data Science & ML"), "keywords": ["ml", "machine learning"], "description": "ML algorithms and techniques"},
        {"name": "Deep Learning", "category_id": categories.get("Data Science & ML"), "keywords": ["dl", "deep learning", "neural networks"], "description": "Neural network architectures"},
        {"name": "TensorFlow", "category_id": categories.get("Data Science & ML"), "keywords": ["tensorflow", "tf"], "description": "ML framework by Google"},
        {"name": "PyTorch", "category_id": categories.get("Data Science & ML"), "keywords": ["pytorch", "torch"], "description": "ML framework by Meta"},
        {"name": "Data Analysis", "category_id": categories.get("Data Science & ML"), "keywords": ["data analysis", "analytics"], "description": "Data exploration and analysis"},
        {"name": "Pandas", "category_id": categories.get("Data Science & ML"), "keywords": ["pandas"], "description": "Python data manipulation library"},
        {"name": "NumPy", "category_id": categories.get("Data Science & ML"), "keywords": ["numpy"], "description": "Python numerical computing"},
        {"name": "NLP", "category_id": categories.get("Data Science & ML"), "keywords": ["nlp", "natural language processing"], "description": "Natural Language Processing"},
        {"name": "Computer Vision", "category_id": categories.get("Data Science & ML"), "keywords": ["cv", "computer vision", "image processing"], "description": "Computer Vision techniques"},
        
        # Databases
        {"name": "PostgreSQL", "category_id": categories.get("Databases"), "keywords": ["postgres", "postgresql"], "description": "Relational database"},
        {"name": "MySQL", "category_id": categories.get("Databases"), "keywords": ["mysql"], "description": "Relational database"},
        {"name": "MongoDB", "category_id": categories.get("Databases"), "keywords": ["mongo", "mongodb"], "description": "NoSQL document database"},
        {"name": "Redis", "category_id": categories.get("Databases"), "keywords": ["redis"], "description": "In-memory data store"},
        {"name": "Elasticsearch", "category_id": categories.get("Databases"), "keywords": ["elasticsearch", "elastic"], "description": "Search and analytics engine"},
        
        # Cloud & DevOps
        {"name": "AWS", "category_id": categories.get("Cloud & DevOps"), "keywords": ["aws", "amazon web services"], "description": "Amazon Web Services"},
        {"name": "Azure", "category_id": categories.get("Cloud & DevOps"), "keywords": ["azure", "microsoft azure"], "description": "Microsoft Azure"},
        {"name": "GCP", "category_id": categories.get("Cloud & DevOps"), "keywords": ["gcp", "google cloud"], "description": "Google Cloud Platform"},
        {"name": "Docker", "category_id": categories.get("Cloud & DevOps"), "keywords": ["docker", "containers"], "description": "Containerization platform"},
        {"name": "Kubernetes", "category_id": categories.get("Cloud & DevOps"), "keywords": ["k8s", "kubernetes"], "description": "Container orchestration"},
        {"name": "CI/CD", "category_id": categories.get("Cloud & DevOps"), "keywords": ["ci/cd", "cicd", "continuous integration"], "description": "Continuous Integration/Deployment"},
        {"name": "Git", "category_id": categories.get("Cloud & DevOps"), "keywords": ["git", "version control"], "description": "Version control system"},
        {"name": "Linux", "category_id": categories.get("Cloud & DevOps"), "keywords": ["linux", "unix"], "description": "Linux administration"},
        {"name": "Terraform", "category_id": categories.get("Cloud & DevOps"), "keywords": ["terraform", "iac"], "description": "Infrastructure as Code"},
        
        # Soft Skills
        {"name": "Communication", "category_id": categories.get("Soft Skills"), "keywords": ["communication", "verbal", "written"], "description": "Professional communication"},
        {"name": "Leadership", "category_id": categories.get("Soft Skills"), "keywords": ["leadership", "lead", "leading"], "description": "Team leadership"},
        {"name": "Problem Solving", "category_id": categories.get("Soft Skills"), "keywords": ["problem solving", "analytical"], "description": "Analytical problem solving"},
        {"name": "Teamwork", "category_id": categories.get("Soft Skills"), "keywords": ["teamwork", "collaboration"], "description": "Team collaboration"},
        {"name": "Time Management", "category_id": categories.get("Soft Skills"), "keywords": ["time management", "organization"], "description": "Time and task management"},
        
        # Project Management
        {"name": "Agile", "category_id": categories.get("Project Management"), "keywords": ["agile", "scrum", "kanban"], "description": "Agile methodologies"},
        {"name": "Scrum", "category_id": categories.get("Project Management"), "keywords": ["scrum", "sprint"], "description": "Scrum framework"},
        {"name": "JIRA", "category_id": categories.get("Project Management"), "keywords": ["jira"], "description": "Project tracking tool"},
    ]
    
    for skill_data in skills:
        result = await db.execute(select(Skill).where(Skill.name == skill_data["name"]))
        if not result.scalar_one_or_none():
            skill = Skill(**skill_data)
            db.add(skill)
    
    await db.commit()
    print("Skills seeded.")


async def seed_career_roles(db: AsyncSession):
    """Seed career roles with skill requirements."""
    # Get skill IDs
    result = await db.execute(select(Skill))
    skills = {skill.name: skill.id for skill in result.scalars().all()}
    
    career_roles = [
        {
            "role": {
                "title": "Full Stack Developer",
                "description": "Develops both frontend and backend components of web applications",
                "industry": "Technology",
                "domain": "Software Development",
                "experience_level": ExperienceLevel.MID,
                "salary_min": 80000,
                "salary_max": 150000,
                "demand_score": 0.9,
                "growth_rate": 0.15,
                "responsibilities": [
                    "Develop frontend user interfaces",
                    "Build backend APIs and services",
                    "Design database schemas",
                    "Deploy and maintain applications"
                ]
            },
            "requirements": [
                {"skill": "JavaScript", "level": 0.7, "importance": 0.9, "mandatory": True},
                {"skill": "React", "level": 0.6, "importance": 0.8, "mandatory": False},
                {"skill": "Node.js", "level": 0.6, "importance": 0.8, "mandatory": False},
                {"skill": "Python", "level": 0.5, "importance": 0.6, "mandatory": False},
                {"skill": "SQL", "level": 0.6, "importance": 0.7, "mandatory": True},
                {"skill": "Git", "level": 0.7, "importance": 0.8, "mandatory": True},
                {"skill": "REST APIs", "level": 0.7, "importance": 0.8, "mandatory": True},
                {"skill": "HTML/CSS", "level": 0.7, "importance": 0.7, "mandatory": True},
            ]
        },
        {
            "role": {
                "title": "Data Scientist",
                "description": "Analyzes complex data to help guide business decisions",
                "industry": "Technology",
                "domain": "Data Science",
                "experience_level": ExperienceLevel.MID,
                "salary_min": 90000,
                "salary_max": 160000,
                "demand_score": 0.95,
                "growth_rate": 0.22,
                "responsibilities": [
                    "Analyze large datasets",
                    "Build predictive models",
                    "Create data visualizations",
                    "Present insights to stakeholders"
                ]
            },
            "requirements": [
                {"skill": "Python", "level": 0.8, "importance": 0.95, "mandatory": True},
                {"skill": "Machine Learning", "level": 0.7, "importance": 0.9, "mandatory": True},
                {"skill": "Data Analysis", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "SQL", "level": 0.7, "importance": 0.8, "mandatory": True},
                {"skill": "Pandas", "level": 0.7, "importance": 0.8, "mandatory": True},
                {"skill": "NumPy", "level": 0.6, "importance": 0.7, "mandatory": False},
                {"skill": "TensorFlow", "level": 0.5, "importance": 0.6, "mandatory": False},
                {"skill": "Communication", "level": 0.7, "importance": 0.7, "mandatory": True},
            ]
        },
        {
            "role": {
                "title": "DevOps Engineer",
                "description": "Manages infrastructure, CI/CD pipelines, and deployment processes",
                "industry": "Technology",
                "domain": "Infrastructure",
                "experience_level": ExperienceLevel.MID,
                "salary_min": 85000,
                "salary_max": 155000,
                "demand_score": 0.88,
                "growth_rate": 0.18,
                "responsibilities": [
                    "Manage CI/CD pipelines",
                    "Automate infrastructure",
                    "Monitor system performance",
                    "Ensure system reliability"
                ]
            },
            "requirements": [
                {"skill": "Docker", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "Kubernetes", "level": 0.7, "importance": 0.85, "mandatory": True},
                {"skill": "AWS", "level": 0.7, "importance": 0.85, "mandatory": False},
                {"skill": "CI/CD", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "Linux", "level": 0.8, "importance": 0.85, "mandatory": True},
                {"skill": "Python", "level": 0.5, "importance": 0.6, "mandatory": False},
                {"skill": "Terraform", "level": 0.6, "importance": 0.7, "mandatory": False},
                {"skill": "Git", "level": 0.8, "importance": 0.8, "mandatory": True},
            ]
        },
        {
            "role": {
                "title": "Machine Learning Engineer",
                "description": "Builds and deploys machine learning models at scale",
                "industry": "Technology",
                "domain": "AI/ML",
                "experience_level": ExperienceLevel.SENIOR,
                "salary_min": 120000,
                "salary_max": 200000,
                "demand_score": 0.92,
                "growth_rate": 0.25,
                "responsibilities": [
                    "Design ML system architecture",
                    "Train and optimize models",
                    "Deploy models to production",
                    "Monitor model performance"
                ]
            },
            "requirements": [
                {"skill": "Python", "level": 0.9, "importance": 0.95, "mandatory": True},
                {"skill": "Machine Learning", "level": 0.85, "importance": 0.95, "mandatory": True},
                {"skill": "Deep Learning", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "TensorFlow", "level": 0.7, "importance": 0.8, "mandatory": False},
                {"skill": "PyTorch", "level": 0.7, "importance": 0.8, "mandatory": False},
                {"skill": "Docker", "level": 0.6, "importance": 0.7, "mandatory": True},
                {"skill": "AWS", "level": 0.6, "importance": 0.7, "mandatory": False},
                {"skill": "SQL", "level": 0.6, "importance": 0.6, "mandatory": False},
            ]
        },
        {
            "role": {
                "title": "Frontend Developer",
                "description": "Specializes in building user interfaces and client-side applications",
                "industry": "Technology",
                "domain": "Software Development",
                "experience_level": ExperienceLevel.JUNIOR,
                "salary_min": 60000,
                "salary_max": 120000,
                "demand_score": 0.85,
                "growth_rate": 0.12,
                "responsibilities": [
                    "Build responsive UIs",
                    "Implement designs",
                    "Optimize performance",
                    "Write unit tests"
                ]
            },
            "requirements": [
                {"skill": "JavaScript", "level": 0.8, "importance": 0.95, "mandatory": True},
                {"skill": "React", "level": 0.7, "importance": 0.85, "mandatory": False},
                {"skill": "TypeScript", "level": 0.6, "importance": 0.7, "mandatory": False},
                {"skill": "HTML/CSS", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "Git", "level": 0.6, "importance": 0.7, "mandatory": True},
                {"skill": "REST APIs", "level": 0.5, "importance": 0.6, "mandatory": False},
            ]
        },
        {
            "role": {
                "title": "Backend Developer",
                "description": "Builds server-side applications and APIs",
                "industry": "Technology",
                "domain": "Software Development",
                "experience_level": ExperienceLevel.MID,
                "salary_min": 75000,
                "salary_max": 140000,
                "demand_score": 0.87,
                "growth_rate": 0.14,
                "responsibilities": [
                    "Design and build APIs",
                    "Manage databases",
                    "Implement business logic",
                    "Ensure security"
                ]
            },
            "requirements": [
                {"skill": "Python", "level": 0.7, "importance": 0.8, "mandatory": False},
                {"skill": "Java", "level": 0.7, "importance": 0.8, "mandatory": False},
                {"skill": "SQL", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "REST APIs", "level": 0.8, "importance": 0.9, "mandatory": True},
                {"skill": "PostgreSQL", "level": 0.7, "importance": 0.8, "mandatory": False},
                {"skill": "Docker", "level": 0.5, "importance": 0.6, "mandatory": False},
                {"skill": "Git", "level": 0.7, "importance": 0.8, "mandatory": True},
            ]
        },
    ]
    
    for career_data in career_roles:
        role_info = career_data["role"]
        
        # Check if role exists
        result = await db.execute(select(CareerRole).where(CareerRole.title == role_info["title"]))
        existing_role = result.scalar_one_or_none()
        
        if existing_role:
            continue
        
        # Create role
        role = CareerRole(**role_info)
        db.add(role)
        await db.flush()
        
        # Add skill requirements
        for req in career_data["requirements"]:
            skill_id = skills.get(req["skill"])
            if skill_id:
                requirement = CareerSkillRequirement(
                    career_role_id=role.id,
                    skill_id=skill_id,
                    required_level=req["level"],
                    importance=req["importance"],
                    is_mandatory=req["mandatory"],
                    category="technical"
                )
                db.add(requirement)
    
    await db.commit()
    print("Career roles seeded.")


async def seed_database():
    """Run all seed functions."""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        await seed_skill_categories(db)
        await seed_skills(db)
        await seed_career_roles(db)
    
    print("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
