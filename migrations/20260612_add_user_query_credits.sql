BEGIN;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS account_type VARCHAR(32),
    ADD COLUMN IF NOT EXISTS credits_remaining INTEGER,
    ADD COLUMN IF NOT EXISTS credits_used INTEGER;

UPDATE users
SET account_type = CASE
    WHEN lower(role::text) = 'researcher' THEN 'researcher'
    ELSE 'public'
END
WHERE account_type IS NULL OR account_type = '';

UPDATE users
SET credits_remaining = CASE
    WHEN account_type = 'researcher' THEN 100
    ELSE 10
END
WHERE credits_remaining IS NULL;

UPDATE users
SET credits_used = 0
WHERE credits_used IS NULL;

ALTER TABLE users
    ALTER COLUMN account_type SET DEFAULT 'public',
    ALTER COLUMN account_type SET NOT NULL,
    ALTER COLUMN credits_remaining SET DEFAULT 10,
    ALTER COLUMN credits_remaining SET NOT NULL,
    ALTER COLUMN credits_used SET DEFAULT 0,
    ALTER COLUMN credits_used SET NOT NULL;

COMMIT;
