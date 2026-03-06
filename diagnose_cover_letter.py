"""
Diagnose cover letter generation issue by calling it directly
"""
import asyncio
from app.core.database import SessionLocal
from app.models.user import User
from app.models.job import Job
from app.api.controllers.cover_letter_controller import CoverLetterController

async def test():
    db = SessionLocal()
    try:
        # Get a user
        user = db.query(User).first()
        if not user:
            print("❌ No users found")
            return
        
        print(f"✅ Using user: {user.email}")
        
        # Get or create a job
        job = db.query(Job).filter(Job.user_id == user.id).first()
        if not job:
            print("Creating test job...")
            job = Job(
                user_id=user.id,
                title="Python Developer",
                company="Test Company",
                location="Remote",
                description="We need a Python developer with FastAPI experience.",
                status="applied"
            )
            db.add(job)
            db.commit()
            db.refresh(job)
        
        print(f"✅ Using job: {job.title} at {job.company}")
        
        # Try to generate cover letter
        print("\n🔄 Generating cover letter...")
        try:
            result = await CoverLetterController.generate_cover_letter(
                job_id=job.id,
                resume_id=None,
                tone="professional",
                user_id=user.id,
                db=db
            )
            print("\n✅ SUCCESS!")
            print(f"Cover Letter ID: {result['id']}")
            print(f"Word Count: {result['word_count']}")
            print(f"Content preview: {result['content'][:200]}...")
        except Exception as e:
            print(f"\n❌ ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test())
