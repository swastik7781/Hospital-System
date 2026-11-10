import asyncio
import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.auth.password import get_password_hash


async def sync_patient_users():
    print("[SYNC] Synchronizing Patient Portal User Accounts...")
    async with async_session_maker() as db:
        patients = (await db.execute(select(Patient).where(Patient.is_deleted.is_(False)).order_by(Patient.id.asc()))).scalars().all()
        print(f"[SYNC] Found {len(patients)} total verified patient records in database.")

        created_count = 0
        linked_count = 0
        already_synced = 0

        for pat in patients:
            if pat.user_id:
                # Verify that user exists
                u = await db.get(User, pat.user_id)
                if u:
                    already_synced += 1
                    continue

            # Target login email
            login_email = pat.email or f"patient_{pat.id}@utkalhospital.com"
            pat.email = login_email

            # Check if user with this email exists
            existing_user = (await db.execute(select(User).where(User.email == login_email))).scalar_one_or_none()
            if existing_user:
                pat.user_id = existing_user.id
                linked_count += 1
                print(f"  [LINKED] Patient #{pat.id} '{pat.full_name}' -> User #{existing_user.id} ({login_email})")
            else:
                new_user = User(
                    email=login_email,
                    hashed_password=get_password_hash("patient123"),
                    full_name=pat.full_name,
                    role=UserRole.PATIENT,
                    is_active=True,
                    phone=pat.phone,
                )
                db.add(new_user)
                await db.flush()
                pat.user_id = new_user.id
                created_count += 1
                print(f"  [CREATED] Patient #{pat.id} '{pat.full_name}' -> New User #{new_user.id} ({login_email} / pwd: patient123)")

            db.add(pat)

        await db.commit()
        print(f"\n[DONE] Synchronization Complete!")
        print(f"       - Newly Created User Accounts: {created_count}")
        print(f"       - Linked to Existing Accounts: {linked_count}")
        print(f"       - Already Synced:              {already_synced}")
        print(f"       - All {len(patients)} patients now have active login accounts with default password 'patient123'!\n")

if __name__ == "__main__":
    asyncio.run(sync_patient_users())

