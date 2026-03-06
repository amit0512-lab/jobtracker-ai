import spacy
import re
from pathlib import Path

# Model load karo — ek baar hi load hoga
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model nahi mila. Run: python -m spacy download en_core_web_sm")


# ─── Common Tech Skills Dictionary ────────────────────────────
TECH_SKILLS = {
    "languages": [
        "python", "javascript", "typescript", "java", "c++", "c#",
        "go", "rust", "php", "ruby", "swift", "kotlin", "scala",
        "html", "css", "sql", "r", "matlab", "perl", "dart"
    ],
    "frameworks": [
        "fastapi", "django", "flask", "react", "angular", "vue",
        "spring", "express", "nextjs", "nestjs", "laravel",
        "nodejs", "reactjs", "vuejs", "bootstrap", "tailwind",
        "jquery", "redux", "svelte", "ember", "backbone"
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "sqlite", "cassandra", "dynamodb", "oracle", "mariadb",
        "neo4j", "couchdb", "firebase", "supabase"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
        "terraform", "ansible", "git", "github", "gitlab", "ci/cd",
        "circleci", "travis", "bitbucket", "heroku", "vercel",
        "netlify", "cloudflare", "nginx", "apache"
    ],
    "data_ml": [
        "machine learning", "deep learning", "nlp", "tensorflow",
        "pytorch", "scikit-learn", "pandas", "numpy", "spark",
        "hadoop", "airflow", "kafka", "data science", "analytics",
        "tableau", "power bi", "jupyter", "matplotlib", "seaborn"
    ],
    "testing": [
        "jest", "pytest", "junit", "selenium", "cypress",
        "mocha", "chai", "testing", "unit testing", "integration testing"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "agile", "scrum", "project management", "collaboration"
    ],
    "other": [
        "rest api", "graphql", "microservices", "agile", "scrum",
        "sqlalchemy", "alembic", "celery", "rabbitmq", "kafka",
        "api", "backend", "frontend", "full stack", "devops",
        "linux", "unix", "windows", "macos", "bash", "powershell",
        "oauth", "jwt", "authentication", "authorization", "security"
    ]
}

ALL_SKILLS = [skill for category in TECH_SKILLS.values() for skill in category]


class ResumeParser:

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """File se plain text nikalo"""
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return ResumeParser._extract_from_pdf(file_path)
        elif ext in [".doc", ".docx"]:
            return ResumeParser._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        try:
            import pypdf
            text = ""
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        except ImportError:
            raise RuntimeError("pypdf install karo: pip install pypdf")

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            raise RuntimeError("python-docx install karo: pip install python-docx")

    # ─── Skills Extract ───────────────────────────────────────

    @staticmethod
    def extract_skills(text: str) -> list[str]:
        """Resume text se tech skills dhundho - Improved with fuzzy matching"""
        text_lower = text.lower()
        found_skills = []

        for skill in ALL_SKILLS:
            # Word boundary check — "go" ko "django" mein na dhundhe
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())
        
        # Also check for common variations
        skill_variations = {
            'nodejs': ['node.js', 'node js', 'nodejs'],
            'reactjs': ['react.js', 'react js', 'reactjs', 'react'],
            'vuejs': ['vue.js', 'vue js', 'vuejs', 'vue'],
            'nextjs': ['next.js', 'next js', 'nextjs'],
            'postgresql': ['postgres', 'postgresql', 'psql'],
            'mongodb': ['mongo', 'mongodb', 'mongo db'],
            'javascript': ['js', 'javascript', 'java script'],
            'typescript': ['ts', 'typescript', 'type script'],
            'machine learning': ['ml', 'machine learning', 'machinelearning'],
            'artificial intelligence': ['ai', 'artificial intelligence'],
            'natural language processing': ['nlp', 'natural language processing'],
        }
        
        for canonical, variations in skill_variations.items():
            for variant in variations:
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(canonical.title())
                    break  # Only add once

        return list(set(found_skills))

    # ─── Keywords Extract ─────────────────────────────────────

    @staticmethod
    def extract_keywords(text: str, top_n: int = 20) -> list[str]:
        """spaCy se important keywords nikalo - Improved with noise filtering"""
        doc = nlp(text)
        keywords = []
        
        # Words to ignore (common noise in job descriptions)
        noise_words = {
            'year', 'years', 'month', 'months', 'day', 'days', 'week', 'weeks',
            'lakh', 'lakhs', 'lpa', 'ctc', 'salary', 'package', 'compensation',
            'rupee', 'rupees', 'dollar', 'dollars', 'inr', 'usd', 'eur',
            'minimum', 'maximum', 'range', 'between', 'approximately', 'around',
            'company', 'role', 'position', 'job', 'work', 'candidate', 'applicant',
            'requirement', 'requirements', 'qualification', 'qualifications',
            'benefit', 'benefits', 'perk', 'perks', 'location', 'office',
            'time', 'date', 'hour', 'hours', 'shift', 'schedule',
            'number', 'amount', 'total', 'sum', 'count', 'quantity'
        }

        for token in doc:
            # Skip if it's a number or contains only digits
            if token.like_num or token.text.isdigit():
                continue
            
            # Skip if it's a currency symbol or number-like
            if token.is_currency or re.match(r'^\d+[\.,]?\d*$', token.text):
                continue
            
            # Skip common noise words
            if token.lemma_.lower() in noise_words:
                continue
            
            # Only keep meaningful nouns, proper nouns, and adjectives
            if (
                token.pos_ in ["NOUN", "PROPN", "ADJ"]
                and not token.is_stop
                and not token.is_punct
                and len(token.text) > 2
                and not token.text.lower() in noise_words
            ):
                # Additional check: skip if it looks like a number with units
                if not re.match(r'^\d+[a-z]*$', token.text.lower()):
                    keywords.append(token.lemma_.lower())

        # Frequency ke hisaab se sort karo
        from collections import Counter
        freq = Counter(keywords)
        
        # Filter out very common words that appear too frequently (likely noise)
        total_words = len(keywords)
        filtered_keywords = []
        for word, count in freq.most_common(top_n * 2):  # Get more initially
            # Skip if word appears too frequently (>20% of text) - likely filler
            if count / total_words < 0.2:
                filtered_keywords.append(word)
            if len(filtered_keywords) >= top_n:
                break
        
        return filtered_keywords

    # ─── Experience Extract ───────────────────────────────────

    @staticmethod
    def extract_experience(text: str) -> list[dict]:
        """Experience sections dhundho"""
        experience = []
        lines = text.split('\n')

        # Common experience section headers
        exp_headers = ['experience', 'work experience', 'employment', 'work history']
        edu_headers = ['education', 'qualification', 'academic']

        in_experience = False
        current_block = []

        for line in lines:
            line_lower = line.lower().strip()

            if any(h in line_lower for h in exp_headers):
                in_experience = True
                continue
            elif any(h in line_lower for h in edu_headers) and in_experience:
                in_experience = False
                if current_block:
                    experience.append({"raw": " ".join(current_block)})
                    current_block = []
                continue

            if in_experience and line.strip():
                current_block.append(line.strip())

                # Har 4 lines pe ek block banao
                if len(current_block) >= 4:
                    experience.append({"raw": " ".join(current_block)})
                    current_block = []

        if current_block:
            experience.append({"raw": " ".join(current_block)})

        return experience[:5]  # Max 5 experience blocks

    # ─── Extract Years of Experience ──────────────────────────

    @staticmethod
    def extract_years_of_experience(text: str) -> float:
        """Extract total years of experience from text"""
        text_lower = text.lower()
        
        # Patterns to match experience mentions
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:in|with)',
            r'total\s+(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)',
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years.append(float(match))
                except:
                    pass
        
        # Return the maximum mentioned (most likely total experience)
        return max(years) if years else 0.0

    # ─── Education Extract ────────────────────────────────────

    @staticmethod
    def extract_education(text: str) -> list[dict]:
        """Education details dhundho"""
        education = []
        doc = nlp(text)

        # Degree patterns
        degree_patterns = [
            r'\b(B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|MBA|BCA|MCA|PhD|B\.?Com)\b',
            r'\b(Bachelor|Master|Doctor)\w*\s+of\s+\w+',
        ]

        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Match ke aaspaas 100 chars context lo
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                education.append({
                    "degree": match.group(),
                    "context": context
                })

        return education[:3]  # Max 3 education entries

    # ─── Full Parse ───────────────────────────────────────────

    @staticmethod
    def parse_resume(file_path: str) -> dict:
        """Ek call mein poora resume parse karo"""
        text = ResumeParser.extract_text_from_file(file_path)

        return {
            "raw_text": text,
            "skills": ResumeParser.extract_skills(text),
            "keywords": ResumeParser.extract_keywords(text),
            "experience": ResumeParser.extract_experience(text),
            "education": ResumeParser.extract_education(text),
        }