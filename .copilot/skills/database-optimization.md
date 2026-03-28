# Skill: Database & SQL Optimization
# Survey-AI Dataset Explorer System

## Scope
This skill applies to all PostgreSQL database operations in the Survey-AI project.

## Core Concepts

### Database Architecture
- **Database**: PostgreSQL `survey_db`
- **Host**: localhost:5432
- **Connection Pooling**: 10 pool size, 20 max overflow
- **Primary Tables**: users, datasets, survey_data
- **Dataset Records**: 261K+ household records

### Critical Rules

1. **Connection Pooling Configuration**
   - Pool size: 10 connections (maintained)
   - Max overflow: 20 additional connections (on demand)
   - Pool pre-ping: True (test connections before use)
   - Timeout: 10 seconds per connection
   - NEVER create connections directly - use pool

   ```javascript
   // Node.js - pg library with pool
   const pool = new Pool({
     connectionString: 'postgresql://postgres:1234@127.0.0.1:5432/survey_db',
     max: 10,
     idleTimeoutMillis: 30000,
     connectionTimeoutMillis: 2000,
   });
   
   // Use pool, never connect directly
   const result = await pool.query('SELECT * FROM users');
   ```

   ```python
   # Python - SQLAlchemy with pooling
   engine = create_engine(
       'postgresql://postgres:1234@127.0.0.1:5432/survey_db',
       poolclass=QueuePool,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
       connect_args={'connect_timeout': 10}
   )
   ```

2. **Query Parameterization - ABSOLUTE REQUIREMENT**
   - Use parameters for ALL user input
   - Use query placeholders ($1, $2 for PostgreSQL)
   - NEVER string interpolation or concatenation

   ```javascript
   // ✅ CORRECT - Parameterized query
   pool.query('SELECT * FROM users WHERE email = $1 AND active = $2', [email, true]);
   
   // ❌ WRONG - String concatenation (SQL INJECTION!)
   pool.query(`SELECT * FROM users WHERE email = '${email}'`);
   
   // ❌ WRONG - String interpolation (SQL INJECTION!)
   pool.query(`SELECT * FROM users WHERE email = '${email}'`);
   ```

   ```python
   # ✅ CORRECT - SQLAlchemy ORM
   user = db.query(User).filter(User.email == email).first()
   
   # ✅ CORRECT - Parameterized raw SQL
   result = db.execute(
       text("SELECT * FROM users WHERE email = :email"),
       {"email": email}
   )
   
   # ❌ WRONG - String concatenation (SQL INJECTION!)
   result = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
   ```

3. **Index Strategy**
   - Create indexes on frequently queried columns
   - Index foreign keys for joins
   - Index columns used in WHERE clauses
   - Monitor query performance

   ```sql
   -- Recommended indexes for survey_db
   CREATE INDEX idx_users_email ON users(email);           -- For login queries
   CREATE INDEX idx_users_role ON users(role);             -- For role filtering
   CREATE INDEX idx_datasets_name ON datasets(name);       -- For dataset lookup
   CREATE INDEX idx_datasets_category ON datasets(category); -- For hierarchical queries
   CREATE INDEX idx_survey_data_dataset_id ON survey_data(dataset_id); -- For joins
   CREATE INDEX idx_survey_data_created ON survey_data(created_at); -- For time filtering
   ```

4. **Query Optimization**
   - Fetch only needed columns (no `SELECT *`)
   - Use LIMIT for result sets
   - Use OFFSET/LIMIT for pagination
   - Avoid N+1 queries
   - Use JOINs efficiently

   ```sql
   -- ❌ AVOID - Fetches all columns, all rows
   SELECT * FROM survey_data;
   
   -- ✅ PREFER - Specific columns, limited set
   SELECT id, household_id, state, quantity 
   FROM survey_data 
   WHERE dataset_id = $1 
   LIMIT 100 
   OFFSET 0;
   
   -- ✅ PREFER - JOIN instead of multiple queries
   SELECT u.id, u.email, COUNT(d.id) as dataset_count
   FROM users u
   LEFT JOIN datasets d ON u.id = d.user_id
   GROUP BY u.id
   LIMIT 50;
   ```

5. **Reusable Query Helpers**
   - Create helper functions for common queries
   - Centralize query logic
   - Make queries testable

   ```javascript
   // database/queries.js
   async function getUserByEmail(pool, email) {
     const result = await pool.query(
       'SELECT id, email, role FROM users WHERE email = $1',
       [email]
     );
     return result.rows[0] || null;
   }
   
   async function getDatasetsByCategory(pool, category) {
     const result = await pool.query(
       'SELECT id, name, record_count FROM datasets WHERE category = $1 ORDER BY name',
       [category]
     );
     return result.rows;
   }
   
   // Usage
   const user = await getUserByEmail(pool, email);
   ```

   ```python
   # database/queries.py
   async def get_user_by_email(db: Session, email: str):
       return db.query(User).filter(User.email == email).first()
   
   async def get_datasets_by_category(db: Session, category: str):
       return db.query(Dataset).filter(Dataset.category == category).order_by(Dataset.name).all()
   
   async def get_hierarchical_datasets(db: Session):
       """Fetch all datasets organized by category"""
       datasets = db.query(Dataset).all()
       hierarchical = {"HCES": [], "PLFS": [], "Survey": [], "Other": []}
       for ds in datasets:
           hierarchical[ds.category].append(ds)
       return hierarchical
   ```

6. **Transaction Management**
   - Use transactions for multi-step operations
   - Commit on success, rollback on failure
   - Keep transactions small and fast

   ```javascript
   // Node.js - Transaction example
   const client = await pool.connect();
   try {
     await client.query('BEGIN');
     
     const userResult = await client.query(
       'INSERT INTO users (email, password) VALUES ($1, $2) RETURNING *',
       [email, hashedPassword]
     );
     
     await client.query(
       'INSERT INTO user_roles (user_id, role) VALUES ($1, $2)',
       [userResult.rows[0].id, 'researcher']
     );
     
     await client.query('COMMIT');
   } catch (err) {
     await client.query('ROLLBACK');
     throw err;
   } finally {
     client.release();
   }
   ```

   ```python
   # Python - Transaction example
   try:
       user = User(email=email, password=hashed_pwd)
       db.add(user)
       db.flush()  # Get the user ID
       
       role = UserRole(user_id=user.id, role='researcher')
       db.add(role)
       
       db.commit()
   except Exception as e:
       db.rollback()
       raise e
   ```

7. **Error Handling**
   - Catch database-specific errors
   - Log errors with context
   - Return meaningful error messages

   ```javascript
   try {
     const result = await pool.query(query, params);
     return result.rows;
   } catch (err) {
     if (err.code === '23505') {
       // Unique constraint violation
       throw new Error('Email already exists');
     } else if (err.code === '23503') {
       // Foreign key violation
       throw new Error('Referenced record not found');
     } else {
       console.error('Database error:', err);
       throw new Error('Database operation failed');
     }
   }
   ```

8. **Data Validation**
   - Validate data types before inserting
   - Check constraints on application side
   - Sanitize string inputs

   ```python
   # Validate before query
   if not isinstance(email, str) or '@' not in email:
       raise ValueError("Invalid email format")
   
   if len(password) < 8:
       raise ValueError("Password must be at least 8 characters")
   
   # Sanitize strings
   email = email.strip().lower()
   ```

## Common Query Patterns

### Get Hierarchical Datasets
```sql
SELECT 
  tablename as name,
  CASE 
    WHEN tablename LIKE 'hces_%' THEN 'HCES'
    WHEN tablename LIKE 'plfs_%' THEN 'PLFS'
    WHEN tablename LIKE 'survey_%' THEN 'Survey'
    ELSE 'Other'
  END as category
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY category, tablename;
```

### Get Column Information
```sql
SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name = $1
ORDER BY ordinal_position;
```

### Get Record Count
```sql
SELECT COUNT(*) as record_count 
FROM survey_data 
WHERE dataset_id = $1;
```

### Paginated Data Retrieval
```sql
SELECT id, household_id, state, quantity
FROM survey_data
WHERE dataset_id = $1
ORDER BY id
LIMIT $2 OFFSET $3;
```

### Aggregated Statistics
```sql
SELECT 
  state,
  COUNT(*) as record_count,
  AVG(quantity) as avg_quantity,
  MAX(quantity) as max_quantity,
  MIN(quantity) as min_quantity
FROM survey_data
WHERE dataset_id = $1
GROUP BY state
ORDER BY record_count DESC;
```

## Database Maintenance

### Performance Monitoring
```sql
-- Check slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Cleanup Tasks
```sql
-- Analyze query planner statistics
ANALYZE;

-- Vacuum database (remove dead rows)
VACUUM ANALYZE;

-- Rebuild indexes
REINDEX TABLE users;
REINDEX TABLE datasets;
```

## Code Generation Checklist

- [ ] Use connection pool, not direct connections
- [ ] Parameterize ALL queries
- [ ] Fetch only needed columns
- [ ] Add indexes on query columns
- [ ] Use LIMIT for result sets
- [ ] Implement pagination for large sets
- [ ] Use transactions for multi-step operations
- [ ] Handle database-specific errors
- [ ] Log errors with context
- [ ] Test with realistic data volumes
- [ ] Monitor query performance

## When to Activate This Skill
- Writing database queries
- Optimizing slow queries
- Adding new database features
- Creating migration scripts
- Troubleshooting performance issues
- Implementing caching strategies

## Related Skills
- backend-development (for Node.js queries)
- fastapi-development (for Python queries)
- api-designer (for response optimization)

## Connection Details
- URL: `postgresql://postgres:1234@127.0.0.1:5432/survey_db`
- Pool Size: 10 connections
- Max Overflow: 20 connections
- Timeout: 10 seconds
