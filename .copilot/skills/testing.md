# Skill: Testing & Quality Assurance
# Survey-AI Dataset Explorer System

## Scope
This skill applies to all testing activities in the Survey-AI project (unit, integration, and end-to-end tests).

## Testing Strategy

### Test Pyramid
```
        E2E Tests (5%)
       /            \
   Integration Tests (25%)
    /                 \
   Unit Tests (70%)
```

## Unit Testing

### Node.js Unit Tests (Jest)

**Test Structure**
```javascript
// tests/unit/authService.test.js
const authService = require('../../services/authService');
const pool = require('../../config/database');

jest.mock('../../config/database');
jest.mock('bcrypt');
jest.mock('jsonwebtoken');

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should return user and token on valid credentials', async () => {
      // Arrange
      const email = 'test@example.com';
      const password = 'password123';
      const mockUser = { id: 1, email, password: 'hashed_pwd' };
      
      pool.query.mockResolvedValueOnce({ rows: [mockUser] });
      bcrypt.compare.mockResolvedValueOnce(true);
      jwt.sign.mockReturnValueOnce('jwt-token');

      // Act
      const result = await authService.login(email, password);

      // Assert
      expect(result.user.email).toBe(email);
      expect(result.token).toBe('jwt-token');
      expect(pool.query).toHaveBeenCalledWith(
        'SELECT * FROM users WHERE email = $1',
        [email]
      );
    });

    it('should throw error on invalid email', async () => {
      const email = 'invalid-email';
      const password = 'password123';

      pool.query.mockResolvedValueOnce({ rows: [] });

      await expect(
        authService.login(email, password)
      ).rejects.toThrow('User not found');
    });

    it('should throw error on invalid password', async () => {
      const email = 'test@example.com';
      const password = 'wrong-password';
      const mockUser = { id: 1, email, password: 'hashed_pwd' };

      pool.query.mockResolvedValueOnce({ rows: [mockUser] });
      bcrypt.compare.mockResolvedValueOnce(false);

      await expect(
        authService.login(email, password)
      ).rejects.toThrow('Invalid credentials');
    });
  });
});
```

**Testing Best Practices**
- One test per behavior
- Use arrange-act-assert pattern
- Mock external dependencies
- Use descriptive test names
- Test both success and failure cases
- Use beforeEach/afterEach for cleanup

### Python Unit Tests (pytest)

**Test Structure**
```python
# tests/unit/test_dataset_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.dataset_service import DatasetService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def dataset_service(mock_db):
    return DatasetService(mock_db)

class TestDatasetService:
    
    @pytest.mark.asyncio
    async def test_get_hierarchical_datasets(self, dataset_service, mock_db):
        # Arrange
        mock_tables = [
            ('hces_household',),
            ('plfs_labour',),
            ('survey_data',)
        ]
        mock_db.execute.return_value.fetchall.return_value = mock_tables
        
        # Act
        result = await dataset_service.get_hierarchical_datasets()
        
        # Assert
        assert 'HCES' in result
        assert 'hces_household' in result['HCES']
        assert len(result['HCES']) == 1
        assert len(result['PLFS']) == 1

    @pytest.mark.asyncio
    async def test_get_dataset_metadata(self, dataset_service, mock_db):
        # Arrange
        dataset_id = 'hces_household'
        mock_columns = [
            ('household_id', 'integer', False, None),
            ('state', 'varchar', False, None),
            ('quantity', 'float', True, None)
        ]
        mock_db.execute.return_value.fetchall.return_value = mock_columns
        
        # Act
        metadata = await dataset_service.get_metadata(dataset_id)
        
        # Assert
        assert len(metadata['columns']) == 3
        assert metadata['columns'][0]['name'] == 'household_id'
        assert metadata['columns'][0]['type'] == 'integer'

    def test_invalid_dataset_id(self, dataset_service, mock_db):
        # Arrange
        dataset_id = 'invalid_dataset'
        mock_db.execute.return_value.fetchall.return_value = []
        
        # Act & Assert
        with pytest.raises(ValueError):
            dataset_service.get_metadata(dataset_id)
```

**Running Tests**
```bash
# Node.js
npm test                    # Run all tests
npm test -- --coverage      # With coverage report
npm test authService.test   # Single test file

# Python
pytest                      # Run all tests
pytest --cov               # With coverage
pytest tests/unit/         # Specific directory
pytest -k "test_login"     # Specific test pattern
```

## Integration Testing

### API Integration Tests (Node.js)

**Test Structure**
```javascript
// tests/integration/auth.integration.test.js
const request = require('supertest');
const app = require('../../app');
const pool = require('../../config/database');

describe('Authentication API', () => {
  
  describe('POST /api/auth/register', () => {
    it('should register new user successfully', async () => {
      // Arrange
      const newUser = {
        email: 'newuser@example.com',
        password: 'password123',
        name: 'New User'
      };

      // Act
      const response = await request(app)
        .post('/api/auth/register')
        .send(newUser)
        .expect(201);

      // Assert
      expect(response.body.success).toBe(true);
      expect(response.body.data.user.email).toBe(newUser.email);
      expect(response.body.data.token).toBeDefined();
      
      // Verify in database
      const dbResult = await pool.query(
        'SELECT * FROM users WHERE email = $1',
        [newUser.email]
      );
      expect(dbResult.rows.length).toBe(1);
    });

    it('should reject duplicate email', async () => {
      // Arrange
      const existingUser = {
        email: 'existing@example.com',
        password: 'password123',
        name: 'Existing User'
      };
      
      // Setup: Create user first
      await pool.query(
        'INSERT INTO users (email, password, name) VALUES ($1, $2, $3)',
        [existingUser.email, 'hashed', existingUser.name]
      );

      // Act
      const response = await request(app)
        .post('/api/auth/register')
        .send(existingUser)
        .expect(409);

      // Assert
      expect(response.body.success).toBe(false);
      expect(response.body.code).toBe('EMAIL_EXISTS');
    });

    it('should validate email format', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({
          email: 'invalid-email',
          password: 'password123',
          name: 'User'
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.code).toBe('INVALID_EMAIL');
    });
  });

  describe('POST /api/auth/login', () => {
    it('should login user with correct credentials', async () => {
      // Arrange
      const user = {
        email: 'test@example.com',
        password: 'password123'
      };
      
      // Setup: Create user
      // (Use factory or fixtures)

      // Act
      const response = await request(app)
        .post('/api/auth/login')
        .send(user)
        .expect(200);

      // Assert
      expect(response.body.success).toBe(true);
      expect(response.body.data.token).toBeDefined();
    });
  });
});
```

### FastAPI Integration Tests (Python)

**Test Structure**
```python
# tests/integration/test_datasets_api.py
import pytest
from fastapi.testclient import TestClient
from main import app
from database.connection import get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    # Setup test database
    from database.connection import SessionLocal
    db = SessionLocal()
    yield db
    db.close()

class TestDatasetsAPI:
    
    def test_get_hierarchical_datasets(self):
        # Act
        response = client.get("/datasets/hierarchical")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'HCES' in data['data']
        assert 'PLFS' in data['data']
        assert isinstance(data['data']['HCES'], list)

    def test_get_dataset_metadata(self, test_db):
        # Act
        response = client.get("/datasets/hces_household/metadata")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['id'] == 'hces_household'
        assert 'columns' in data['data']

    def test_get_nonexistent_dataset(self):
        # Act
        response = client.get("/datasets/nonexistent/metadata")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
        assert data['code'] == 'NOT_FOUND'

    def test_dataset_preview_pagination(self):
        # Act
        response = client.get("/datasets/hces_household/preview?limit=5&offset=0")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data['data']['rows']) <= 5
        assert data['meta']['pagination']['limit'] == 5
        assert data['meta']['pagination']['offset'] == 0
```

## Test Data Fixtures

### Database Fixtures
```python
# tests/fixtures/database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine('sqlite:///:memory:')
    # Create tables
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def test_session(test_db):
    """Create test session"""
    connection = test_db.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_user(test_session):
    """Create sample user for tests"""
    user = User(
        email='test@example.com',
        password='hashed_password',
        role='researcher'
    )
    test_session.add(user)
    test_session.commit()
    return user
```

## Test Coverage

### Coverage Goals
- Unit tests: 80%+ coverage
- Integration tests: 60%+ coverage
- Critical paths: 100% coverage

### Generate Coverage Report
```bash
# Node.js
npm test -- --coverage --coverageDirectory=./coverage

# Python
pytest --cov=app --cov-report=html
```

## Continuous Testing

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: survey_db
          POSTGRES_PASSWORD: postgres
          
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm install
    
    - name: Run tests
      run: npm test -- --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Testing Checklist

- [ ] Write unit tests for service functions
- [ ] Write integration tests for endpoints
- [ ] Test all success paths
- [ ] Test all error conditions
- [ ] Test edge cases (empty data, null values)
- [ ] Test boundary conditions
- [ ] Mock external dependencies
- [ ] Use test fixtures
- [ ] Validate response format
- [ ] Validate response codes
- [ ] Check error messages
- [ ] Verify database changes
- [ ] Maintain 80%+ coverage

## Common Testing Patterns

### Testing Async Functions
```javascript
// Node.js
it('should test async function', async () => {
  const result = await asyncFunction();
  expect(result).toBeDefined();
});
```

```python
# Python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Testing Error Handling
```javascript
it('should throw validation error', () => {
  expect(() => {
    validateEmail('invalid');
  }).toThrow(ValidationError);
});
```

```python
def test_validation_error():
    with pytest.raises(ValidationError):
        validate_email('invalid')
```

### Testing Database Transactions
```javascript
it('should rollback on error', async () => {
  await expect(multiStepOperation()).rejects.toThrow();
  
  const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  expect(result.rows).toHaveLength(0); // Not inserted
});
```

## When to Activate This Skill
- Writing new tests
- Troubleshooting test failures
- Improving test coverage
- Creating fixtures and mocks
- Setting up test infrastructure
- Debugging flaky tests

## Related Skills
- backend-development (for route testing)
- fastapi-development (for endpoint testing)
- database-optimization (for query testing)
- debugging-assistant (for test debugging)

## Testing Tools Reference
- **Node.js**: Jest, Supertest, nock
- **Python**: pytest, pytest-asyncio, httpx
- **Coverage**: jest --coverage, pytest --cov
- **Mocking**: jest.mock(), unittest.mock
