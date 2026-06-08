print("=== AI Job Application Pipeline ===\n")

print("Step 1/4: Scraping jobs...")
import scraper

print("\nStep 2/4: Scoring jobs...")
import score_jobs

print("\nStep 3/4: Tailoring resumes...")
import resume_tailor
resume_tailor.main()

print("\nStep 4/4: Generating cover letters...")
import cover_letter
cover_letter.main()

print("\nStep 5/5: Sending emails...")
import email_sender
email_sender.main()

print("\n✅ Pipeline complete!")