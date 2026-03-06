import re
import spacy
from app.services.nlp.resume_parser import ResumeParser, ALL_SKILLS, nlp


class JDMatcher:

    @staticmethod
    def calculate_match_score(resume_text: str, jd_text: str) -> dict:
        """
        Resume vs JD match karo - With experience matching
        Returns: score, matched keywords, missing keywords, suggestions
        """
        # Normalize text - CASE INSENSITIVE
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        # Extract years of experience
        resume_years = ResumeParser.extract_years_of_experience(resume_text)
        jd_years = ResumeParser.extract_years_of_experience(jd_text)
        
        # Extract skills from both - ALL LOWERCASE for comparison
        resume_skills = set([s.lower() for s in ResumeParser.extract_skills(resume_text)])
        jd_skills = set([s.lower() for s in ResumeParser.extract_skills(jd_text)])

        # Extract keywords - ALL LOWERCASE
        resume_keywords = set([kw.lower() for kw in ResumeParser.extract_keywords(resume_text, top_n=50)])
        jd_keywords = set([kw.lower() for kw in ResumeParser.extract_keywords(jd_text, top_n=30)])

        # Extract important terms - already lowercase
        jd_important_words = JDMatcher._extract_important_terms(jd_lower)
        resume_important_words = JDMatcher._extract_important_terms(resume_lower)

        # NEW: Direct text search for skills that might be missed by spaCy
        for jd_skill in jd_skills:
            pattern = r'\b' + re.escape(jd_skill) + r'\b'
            if re.search(pattern, resume_lower, re.IGNORECASE):
                resume_skills.add(jd_skill)
        
        for jd_kw in jd_keywords:
            pattern = r'\b' + re.escape(jd_kw) + r'\b'
            if re.search(pattern, resume_lower, re.IGNORECASE):
                resume_keywords.add(jd_kw)

        # Calculate matches
        matched_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills.difference(resume_skills)

        matched_keywords = resume_keywords.intersection(jd_keywords)
        missing_keywords = jd_keywords.difference(resume_keywords)
        
        matched_terms = resume_important_words.intersection(jd_important_words)
        missing_terms = jd_important_words.difference(resume_important_words)
        
        # COMPREHENSIVE NOISE FILTER - Apply to BOTH matched and missing
        noise_filter = {
            # Time/Date related
            'year', 'years', 'month', 'months', 'day', 'days', 'week', 'weeks',
            'time', 'date', 'hour', 'hours', 'shift', 'schedule', 'timing',
            
            # Money/Compensation
            'lakh', 'lakhs', 'lpa', 'ctc', 'salary', 'package', 'compensation',
            'rupee', 'rupees', 'dollar', 'dollars', 'inr', 'usd', 'eur', 'gbp',
            'minimum', 'maximum', 'range', 'between', 'approximately', 'around',
            
            # Generic job terms
            'company', 'role', 'position', 'job', 'work', 'candidate', 'applicant',
            'requirement', 'requirements', 'qualification', 'qualifications',
            'benefit', 'benefits', 'perk', 'perks', 'location', 'office',
            'number', 'amount', 'total', 'sum', 'count', 'quantity',
            'experience', 'skill', 'ability', 'knowledge', 'understanding',
            'opportunity', 'growth', 'career', 'development', 'learning',
            'environment', 'culture', 'value', 'mission', 'vision',
            'team', 'member', 'individual', 'person', 'people', 'staff',
            'level', 'senior', 'junior', 'mid', 'entry', 'lead',
            
            # Education terms (NOT technical skills)
            'bachelor', 'bachelors', 'master', 'masters', 'degree', 'diploma',
            'education', 'graduate', 'undergraduate', 'phd', 'doctorate',
            'college', 'university', 'school', 'institute', 'academy',
            'certification', 'certified', 'certificate',
            
            # Location names (Indian cities + common company names)
            'bangalore', 'bengaluru', 'mumbai', 'delhi', 'hyderabad', 'chennai',
            'pune', 'kolkata', 'ahmedabad', 'jaipur', 'surat', 'lucknow',
            'kanpur', 'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam',
            'noida', 'gurgaon', 'gurugram', 'chandigarh', 'goa', 'kochi',
            'foxo', 'tcs', 'infosys', 'wipro', 'accenture', 'cognizant',
            
            # Generic adjectives
            'good', 'excellent', 'strong', 'basic', 'advanced', 'proficient',
            'working', 'hands', 'plus', 'must', 'should', 'need', 'require',
            'prefer', 'desired', 'nice', 'bonus', 'optional', 'mandatory',
            'flexible', 'remote', 'hybrid', 'onsite', 'fulltime', 'parttime',
            'contract', 'permanent', 'temporary', 'freelance', 'freelancer',
            
            # Generic business terms
            'product', 'service', 'customer', 'client', 'user',
            'business', 'industry', 'market', 'sector', 'domain',
            'process', 'system', 'solution', 'platform', 'application',
            
            # Generic verbs
            'design', 'develop', 'implement', 'build', 'create', 'maintain',
            'manage', 'lead', 'coordinate', 'collaborate', 'communicate',
            'ensure', 'provide', 'support', 'assist', 'help', 'contribute',
            'work', 'working', 'worked', 'make', 'making', 'made',
            
            # Common words
            'description', 'required', 'preferred', 'looking', 'seeking',
            'join', 'joining', 'immediate', 'urgent', 'apply', 'application',
            'resume', 'cv', 'profile', 'portfolio', 'reference', 'references',
            
            # Job titles (not skills)
            'developer', 'engineer', 'analyst', 'manager', 'architect',
            'consultant', 'specialist', 'coordinator', 'administrator',
            'designer', 'tester', 'qa', 'devops', 'intern', 'trainee',
            
            # Report/document terms
            'report', 'bug', 'issue', 'ticket', 'document', 'documentation',
            
            # ADDITIONAL GENERIC WORDS (from screenshot)
            'content', 'critical', 'data', 'datum', 'feedback', 'future',
            'google', 'guideline', 'guidelines', 'include', 'includes', 'included',
            'key', 'keys', 'list', 'lists', 'mobile', 'peer', 'peers',
            'quality', 'search', 'searching', 'searched',
            
            # More generic terms
            'ability', 'access', 'action', 'activity', 'actual', 'add',
            'address', 'analysis', 'approach', 'area', 'article', 'aspect',
            'base', 'based', 'basic', 'basis', 'best', 'better',
            'case', 'center', 'change', 'check', 'clear', 'close',
            'common', 'complete', 'concept', 'condition', 'contact',
            'current', 'detail', 'details', 'different', 'direct',
            'effective', 'end', 'ensure', 'example', 'fact', 'feature',
            'field', 'file', 'final', 'find', 'focus', 'follow',
            'form', 'format', 'function', 'general', 'give', 'goal',
            'group', 'guide', 'high', 'idea', 'identify', 'impact',
            'important', 'improve', 'information', 'input', 'item',
            'large', 'latest', 'line', 'link', 'local', 'long',
            'main', 'major', 'method', 'model', 'multiple', 'name',
            'need', 'needs', 'new', 'note', 'object', 'option',
            'order', 'output', 'overall', 'page', 'part', 'particular',
            'plan', 'point', 'possible', 'practice', 'present', 'primary',
            'problem', 'project', 'proper', 'provide', 'purpose',
            'question', 'quick', 'range', 'rate', 'reason', 'record',
            'related', 'relevant', 'request', 'resource', 'result',
            'review', 'right', 'section', 'select', 'set', 'show',
            'simple', 'single', 'site', 'size', 'small', 'source',
            'specific', 'standard', 'start', 'state', 'step', 'structure',
            'style', 'subject', 'summary', 'task', 'term', 'test',
            'text', 'thing', 'tool', 'topic', 'track', 'type',
            'update', 'use', 'used', 'using', 'value', 'version',
            'view', 'way', 'web', 'well', 'wide', 'word',
            
            # Vague quantifiers
            'many', 'much', 'more', 'most', 'less', 'least', 'few', 'several',
            'some', 'any', 'all', 'each', 'every', 'various', 'different',
            
            # Generic tech words (not specific skills)
            'technology', 'technologies', 'technical', 'software', 'hardware',
            'digital', 'online', 'internet', 'website', 'webpage',
            'database', 'server', 'network', 'security', 'performance',
            'interface', 'framework', 'library', 'module', 'component',
            'management', 'skills', 'testing', 'collaboration', 'compliance',
            'creation', 'metric', 'metrics', 'roadmap', 'cloud',
            
            # Action words that are too generic
            'achieve', 'act', 'add', 'allow', 'apply', 'assess',
            'begin', 'bring', 'call', 'carry', 'cause', 'change',
            'come', 'consider', 'continue', 'control', 'cover',
            'define', 'describe', 'determine', 'develop', 'differ',
            'enable', 'establish', 'exist', 'expect', 'explain',
            'feel', 'follow', 'gain', 'generate', 'get', 'give',
            'handle', 'happen', 'hold', 'identify', 'improve',
            'increase', 'indicate', 'involve', 'keep', 'know',
            'learn', 'leave', 'let', 'like', 'look', 'lose',
            'mean', 'meet', 'mention', 'move', 'obtain', 'occur',
            'offer', 'open', 'operate', 'order', 'perform', 'place',
            'play', 'prepare', 'present', 'produce', 'prove',
            'reach', 'read', 'receive', 'recognize', 'reduce',
            'refer', 'reflect', 'relate', 'remain', 'remove',
            'replace', 'represent', 'require', 'respond', 'result',
            'return', 'reveal', 'run', 'say', 'see', 'seek',
            'seem', 'send', 'serve', 'set', 'share', 'show',
            'speak', 'spend', 'stand', 'start', 'state', 'stay',
            'suggest', 'take', 'talk', 'tell', 'tend', 'think',
            'try', 'turn', 'understand', 'use', 'vary', 'wait',
            'want', 'watch', 'wear', 'win', 'wish', 'wonder', 'write'
        }
        
        # Helper function to filter noise
        def is_valid_keyword(kw):
            return (
                kw not in noise_filter 
                and len(kw) > 2 
                and not kw.isdigit()
                and not re.match(r'^\d+[\.,]?\d*[klm]?$', kw)
            )
        
        # Clean ALL keyword sets
        matched_keywords = {kw for kw in matched_keywords if is_valid_keyword(kw)}
        missing_keywords = {kw for kw in missing_keywords if is_valid_keyword(kw)}
        matched_terms = {term for term in matched_terms if is_valid_keyword(term)}
        missing_terms = {term for term in missing_terms if is_valid_keyword(term)}

        # Calculate experience score
        experience_score = 100.0
        experience_gap = 0
        if jd_years > 0:
            if resume_years >= jd_years:
                experience_score = 100.0  # Meets or exceeds requirement
            elif resume_years >= jd_years * 0.8:
                experience_score = 90.0  # 80%+ of required (close enough)
            elif resume_years >= jd_years * 0.6:
                experience_score = 75.0  # 60%+ of required
            elif resume_years >= jd_years * 0.4:
                experience_score = 60.0  # 40%+ of required
            else:
                experience_score = 40.0  # Less than 40% of required
            
            experience_gap = jd_years - resume_years
        
        # Skills score - with minimum baseline
        if jd_skills:
            skill_match_ratio = len(matched_skills) / len(jd_skills)
            skill_score = skill_match_ratio * 100
            if len(matched_skills) > 0:
                skill_score = max(skill_score, 40)
        else:
            skill_score = 70
            
        # Keyword score - more forgiving
        if jd_keywords:
            keyword_match_ratio = len(matched_keywords) / len(jd_keywords)
            keyword_score = keyword_match_ratio * 100
            if keyword_match_ratio >= 0.2:
                keyword_score = max(keyword_score, 50)
        else:
            keyword_score = 70
            
        # Terms score - most forgiving
        if jd_important_words:
            term_match_ratio = len(matched_terms) / len(jd_important_words)
            term_score = term_match_ratio * 100
            if term_match_ratio >= 0.15:
                term_score = max(term_score, 45)
        else:
            term_score = 70
        
        # NEW: Weighted scoring with experience included
        # Skills (40%), Experience (20%), Keywords (25%), Terms (15%)
        final_score = (skill_score * 0.40) + (experience_score * 0.20) + (keyword_score * 0.25) + (term_score * 0.15)
        
        # Bonus system
        total_matches = len(matched_skills) + len(matched_keywords) + len(matched_terms)
        if total_matches >= 10:
            final_score = min(final_score + 10, 100)
        elif total_matches >= 5:
            final_score = min(final_score + 5, 100)
        
        if jd_skills and len(matched_skills) >= len(jd_skills) * 0.7:
            final_score = min(final_score + 8, 100)
        
        if total_matches > 0:
            final_score = max(final_score, 35)

        # Generate suggestions with experience info
        suggestions = JDMatcher._generate_suggestions(
            final_score, missing_skills, missing_keywords, 
            resume_years, jd_years, experience_gap
        )

        return {
            "match_score": round(min(final_score, 100.0), 2),
            "matched_keywords": sorted(list(matched_skills | matched_keywords | matched_terms))[:20],
            "missing_keywords": sorted(list(missing_skills | missing_keywords))[:10],
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(list(missing_skills))[:6],
            "suggestions": suggestions,
            "experience_match": {
                "resume_years": resume_years,
                "required_years": jd_years,
                "gap": experience_gap,
                "meets_requirement": resume_years >= jd_years if jd_years > 0 else True
            },
            "_debug": {
                "skill_score": round(skill_score, 2),
                "experience_score": round(experience_score, 2),
                "keyword_score": round(keyword_score, 2),
                "term_score": round(term_score, 2),
                "total_matches": total_matches,
                "matched_skills_count": len(matched_skills),
                "matched_keywords_count": len(matched_keywords),
                "matched_terms_count": len(matched_terms),
                "jd_skills_count": len(jd_skills),
                "jd_keywords_count": len(jd_keywords),
                "jd_terms_count": len(jd_important_words)
            }
        }
    
    @staticmethod
    def _extract_important_terms(text: str) -> set:
        """Extract important technical and business terms from text - Improved noise filtering"""
        doc = nlp(text)
        important_terms = set()
        
        # Comprehensive noise words list - EXPANDED
        noise_words = {
            # Time/Date
            'year', 'years', 'month', 'months', 'day', 'days', 'week', 'weeks',
            'time', 'date', 'hour', 'hours', 'shift', 'schedule', 'timing',
            # Money
            'lakh', 'lakhs', 'lpa', 'ctc', 'salary', 'package', 'compensation',
            'rupee', 'rupees', 'dollar', 'dollars', 'inr', 'usd', 'eur', 'gbp',
            'minimum', 'maximum', 'range', 'between', 'approximately', 'around',
            # Job terms
            'company', 'role', 'position', 'job', 'work', 'candidate', 'applicant',
            'requirement', 'requirements', 'qualification', 'qualifications',
            'benefit', 'benefits', 'perk', 'perks', 'location', 'office',
            'number', 'amount', 'total', 'sum', 'count', 'quantity',
            'experience', 'skill', 'ability', 'knowledge', 'understanding',
            'opportunity', 'growth', 'career', 'development', 'learning',
            'environment', 'culture', 'value', 'mission', 'vision',
            'team', 'member', 'individual', 'person', 'people', 'staff',
            'level', 'senior', 'junior', 'mid', 'entry', 'lead',
            # Education
            'bachelor', 'bachelors', 'master', 'masters', 'degree', 'diploma',
            'education', 'graduate', 'undergraduate', 'phd', 'doctorate',
            'college', 'university', 'school', 'institute', 'academy',
            # Locations
            'bangalore', 'bengaluru', 'mumbai', 'delhi', 'hyderabad', 'chennai',
            'pune', 'kolkata', 'ahmedabad', 'jaipur', 'noida', 'gurgaon', 'gurugram',
            # Adjectives
            'good', 'excellent', 'strong', 'basic', 'advanced', 'proficient',
            'working', 'hands', 'plus', 'must', 'should', 'need', 'require',
            'prefer', 'desired', 'nice', 'bonus', 'optional', 'mandatory',
            'flexible', 'remote', 'hybrid', 'onsite', 'freelance', 'freelancer',
            # Generic terms
            'product', 'service', 'customer', 'client', 'user',
            'business', 'industry', 'market', 'sector', 'domain',
            'process', 'system', 'solution', 'platform', 'application',
            'design', 'develop', 'implement', 'build', 'create', 'maintain',
            'manage', 'lead', 'coordinate', 'collaborate', 'communicate',
            'description', 'required', 'preferred', 'looking', 'seeking',
            # Job titles
            'developer', 'engineer', 'analyst', 'manager', 'architect',
            'consultant', 'specialist', 'coordinator', 'administrator',
            # ADDITIONAL GENERIC WORDS
            'content', 'critical', 'data', 'datum', 'feedback', 'future',
            'google', 'guideline', 'guidelines', 'include', 'includes', 'included',
            'key', 'keys', 'list', 'lists', 'mobile', 'peer', 'peers',
            'quality', 'search', 'searching', 'searched',
            'ability', 'access', 'action', 'activity', 'actual', 'add',
            'address', 'analysis', 'approach', 'area', 'article', 'aspect',
            'base', 'based', 'basic', 'basis', 'best', 'better',
            'case', 'center', 'change', 'check', 'clear', 'close',
            'common', 'complete', 'concept', 'condition', 'contact',
            'current', 'detail', 'details', 'different', 'direct',
            'effective', 'end', 'ensure', 'example', 'fact', 'feature',
            'field', 'file', 'final', 'find', 'focus', 'follow',
            'form', 'format', 'function', 'general', 'give', 'goal',
            'group', 'guide', 'high', 'idea', 'identify', 'impact',
            'important', 'improve', 'information', 'input', 'item',
            'large', 'latest', 'line', 'link', 'local', 'long',
            'main', 'major', 'method', 'model', 'multiple', 'name',
            'need', 'needs', 'new', 'note', 'object', 'option',
            'order', 'output', 'overall', 'page', 'part', 'particular',
            'plan', 'point', 'possible', 'practice', 'present', 'primary',
            'problem', 'project', 'proper', 'provide', 'purpose',
            'question', 'quick', 'range', 'rate', 'reason', 'record',
            'related', 'relevant', 'request', 'resource', 'result',
            'review', 'right', 'section', 'select', 'set', 'show',
            'simple', 'single', 'site', 'size', 'small', 'source',
            'specific', 'standard', 'start', 'state', 'step', 'structure',
            'style', 'subject', 'summary', 'task', 'term', 'test',
            'text', 'thing', 'tool', 'topic', 'track', 'type',
            'update', 'use', 'used', 'using', 'value', 'version',
            'view', 'way', 'web', 'well', 'wide', 'word',
            'many', 'much', 'more', 'most', 'less', 'least', 'few', 'several',
            'some', 'any', 'all', 'each', 'every', 'various', 'different',
            'technology', 'technologies', 'technical', 'software', 'hardware',
            'digital', 'online', 'internet', 'website', 'webpage',
            'database', 'server', 'network', 'security', 'performance',
            'interface', 'framework', 'library', 'module', 'component',
            'management', 'skills', 'testing', 'collaboration', 'compliance',
            'creation', 'metric', 'metrics', 'roadmap', 'cloud'
        }
        
        for token in doc:
            # Skip numbers and number-like tokens
            if token.like_num or token.text.isdigit() or token.is_currency:
                continue
            
            # Skip if it matches number patterns
            if re.match(r'^\d+[\.,]?\d*[klm]?$', token.text.lower()):
                continue
            
            # Skip noise words
            if token.lemma_.lower() in noise_words:
                continue
            
            # Get nouns, proper nouns, adjectives, and verbs that are meaningful
            if (
                token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]
                and not token.is_stop
                and not token.is_punct
                and len(token.text) > 2  # At least 3 characters
                and not token.lemma_.lower() in noise_words
            ):
                # Additional filter: skip if it looks like a number with units
                if not re.match(r'^\d+[a-z]*$', token.text.lower()):
                    important_terms.add(token.lemma_.lower())
        
        # Extract all capitalized acronyms (API, AWS, SQL, CI/CD, etc.)
        # But skip common salary/number patterns
        acronym_pattern = r'\b[A-Z]{2,}(?:/[A-Z]+)?\b'
        acronyms = re.findall(acronym_pattern, text)
        for acronym in acronyms:
            # Skip if it's likely a currency or number-related
            if acronym.lower() not in ['lpa', 'ctc', 'inr', 'usd', 'eur', 'gbp', 'qa']:
                important_terms.add(acronym.lower())
        
        # Extract common tech patterns
        tech_patterns = [
            r'\b\w+\.js\b',  # React.js, Node.js, etc.
            r'\b\w+SQL\b',   # MySQL, PostgreSQL, etc.
            r'\b\w+DB\b',    # MongoDB, DynamoDB, etc.
        ]
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                important_terms.add(match.lower())
        
        return important_terms

    # ─── Suggestions ──────────────────────────────────────────

    @staticmethod
    def _generate_suggestions(score: float, missing_skills: set, missing_keywords: set, 
                             resume_years: float = 0, jd_years: float = 0, experience_gap: float = 0) -> list[str]:
        suggestions = []

        # Experience-based feedback FIRST (most important)
        if jd_years > 0:
            if resume_years >= jd_years:
                suggestions.append(f"✅ Experience requirement met: You have {resume_years} years, required {jd_years} years")
            elif experience_gap > 0:
                if experience_gap >= 3:
                    suggestions.append(f"⚠️ Experience gap: You have {resume_years} years, but {jd_years}+ years required (gap: {experience_gap} years)")
                    suggestions.append(f"💡 Consider roles requiring {resume_years}-{resume_years+2} years of experience for better fit")
                elif experience_gap >= 1:
                    suggestions.append(f"📊 Close to requirement: You have {resume_years} years, {jd_years} years preferred")
                    suggestions.append(f"💪 Highlight relevant projects and achievements to compensate for experience gap")

        # Score-based overall feedback
        if score >= 85:
            suggestions.append("🎯 Excellent match! Your resume aligns very well with this job description.")
            suggestions.append("✅ You have most of the required skills - apply with confidence!")
        elif score >= 70:
            suggestions.append("✨ Good match! Your resume shows strong alignment with the job requirements.")
            suggestions.append("💡 Add a few more relevant keywords to strengthen your application.")
        elif score >= 50:
            suggestions.append("⚠️ Moderate match. Your resume needs improvement to better align with this JD.")
            suggestions.append("📝 Focus on highlighting the missing skills and keywords mentioned below.")
        elif score >= 30:
            suggestions.append("❌ Low match. Significant gaps between your resume and job requirements.")
            suggestions.append("🔧 Consider gaining experience in the missing skills before applying.")
        else:
            suggestions.append("⛔ Very low match. This role may not be suitable for your current profile.")
            suggestions.append("💼 Look for roles that better match your existing skillset.")

        # Specific missing skills suggestions
        if missing_skills:
            top_missing = sorted(list(missing_skills))[:5]
            if len(top_missing) == 1:
                suggestions.append(f"🎓 Key skill missing: {top_missing[0].upper()}")
            elif len(top_missing) <= 3:
                suggestions.append(f"🎓 Key skills missing: {', '.join([s.upper() for s in top_missing])}")
            else:
                suggestions.append(f"🎓 Top missing skills: {', '.join([s.upper() for s in top_missing[:3]])} and {len(top_missing)-3} more")
            
            # Actionable advice based on missing skills
            if any(skill in ['python', 'java', 'javascript', 'c++', 'go', 'rust'] for skill in missing_skills):
                suggestions.append("💻 Add programming language proficiency with specific projects or certifications")
            if any(skill in ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'] for skill in missing_skills):
                suggestions.append("☁️ Highlight cloud platform experience or consider getting certified")
            if any(skill in ['react', 'angular', 'vue', 'nodejs', 'django', 'flask'] for skill in missing_skills):
                suggestions.append("🌐 Showcase framework experience with live project links or GitHub repos")
            if any(skill in ['sql', 'mongodb', 'postgresql', 'mysql', 'redis'] for skill in missing_skills):
                suggestions.append("🗄️ Emphasize database management experience with specific use cases")

        # Missing keywords suggestions
        if missing_keywords:
            top_keywords = sorted(list(missing_keywords))[:4]
            if len(top_keywords) <= 2:
                suggestions.append(f"🔑 Important keywords to add: {', '.join(top_keywords)}")
            else:
                suggestions.append(f"🔑 Add these keywords: {', '.join(top_keywords[:3])}")

        # General improvement tips based on score
        if score < 70:
            suggestions.append("📊 Use quantifiable achievements (e.g., 'Improved performance by 40%', 'Reduced costs by $50K')")
            suggestions.append("🎯 Mirror the job title and key phrases from the JD in your resume")
            suggestions.append("📄 Tailor your resume summary to match the role's requirements")
        
        if score >= 70:
            suggestions.append("✏️ Fine-tune your resume by adding specific examples of the mentioned skills")
            suggestions.append("🚀 Highlight relevant projects that demonstrate your expertise")

        # Always include action items
        if missing_skills or missing_keywords:
            suggestions.append("⚡ Action: Update your resume with the missing skills/keywords if you have relevant experience")
        
        return suggestions

    # ─── Similarity Score (spaCy vectors) ────────────────────

    @staticmethod
    def semantic_similarity(text1: str, text2: str) -> float:
        """
        spaCy word vectors se semantic similarity
        (en_core_web_sm mein basic similarity hoti hai)
        """
        # Sirf pehle 1000 chars lo — performance ke liye
        doc1 = nlp(text1[:1000])
        doc2 = nlp(text2[:1000])

        if doc1.vector_norm and doc2.vector_norm:
            return round(doc1.similarity(doc2) * 100, 2)
        return 0.0