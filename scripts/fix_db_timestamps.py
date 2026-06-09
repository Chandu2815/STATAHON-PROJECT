from datetime import timezone
import sys, os
# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app.models.user import OtpChallenge, User, Transaction, UsageLog

session = SessionLocal()
updated = 0
try:
    # Fix OtpChallenge.expires_at and created_at
    for ch in session.query(OtpChallenge).all():
        changed = False
        if ch.expires_at is not None and (ch.expires_at.tzinfo is None or ch.expires_at.tzinfo.utcoffset(ch.expires_at) is None):
            ch.expires_at = ch.expires_at.replace(tzinfo=timezone.utc)
            changed = True
        if ch.created_at is not None and (ch.created_at.tzinfo is None or ch.created_at.tzinfo.utcoffset(ch.created_at) is None):
            ch.created_at = ch.created_at.replace(tzinfo=timezone.utc)
            changed = True
        if changed:
            session.add(ch)
            updated += 1

    # Fix User timestamps
    for u in session.query(User).all():
        changed = False
        if u.created_at is not None and (u.created_at.tzinfo is None or u.created_at.tzinfo.utcoffset(u.created_at) is None):
            u.created_at = u.created_at.replace(tzinfo=timezone.utc)
            changed = True
        if u.updated_at is not None and (u.updated_at.tzinfo is None or u.updated_at.tzinfo.utcoffset(u.updated_at) is None):
            u.updated_at = u.updated_at.replace(tzinfo=timezone.utc)
            changed = True
        if changed:
            session.add(u)
            updated += 1

    # Transactions
    for t in session.query(Transaction).all():
        if t.created_at is not None and (t.created_at.tzinfo is None or t.created_at.tzinfo.utcoffset(t.created_at) is None):
            t.created_at = t.created_at.replace(tzinfo=timezone.utc)
            session.add(t)
            updated += 1

    # UsageLog
    for l in session.query(UsageLog).all():
        if l.timestamp is not None and (l.timestamp.tzinfo is None or l.timestamp.tzinfo.utcoffset(l.timestamp) is None):
            l.timestamp = l.timestamp.replace(tzinfo=timezone.utc)
            session.add(l)
            updated += 1

    session.commit()
    print(f"Timestamps normalized to UTC for {updated} rows")
except Exception as e:
    session.rollback()
    print("Error while fixing timestamps:", e)
finally:
    session.close()
