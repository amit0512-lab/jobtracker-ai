import os
import httpx
from typing import Optional
import random
import re


class CoverLetterGenerator:
    """
    AI-powered cover letter generator using OpenAI API
    Falls back to template-based generation if API key not available
    Includes humanization post-processing to reduce AI detection
    """

    @staticmethod
    def _humanize_text(text: str) -> str:
        """
        Apply transformations to make AI-generated text appear more human-written.
        Uses techniques similar to paraphrasing tools.
        """
        
        # Common AI phrases to replace with more natural alternatives
        replacements = {
            # Overly formal phrases
            r'\bI am writing to express\b': ['I\'m reaching out to share', 'I wanted to express', 'I\'m writing to share'],
            r'\bI am confident that\b': ['I believe', 'I\'m confident', 'I think'],
            r'\bI would be\b': ['I\'d be', 'I would be', 'I\'d love to be'],
            r'\bI have developed\b': ['I\'ve built', 'I\'ve developed', 'I\'ve gained'],
            r'\bI am particularly\b': ['I\'m especially', 'I\'m particularly', 'What really interests me is'],
            r'\bI am excited\b': ['I\'m excited', 'I\'m really excited', 'I\'m genuinely excited'],
            r'\bthroughout my career\b': ['in my experience', 'over the years', 'in my work'],
            r'\bdemonstrated the ability\b': ['shown I can', 'proven I can', 'been able'],
            r'\bI would welcome the opportunity\b': ['I\'d love the chance', 'I\'d welcome the opportunity', 'I\'d be happy'],
            r'\bthank you for considering\b': ['thanks for considering', 'thank you for reviewing', 'I appreciate you considering'],
            r'\bI look forward to\b': ['I\'m looking forward to', 'Looking forward to', 'I\'d love to'],
            
            # Generic corporate speak
            r'\bleverag(e|ing)\b': ['use', 'apply', 'work with'],
            r'\bsynergy\b': ['collaboration', 'teamwork', 'working together'],
            r'\bparadigm\b': ['approach', 'method', 'way'],
            r'\brobust\b': ['strong', 'solid', 'reliable'],
            r'\bseamlessly\b': ['smoothly', 'effectively', 'well'],
            r'\bstakeholders\b': ['team members', 'colleagues', 'partners'],
        }
        
        # Apply random replacements
        for pattern, alternatives in replacements.items():
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                if random.random() > 0.3:  # 70% chance to replace
                    replacement = random.choice(alternatives)
                    # Preserve original capitalization
                    if match.group(0)[0].isupper():
                        replacement = replacement[0].upper() + replacement[1:]
                    text = text[:match.start()] + replacement + text[match.end():]
        
        # Add natural imperfections
        sentences = text.split('. ')
        
        # Occasionally start sentences with conjunctions (more human-like)
        for i in range(1, len(sentences)):
            if random.random() > 0.85 and not sentences[i].startswith(('And', 'But', 'So')):
                starters = ['And ', 'Plus, ', 'Also, ']
                if random.random() > 0.7:
                    sentences[i] = random.choice(starters) + sentences[i][0].lower() + sentences[i][1:]
        
        # Vary punctuation slightly
        text = '. '.join(sentences)
        
        # Add occasional em dashes for more natural flow
        text = re.sub(r' - ', ' — ', text)
        
        # Ensure contractions are used
        contraction_map = {
            r'\bI am\b': 'I\'m',
            r'\bI have\b': 'I\'ve',
            r'\bI would\b': 'I\'d',
            r'\bI will\b': 'I\'ll',
            r'\bthat is\b': 'that\'s',
            r'\bit is\b': 'it\'s',
            r'\bwhat is\b': 'what\'s',
        }
        
        for pattern, contraction in contraction_map.items():
            if random.random() > 0.2:  # 80% chance to use contraction
                text = re.sub(pattern, contraction, text, flags=re.IGNORECASE)
        
        return text

    @staticmethod
    async def generate(
        resume_text: str,
        job_title: str,
        company: str,
        job_description: str,
        tone: str = "professional",
        user_name: Optional[str] = None
    ) -> dict:
        """
        Generate personalized cover letter
        
        Args:
            resume_text: Full resume content
            job_title: Job position title
            company: Company name
            job_description: Full JD text
            tone: professional, enthusiastic, creative, formal
            user_name: User's full name
            
        Returns:
            dict with 'content' and 'word_count'
        """
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key and api_key != "your-openai-api-key-here":
            try:
                return await CoverLetterGenerator._generate_with_ai(
                    resume_text, job_title, company, job_description, tone, user_name, api_key
                )
            except Exception as e:
                print(f"AI generation failed: {e}, falling back to template")
                return CoverLetterGenerator._generate_template(
                    resume_text, job_title, company, job_description, tone, user_name
                )
        else:
            return CoverLetterGenerator._generate_template(
                resume_text, job_title, company, job_description, tone, user_name
            )

    @staticmethod
    async def _generate_with_ai(
        resume_text: str,
        job_title: str,
        company: str,
        job_description: str,
        tone: str,
        user_name: Optional[str],
        api_key: str
    ) -> dict:
        """Generate cover letter using OpenAI API"""
        
        tone_instructions = {
            "professional": "Write naturally and professionally. Use contractions (I'm, I've). Mix short and long sentences. Be confident without sounding robotic.",
            "enthusiastic": "Show genuine excitement without overdoing it. Be warm and personable. Use natural language, not corporate speak.",
            "creative": "Be engaging and memorable. Tell a brief story or use a unique angle. Stay professional but show personality.",
            "formal": "Be respectful and polished, but still sound human. Use some contractions. Avoid being too stiff or robotic."
        }
        
        prompt = f"""You are writing a cover letter as a real job candidate. Write naturally like a human would - with personality, slight imperfections, and authentic voice.

**Job Details:**
- Position: {job_title}
- Company: {company}

**Job Description:**
{job_description[:1500]}

**Candidate's Resume:**
{resume_text[:2000]}

**Tone:** {tone_instructions.get(tone, tone_instructions['professional'])}

**CRITICAL - Write Like a Human:**
- Use contractions naturally (I'm, I've, I'd)
- Vary sentence length - mix short and long sentences
- Include personal pronouns and first-person perspective
- Add subtle personality and authentic enthusiasm
- Use specific examples, not generic statements
- Avoid overly formal or robotic phrasing
- Don't use buzzwords excessively (synergy, leverage, etc.)
- Write conversationally but professionally
- Include natural transitions between ideas
- Show genuine interest, not templated enthusiasm

Write a 250-350 word cover letter with 3-4 paragraphs:
1. Opening: Personal connection or genuine interest (not generic)
2. Body: 2-3 specific relevant experiences/skills with brief context
3. Company fit: Why this company/role specifically interests you
4. Closing: Natural call to action

Format:
- Start: "Dear Hiring Manager," or "Dear [Company] Team,"
- End: "Sincerely,\\n[Your Name]"
- NO address, date, or contact info
- Write as if you're genuinely excited about this opportunity

Write naturally and authentically:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a real job seeker writing your own cover letter. Write naturally with personality, using contractions, varied sentence structure, and authentic voice. Avoid corporate jargon and robotic phrasing."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.9,  # Higher for more natural variation
                    "max_tokens": 600,
                    "presence_penalty": 0.6,  # Encourage diverse vocabulary
                    "frequency_penalty": 0.3  # Reduce repetition
                }
            )
            
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Apply humanization post-processing
            content = CoverLetterGenerator._humanize_text(content)
            
            # Replace placeholder name if provided
            if user_name and "[Your Name]" in content:
                content = content.replace("[Your Name]", user_name)
            
            word_count = len(content.split())
            
            return {
                "content": content,
                "word_count": word_count
            }

    @staticmethod
    def _generate_template(
        resume_text: str,
        job_title: str,
        company: str,
        job_description: str,
        tone: str,
        user_name: Optional[str]
    ) -> dict:
        """Fallback template-based generation with human-like variations"""
        
        # Extract key skills from resume (simple keyword matching)
        skills = []
        skill_keywords = ["python", "javascript", "react", "fastapi", "sql", "docker", "aws", "api", "database", "node", "typescript", "java"]
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()
        
        for skill in skill_keywords:
            if skill in resume_lower and skill in jd_lower:
                skills.append(skill.capitalize())
        
        skills_text = ", ".join(skills[:3]) if skills else "software development"
        
        # Human-like variations for different tones
        openings = {
            "professional": f"I'm writing to express my interest in the {job_title} position at {company}. When I came across this opportunity, it immediately stood out to me.",
            "enthusiastic": f"I'm excited to apply for the {job_title} role at {company}! This position aligns perfectly with what I've been looking for in my next career move.",
            "creative": f"I've been following {company}'s work for a while now, and when I saw the {job_title} opening, I knew I had to apply.",
            "formal": f"I am writing to apply for the {job_title} position at {company}. I believe my background makes me a strong candidate for this role."
        }
        
        # Add natural variations to body paragraphs
        body_variations = [
            f"Over the past few years, I've developed strong skills in {skills_text}, which I've used to deliver real results in my previous roles. I'm particularly drawn to how {company} approaches these technologies.",
            f"My experience with {skills_text} has given me a solid foundation that matches well with what you're looking for. I've consistently worked on projects that required both technical depth and practical problem-solving.",
            f"I've spent considerable time working with {skills_text}, and I'm confident these skills align with your needs. What excites me most is the opportunity to apply this experience at {company}."
        ]
        
        closing_variations = [
            f"I'd love the chance to discuss how my background could contribute to {company}'s goals. Thanks for considering my application - I'm looking forward to hearing from you.",
            f"I'm genuinely interested in this opportunity and would welcome the chance to talk more about how I can contribute to your team. Thank you for your time and consideration.",
            f"I'd be thrilled to bring my skills to {company} and contribute to your team's success. I appreciate you taking the time to review my application."
        ]
        
        import random
        random.seed(hash(company + job_title) % 1000)  # Consistent but varied per job
        
        opening = openings.get(tone, openings["professional"])
        body = random.choice(body_variations)
        closing = random.choice(closing_variations)
        name_line = user_name if user_name else "[Your Name]"
        
        content = f"""Dear Hiring Manager,

{opening}

{body} I've always believed that the best work happens when you're genuinely interested in what you're building, and that's exactly what I see in this role.

What really appeals to me about {company} is the opportunity to work on meaningful projects while continuing to grow professionally. I'm confident I can hit the ground running and make valuable contributions to your team.

{closing}

Sincerely,
{name_line}"""

        # Apply humanization to template as well
        content = CoverLetterGenerator._humanize_text(content)
        
        word_count = len(content.split())
        
        return {
            "content": content,
            "word_count": word_count
        }
