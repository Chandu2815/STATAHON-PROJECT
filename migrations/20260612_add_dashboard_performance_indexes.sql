CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_plfs_person_st
ON plfs.person (st);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_survey_ai_activity_user_action_created
ON public.survey_ai_activity (user_id, action, created_at DESC);
