#!/usr/bin/env python3
"""Test to verify comprehensive noise word filtering"""

from app.services.nlp.jd_matcher import JDMatcher

# Test with a resume that has BOTH technical skills AND noise words
resume_text = """
QA Report for XYZ Company
Location: Bangalore, India
Education: Bachelor's Degree
Experience: 2 years

Technical Skills:
- Python (3 years)
- Django REST Framework
- FastAPI
- Docker containerization
- AWS (EC2, S3, Lambda)
- PostgreSQL database
- Git version control
- RESTful API design

Content management, critical thinking, data analysis, feedback loops,
future planning, Google search, guideline adherence, include all features,
key performance indicators, list management, mobile responsive, peer review,
quality assurance, search optimization.

Projects:
- Built a web application using Django
- Deployed microservices on AWS
- Implemented CI/CD pipeline with Docker
"""

# Job description with similar noise
jd_text = """
We are looking for a Python Developer with 3+ years of experience.

Required Technical Skills:
- Python
- Django
- FastAPI
- Docker
- AWS
- Kubernetes
- PostgreSQL
- Redis

Content creation, critical analysis, data management, feedback systems,
future roadmap, Google Cloud, guideline compliance, include testing,
key metrics, list processing, mobile development, peer collaboration,
quality standards, search functionality.

Location: Bangalore
Salary: 10-15 LPA
Education: Bachelor's Degree required
"""

print("=" * 60)
print("KEYWORD FILTER TEST - Noise Word Removal")
print("=" * 60)

result = JDMatcher.calculate_match_score(resume_text, jd_text)

print(f"\n✅ Match Score: {result['match_score']}%")

print(f"\n✅ Matched Keywords ({len(result['matched_keywords'])}):")
if result['matched_keywords']:
    for kw in result['matched_keywords'][:15]:  # Show first 15
        print(f"  - {kw}")
else:
    print("  (none)")

print(f"\n⚠️  Missing Keywords ({len(result['missing_keywords'])}):")
if result['missing_keywords']:
    for kw in result['missing_keywords'][:10]:  # Show first 10
        print(f"  - {kw}")
else:
    print("  (none)")

print(f"\n📊 Matched Skills ({len(result['matched_skills'])}):")
if result['matched_skills']:
    for skill in result['matched_skills']:
        print(f"  - {skill}")
else:
    print("  (none)")

print(f"\n❌ Missing Skills ({len(result['missing_skills'])}):")
if result['missing_skills']:
    for skill in result['missing_skills']:
        print(f"  - {skill}")
else:
    print("  (none)")

# Verify noise words are filtered
noise_words_in_matched = [
    kw for kw in result['matched_keywords'] 
    if kw in ['content', 'critical', 'data', 'feedback', 'future', 
              'google', 'guideline', 'include', 'key', 'list', 
              'mobile', 'peer', 'quality', 'search', 'bangalore', 
              'bachelor', 'degree', 'education', 'location', 'salary']
]

print(f"\n{'='*60}")
print(f"🎯 NOISE FILTER VERIFICATION")
print(f"{'='*60}")
print(f"Noise words found in matched keywords: {len(noise_words_in_matched)}")
if noise_words_in_matched:
    print("❌ FAILED - These noise words should be filtered:")
    for word in noise_words_in_matched:
        print(f"  - {word}")
else:
    print("✅ PASSED - All noise words successfully filtered!")

print(f"\n{'='*60}")
