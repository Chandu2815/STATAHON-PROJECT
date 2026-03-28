# GitHub Copilot Project Configuration

This directory contains GitHub Copilot configuration files for the **Survey-AI Dataset Explorer System** project.

## Overview

The Copilot configuration provides specialized guidance across:
- **Node.js Express.js backend** (Port 8000) - Authentication & API Gateway
- **Python FastAPI backend** (Port 8001) - Dataset & Analytics Service
- **PostgreSQL database** (localhost:5432) - Shared data store
- **React Vite frontend** (Port 5173) - Dashboard UI

## Files Structure

```
.copilot/
├── config.json                    # Main configuration file
└── skills/                        # Specialized skill guides
    ├── backend-development.md     # Node.js Express patterns
    ├── fastapi-development.md     # Python FastAPI patterns
    ├── database-optimization.md   # SQL optimization
    ├── api-design.md             # REST API standards
    └── testing.md                # Test patterns

.copilot-instructions.md          # Root instructions file
```

## Quick Start

1. **Open a backend file** - Copilot will automatically detect the context and suggest relevant patterns
2. **Ask for help** - Type `@copilot` to get AI assistance with coding
3. **Use skill shortcuts** - Mention a skill name to activate specialized guidance

## Activated Agents

| Agent | Purpose | Triggers |
|-------|---------|----------|
| **backend-developer** | Node.js/Python backend patterns | routes/, controllers/, services/, routers/ |
| **database-expert** | SQL optimization and database queries | models/, queries.py, database.* |
| **api-designer** | REST API endpoint design | routes/*, endpoint design discussions |
| **python-fastapi-expert** | FastAPI-specific patterns | routers/, async def, .py files |
| **debugging-assistant** | Troubleshooting and debugging | error, bug, debug keywords |
| **testing-specialist** | Unit and integration tests | tests/, .test.js, pytest files |

## Active Skills

### 1. Backend Development (Node.js)
**Applies to**: `routes/`, `controllers/`, `services/`, `**/*.js`

Covers:
- Express Router patterns
- MVC architecture
- Async/await standards
- Error handling middleware
- Service layer design

**Example**: When editing `routes/auth.js`, Copilot provides Express Router patterns and middleware setup guidance.

### 2. FastAPI Development (Python)
**Applies to**: `routers/`, `services/`, `**/*.py`

Covers:
- APIRouter pattern
- Dependency injection
- Pydantic schema validation
- Async endpoints
- HTTPException handling

**Example**: When editing `routers/datasets.py`, Copilot suggests async route patterns and dependency injection setups.

### 3. Database Optimization
**Applies to**: Database-related files in both backends

Covers:
- Connection pooling configuration
- Parameterized queries
- Query optimization
- Index strategy
- Transaction management

**Example**: When writing SQL queries, Copilot ensures they use parameterized queries and include proper indexes.

### 4. API Design
**Applies to**: Endpoint design and implementation

Covers:
- Response format standardization
- Error handling conventions
- HTTP status codes
- Request validation
- API documentation

**Example**: When creating a new endpoint, Copilot suggests the standard `{ success, data, meta }` response format.

### 5. Testing
**Applies to**: Test files and testing contexts

Covers:
- Unit test patterns (Jest/pytest)
- Integration test setup
- Mock and fixture usage
- Coverage best practices
- Continuous testing

**Example**: When writing tests, Copilot provides arrange-act-assert patterns and mocking strategies.

## Key Patterns

### Node.js Backend Pattern
```javascript
// routes → controllers → services → models → database
// All async/await, parameterized queries, centralized error handling
```

### Python Backend Pattern
```python
# APIRouter → Service Layer → Pydantic Schema → SQLAlchemy → Database
# All async, dependency injection, HTTPException handling
```

### Response Format (All APIs)
```json
{
  "success": true,
  "data": { /* payload */ },
  "meta": {
    "timestamp": "ISO-8601",
    "requestId": "unique-id"
  }
}
```

## Database Configuration

```
PostgreSQL: survey_db
Host: localhost:5432
User: postgres
Connection Pool: 10 connections
Max Overflow: 20 connections
Timeout: 10 seconds
```

## Common Tasks

### Adding a New API Endpoint

1. **Design the endpoint**: Use `api-design` skill
   - Define request/response schemas
   - Choose appropriate HTTP method
   - Plan error cases

2. **Implement in Node.js**:
   - Create route in `routes/`
   - Create controller in `controllers/`
   - Create service in `services/`
   - Use parameterized database queries

3. **OR Implement in FastAPI**:
   - Create route in `routers/`
   - Create service in `services/`
   - Define Pydantic schema
   - Use SQLAlchemy ORM

4. **Write tests**:
   - Unit tests for service logic
   - Integration tests for endpoint
   - Test both success and error cases

5. **Document**:
   - Add docstring with examples
   - Update API documentation
   - Include error codes

### Optimizing a Database Query

1. Activate `database-expert` agent
2. Review current query
3. Check for:
   - Parameterized safety
   - Column selection specificity
   - Index usage
   - JOIN efficiency
   - Pagination limits

### Debugging an Issue

1. Use `debugging-assistant` agent
2. Provide error message/logs
3. Agent suggests:
   - Root cause analysis
   - Common fixes
   - Testing strategies
   - Documentation links

## Copilot Chat Commands

```bash
# Activate specific agent
@copilot ask backend-developer to ...

# Activate specific skill
@copilot use database-optimization to ...

# Get project context
@copilot explain the database schema

# Suggest improvements
@copilot review this code for performance
```

## Standards Reference

### JavaScript/Node.js
- ✅ Use Express Router
- ✅ Use async/await
- ✅ Parameterize all queries
- ✅ Return standardized JSON
- ❌ Never mix callbacks with async
- ❌ Never concatenate SQL strings

### Python/FastAPI
- ✅ Use APIRouter
- ✅ Use async endpoints
- ✅ Use Pydantic schemas
- ✅ Use dependency injection
- ❌ Never use sync operations
- ❌ Never bypass type validation

### Database
- ✅ Use connection pooling
- ✅ Parameterize all queries
- ✅ Create appropriate indexes
- ✅ Use transactions for multi-step ops
- ❌ Never run unparameterized queries
- ❌ Never SELECT * from large tables

### API
- ✅ Use { success, data, meta } format
- ✅ Include proper error codes
- ✅ Validate all inputs
- ✅ Document with examples
- ❌ Never expose internal errors
- ❌ Never return sensitive data

### Testing
- ✅ Test success paths
- ✅ Test error cases
- ✅ Mock dependencies
- ✅ Use descriptive test names
- ✅ Maintain 80%+ coverage
- ❌ Never test implementation details
- ❌ Never skip edge cases

## Continuous Improvement

This configuration evolves with the project:

1. **New patterns discovered** → Update skill files
2. **Common issues fixed** → Document in guidelines
3. **Team preferences** → Add to standards
4. **Performance optimizations** → Update best practices

## Getting Help

- **General question**: Ask Copilot directly
- **Specific task**: Use `@copilot` with context
- **Bug fix**: Mention `@copilot debug`
- **Code review**: Ask `@copilot review`
- **Documentation**: Ask `@copilot document`

## Links

- **Main Configuration**: [.copilot-instructions.md](../.copilot-instructions.md)
- **Backend Development**: [skills/backend-development.md](skills/backend-development.md)
- **FastAPI Development**: [skills/fastapi-development.md](skills/fastapi-development.md)
- **Database Optimization**: [skills/database-optimization.md](skills/database-optimization.md)
- **API Design**: [skills/api-design.md](skills/api-design.md)
- **Testing Guide**: [skills/testing.md](skills/testing.md)

## Last Updated

**March 28, 2026** - Initial GitHub Copilot configuration setup

---

**Created with awesome-copilot best practices**  
Visit: https://github.com/github/awesome-copilot
