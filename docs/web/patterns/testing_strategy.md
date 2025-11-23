# Unit Testing Guidelines

## Testing Framework

All tests must be written using pytest.

## Test Structure & Organization

### File and Package Structure

* The structure of the `tests/` package reflects the structure of the production code
* Test files should be named `test_*.py` to be automatically discovered by pytest
* Tests can be organized as functions or classes, but **prefer test functions for simplicity**
* Use test classes only when you need to group related tests or share fixtures within a logical unit
* Ensure you create `__init__.py` files for every new Python package
* Order tests to reflect the order of methods and functions in the to-be-tested code

### Function vs. Class-Based Tests

**Prefer test functions:**

```python
def test_create_user_with_valid_email():
    user = baker.make_recipe("account.user", email="test@example.com")
    assert user.email == "test@example.com"
```

**Use test classes when grouping is beneficial:**

```python
class TestUserPermissions:
    def test_admin_can_edit_all_users(self):
        # Test admin permissions
        pass

    def test_regular_user_can_only_edit_own_profile(self):
        # Test user permissions
        pass
```

## Test Design Principles

### Atomicity & Coverage

* Tests are atomic, meaning they cover only one case - avoid large tests covering every case
* Write at least one test per function or method
* Have one test per code branch in your testee, but don't overengineer
* Have one test case per edge case, not more
* Each test needs at least one assert statement - if a method returns nothing, use `assert result is None`
* Ensure that all code branches are covered for maintainer peace of mind when updating packages

### Test Patterns

* Stick to the AAA pattern: **Arrange / Act / Assert**
* Keep tests simple and understandable - avoid loops and strong abstractions
* Avoid type-hints in variable names (e.g., avoid `mymodel_qs`)
* Use blank lines to separate the three phases of AAA for readability

**Example:**

```python
def test_approve_system_updates_status():
    # Arrange
    system = baker.make_recipe("approval.software_system", status="pending")

    # Act
    system.approve()

    # Assert
    assert system.status == "approved"
    assert system.approved_at is not None
```

## Naming Conventions

* Test function names reflect the testee and test case: `test_[testee]_[test_case]`
* Use descriptive, readable names that explain what is being tested
* Avoid double underscores in names when testing protected methods
* Use semantically useful names like `manufacturer_with_product_id` instead of `mf1`

**Examples:**

```python
# Good
def test_create_release_with_valid_identifier():
    pass


def test_create_release_raises_error_when_identifier_is_duplicate():
    pass


# Bad
def test_release():  # Too vague
    pass


def test_create_release_1():  # Non-descriptive numbering
    pass
```

## Test Fixtures

### Pytest Fixtures

**Use pytest fixtures for setup and teardown:**

```python
import pytest
from model_bakery import baker


@pytest.fixture
def user():
    """Create a test user."""
    return baker.make_recipe("account.user")


@pytest.fixture
def admin_user():
    """Create a test admin user."""
    return baker.make_recipe("account.admin_user")


def test_user_can_login(user):
    # Use the user fixture
    assert user.is_authenticated
```

### Fixture Scope

Control fixture lifetime with scope:

* `function` (default): Created and destroyed for each test
* `class`: Shared across all methods in a test class
* `module`: Shared across all tests in a module
* `session`: Shared across all tests in the test session

### Django-Specific Fixtures

Pytest-django provides useful fixtures:

* `db`: Enables database access for a test
* `transactional_db`: For tests needing transactions
* `django_db_setup`: For session-scoped database setup
* `client`: Django test client
* `admin_client`: Authenticated admin client

### Fixture Best Practices

* Keep fixtures focused and single-purpose
* Use `autouse=True` sparingly - explicit is better than implicit
* Prefer composition to large fixtures - create small fixtures and combine them
* Use fixture factories for parameterized object creation

### Object Creation

* **Never create objects directly - always use model_bakery recipes**
* Never create objects via bakery without a recipe
* Try to create objects from factories in batches to optimize runtime
* Prefer fixtures for commonly used objects across multiple tests

## Assertions & Testing Practices

### Assertion Best Practices

* Pytest uses plain Python `assert` statements with intelligent introspection
* Avoid unittest-style assertions with `self.assert*`

### Testing Exceptions

Use `pytest.raises` context manager: # todo: wrong! we need to assert the error message

```python
import pytest
from django.core.exceptions import ValidationError


def test_create_user_with_invalid_email_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        baker.make_recipe("account.user", email="invalid")

    assert "email" in str(exc_info.value)
```

### Mocking Guidelines

* Use mocking as seldom as possible for first-party code since it tests implementation rather than functionality
* For higher-level methods, prefer testing the happy path over mocking
* Try to avoid mocking - a happy-path test is usually better than mocking
* Use `pytest-mock` fixture (`mocker`) or `unittest.mock` for mocking
* Use `mocker.patch()` for patching in tests


## Parametrized Tests

* Use `@pytest.mark.parametrize` to test multiple cases efficiently

## Import Guidelines

* Do not use local imports in test files
* Import test utilities and fixtures at the top of the file
* Use absolute imports from the project root

## Migration from Django Unittest

When migrating existing tests:

1. Replace `TestCase` classes with test functions or pytest-style test classes
2. Convert `setUp`/`setUpTestData` to pytest fixtures
3. Replace `self.assert*` with plain `assert` statements
4. Replace `self.assertRaises` with `pytest.raises`
5. Add `@pytest.mark.django_db` marker to tests that access the database
6. Use `mocker` fixture instead of `mock.patch` decorators
