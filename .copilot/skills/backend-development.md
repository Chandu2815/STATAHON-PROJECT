# Skill: Backend Development Standards
# Survey-AI Dataset Explorer System

## Scope
This skill applies to Node.js (Express.js) backend development in the Survey-AI project.

## Core Concepts

### Architecture Pattern: MVC (Model-View-Controller)
- **Routes**: Define API endpoints using Express Router
- **Controllers**: Handle request/response, validation
- **Services**: Contain business logic, database operations
- **Models**: Define data structures, database interactions

### Key Rules
1. **Router Usage**
   - Always use `express.Router()` for modular routing
   - Group related routes in separate files
   - Mount routers with clear prefixes
   
   ```javascript
   const authRouter = require('./routes/auth');
   app.use('/api/auth', authRouter);
   ```

2. **Async/Await Mandatory**
   - All asynchronous operations must use async/await
   - Never mix callbacks with async/await
   - Always wrap async routes with try/catch

   ```javascript
   router.post('/login', async (req, res, next) => {
     try {
       const user = await authService.validateUser(req.body);
       res.json({ success: true, data: user });
     } catch (err) {
       next(err);
     }
   });
   ```

3. **Database Query Safety**
   - Use parameterized queries ONLY
   - Never concatenate user input into query strings
   
   ```javascript
   // ✅ CORRECT
   pool.query('SELECT * FROM users WHERE email = $1', [email]);
   
   // ❌ WRONG
   pool.query(`SELECT * FROM users WHERE email = '${email}'`);
   ```

4. **Response Format Consistency**
   - All successful responses: `{ success: true, data: {...} }`
   - All error responses: `{ success: false, error: '...', code: '...' }`
   - Include metadata where relevant

   ```javascript
   res.json({
     success: true,
     data: { id: user.id, email: user.email },
     meta: { timestamp: new Date().toISOString() }
   });
   ```

5. **Error Handling**
   - Implement centralized error handler middleware
   - Pass all errors to next() middleware
   - Never send unhandled errors to client
   - Log errors for debugging

   ```javascript
   // In controller
   try {
     const user = await userService.getUser(id);
   } catch (err) {
     next(err); // Pass to error handler middleware
   }
   
   // Error handler middleware
   app.use((err, req, res, next) => {
     console.error(err);
     res.status(err.status || 500).json({
       success: false,
       error: err.message,
       code: err.code
     });
   });
   ```

6. **Service Layer Pattern**
   - All business logic in services
   - Controllers call services
   - Services handle database access
   - Keep controllers thin

   ```javascript
   // Service
   async function createUser(userData) {
     const hashedPwd = await bcrypt.hash(userData.password, 10);
     return pool.query(
       'INSERT INTO users (email, password) VALUES ($1, $2) RETURNING *',
       [userData.email, hashedPwd]
     );
   }
   
   // Controller
   const newUser = await userService.createUser(req.body);
   res.status(201).json({ success: true, data: newUser });
   ```

## Code Generation Checklist

- [ ] Use Express Router - no app.get/post directly
- [ ] Implement all operations as async functions
- [ ] Use try/catch for error handling
- [ ] Parameterize all database queries
- [ ] Validate request input before processing
- [ ] Return consistent JSON response format
- [ ] Implement proper HTTP status codes
- [ ] Add appropriate middleware (auth, validation)
- [ ] Document endpoint with JSDoc comment
- [ ] Handle edge cases and errors

## Common Patterns

### Authentication Endpoint
```javascript
// routes/auth.js
router.post('/login', authController.login);

// controllers/authController.js
async function login(req, res, next) {
  try {
    const { email, password } = req.body;
    
    // Validate input
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        error: 'Email and password required',
        code: 'VALIDATION_ERROR'
      });
    }
    
    // Call service
    const { user, token } = await authService.login(email, password);
    
    // Return response
    res.json({
      success: true,
      data: { user, token },
      meta: { expiresIn: 3600 }
    });
  } catch (err) {
    next(err);
  }
}

// services/authService.js
async function login(email, password) {
  // Query user by email (parameterized)
  const result = await pool.query(
    'SELECT * FROM users WHERE email = $1',
    [email]
  );
  
  if (result.rows.length === 0) {
    throw new Error('User not found');
  }
  
  const user = result.rows[0];
  
  // Compare passwords
  const isValid = await bcrypt.compare(password, user.password);
  if (!isValid) {
    throw new Error('Invalid password');
  }
  
  // Generate token
  const token = jwt.sign({ id: user.id }, process.env.SECRET_KEY);
  
  return { user: { id: user.id, email: user.email }, token };
}
```

### Protected Route Middleware
```javascript
const verifyToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader) {
      return res.status(401).json({
        success: false,
        error: 'No authorization header',
        code: 'UNAUTHORIZED'
      });
    }
    
    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.SECRET_KEY);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({
      success: false,
      error: 'Invalid token',
      code: 'UNAUTHORIZED'
    });
  }
};

router.get('/profile', verifyToken, async (req, res, next) => {
  try {
    const user = await userService.getUserById(req.user.id);
    res.json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
});
```

## When to Activate This Skill
- Writing new Express routes
- Implementing controllers for new features
- Creating service layer logic
- Fixing backend bugs
- Adding authentication endpoints
- Refactoring existing backend code

## Related Skills
- database-expert (for database queries in services)
- api-designer (for REST endpoint design)
- debugging-assistant (for troubleshooting)
