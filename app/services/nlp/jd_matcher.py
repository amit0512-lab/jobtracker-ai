import re
import spacy
from app.services.nlp.resume_parser import ResumeParser, ALL_SKILLS, nlp


class JDMatcher:

    # ─── Match Score Calculate ────────────────────────────────

    @staticmethod
    def calculate_match_score(resume_text: str, jd_text: str) -> dict:
        """
        Resume vs JD match karo - Improved algorithm
        Returns: score, matched keywords, missing keywords, suggestions
        """
        # Normalize text
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        # Dono se skills nikalo
        resume_skills = set([s.lower() for s in ResumeParser.extract_skills(resume_text)])
        jd_skills = set([s.lower() for s in ResumeParser.extract_skills(jd_text)])

        # Keywords nikalo - MORE keywords for better matching
        resume_keywords = set(ResumeParser.extract_keywords(resume_text, top_n=100))
        jd_keywords = set(ResumeParser.extract_keywords(jd_text, top_n=100))

        # Extract ALL important words from JD (not just from predefined list)
        jd_important_words = JDMatcher._extract_important_terms(jd_lower)
        resume_important_words = JDMatcher._extract_important_terms(resume_lower)

        # Match calculate karo
        matched_skills = resume_skills.intersection(jd_skills)
        missing_skills = jd_skills.difference(resume_skills)

        matched_keywords = resume_keywords.intersection(jd_keywords)
        missing_keywords = jd_keywords.difference(resume_keywords)
        
        # Match important terms
        matched_terms = resume_important_words.intersection(jd_important_words)
        missing_terms = jd_important_words.difference(resume_important_words)

        # Improved Score formula with better weights:
        # 30% weight — skills match
        # 35% weight — keyword match  
        # 35% weight — important terms match
        
        # Calculate individual scores with minimum baseline
        if jd_skills:
            skill_score = (len(matched_skills) / len(jd_skills) * 100)
        else:
            skill_score = 60  # No skills in JD, give benefit of doubt
            
        if jd_keywords:
            keyword_score = (len(matched_keywords) / len(jd_keywords) * 100)
        else:
            keyword_score = 60
            
        if jd_important_words:
            term_score = (len(matched_terms) / len(jd_important_words) * 100)
        else:
            term_score = 60
        
        # Calculate weighted final score
        final_score = round((skill_score * 0.30) + (keyword_score * 0.35) + (term_score * 0.35), 2)
        
        # Add bonus for high overlap in any category
        if skill_score > 80 or keyword_score > 80 or term_score > 80:
            final_score = min(final_score + 5, 100)  # 5% bonus

        # Suggestions generate karo
        suggestions = JDMatcher._generate_suggestions(
            final_score, missing_skills, missing_keywords
        )

        return {
            "match_score": min(final_score, 100.0),  # 100 se zyada nahi
            "matched_keywords": sorted(list(matched_skills | matched_keywords | matched_terms))[:25],
            "missing_keywords": sorted(list(missing_skills | missing_keywords | missing_terms))[:12],
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(list(missing_skills))[:8],
            "suggestions": suggestions,
            # Debug info (optional - can remove in production)
            "_debug": {
                "skill_score": round(skill_score, 2),
                "keyword_score": round(keyword_score, 2),
                "term_score": round(term_score, 2),
                "matched_skills_count": len(matched_skills),
                "matched_keywords_count": len(matched_keywords),
                "matched_terms_count": len(matched_terms),
                "total_jd_skills": len(jd_skills),
                "total_jd_keywords": len(jd_keywords),
                "total_jd_terms": len(jd_important_words)
            }
        }
    
    @staticmethod
    def _extract_important_terms(text: str) -> set:
        """Extract important technical and business terms from text"""
        doc = nlp(text)
        important_terms = set()
        
        for token in doc:
            # Get nouns, proper nouns, adjectives, and verbs that are meaningful
            if (
                token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]
                and not token.is_stop
                and not token.is_punct
                and len(token.text) > 2  # At least 3 characters (to include API, AWS, SQL)
            ):
                important_terms.add(token.lemma_.lower())
        
        # Extract all capitalized acronyms (API, AWS, SQL, CI/CD, etc.)
        acronym_pattern = r'\b[A-Z]{2,}(?:/[A-Z]+)?\b'
        acronyms = re.findall(acronym_pattern, text)
        for acronym in acronyms:
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
    def _generate_suggestions(score: float, missing_skills: set, missing_keywords: set) -> list[str]:
        suggestions = []

        if score < 30:
            suggestions.append("Resume JD se bahut alag hai — core skills add karo")
        elif score < 50:
            suggestions.append("Resume improve karne ki zaroorat hai — neeche diye skills add karo")
        elif score < 70:
            suggestions.append("Achha match hai! Kuch aur skills add karo score badhane ke liye")
        else:
            suggestions.append("Bahut achha match hai! Yeh job apply karne ke liye suitable hai")

        # Missing skills ke liye specific suggestions
        if missing_skills:
            top_missing = list(missing_skills)[:3]
            suggestions.append(
                f"Yeh skills JD mein hain lekin resume mein nahi: {', '.join(top_missing)}"
            )

        if missing_keywords:
            top_kw = list(missing_keywords)[:3]
            suggestions.append(
                f"Yeh keywords JD mein important hain: {', '.join(top_kw)}"
            )

        suggestions.append("Resume mein quantifiable achievements add karo (e.g., '40% performance improve kiya')")
        suggestions.append("Job title JD ke title se match karo agar relevant ho")

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