# Alembic Database Migration Guide

## Overview

Alembic is a database migration tool for SQLAlchemy. This guide covers setup, configuration, and all essential commands for managing database schema changes in this project.

## Initial Setup

### 1. Initialize Alembic

```bash
alembic init migrations
```

### 2. Configure env.py

Add the following imports at the top of `migrations/env.py`:

```python
from sqlmodel import SQLModel
from src.module.profile.model.profile_model import Profile
from src.module.resume.model.resume_model import Resume
```

### 3. Set target_metadata

In `migrations/env.py`, ensure:

```python
target_metadata = SQLModel.metadata
```

### 4. Configure Database URL

In `migrations/env.py`, add:

```python
config.set_main_option("sqlalchemy.url", os.getenv("POSTGRES_URL"))
```

## Essential Commands

### Creating Migrations

#### Auto-generate migration from model changes

```bash
alembic revision --autogenerate -m "Description of changes"
```

#### Create empty migration file

```bash
alembic revision -m "Description of changes"
```

#### Create migration with specific revision ID

```bash
alembic revision --rev-id abc123 -m "Description of changes"
```

### Running Migrations

#### Apply all pending migrations

```bash
alembic upgrade head
```

#### Apply migrations up to specific revision

```bash
alembic upgrade <revision_id>
```

#### Apply next migration only

```bash
alembic upgrade +1
```

#### Apply multiple migrations

```bash
alembic upgrade +3
```

### Downgrading Migrations

#### Downgrade to previous migration

```bash
alembic downgrade -1
```

#### Downgrade to specific revision

```bash
alembic downgrade <revision_id>
```

#### Downgrade to base (remove all migrations)

```bash
alembic downgrade base
```

#### Downgrade multiple migrations

```bash
alembic downgrade -3
```

### Migration History and Status

#### Show current migration status

```bash
alembic current
```

#### Show migration history

```bash
alembic history
```

#### Show detailed migration history

```bash
alembic history --verbose
```

#### Show migration history in reverse

```bash
alembic history --verbose --indicate-current
```

#### Show specific migration details

```bash
alembic show <revision_id>
```

#### Show current head revision

```bash
alembic heads
```

### Advanced Commands

#### Merge multiple heads

```bash
alembic merge -m "Merge message" <revision1> <revision2>
```

#### Stamp database to specific revision (without running migration)

```bash
alembic stamp <revision_id>
```

#### Stamp database to head

```bash
alembic stamp head
```

#### Check if database is up to date

```bash
alembic check
```

#### Show SQL that would be executed

```bash
alembic upgrade head --sql
```

#### Run migration in offline mode (generate SQL only)

```bash
alembic upgrade head --sql > migration.sql
```

### Configuration Commands

#### Show current configuration

```bash
alembic config
```

#### Show specific configuration value

```bash
alembic config sqlalchemy.url
```

#### Edit configuration

```bash
alembic config --set sqlalchemy.url="postgresql://user:pass@localhost/db"
```

## Common Workflows

### 1. Making Model Changes

```bash
# 1. Modify your SQLModel classes
# 2. Generate migration
alembic revision --autogenerate -m "Add new field to User model"
# 3. Review generated migration file
# 4. Apply migration
alembic upgrade head
```

### 2. Rolling Back Changes

```bash
# 1. Check current status
alembic current
# 2. Downgrade to previous revision
alembic downgrade -1
# 3. Or downgrade to specific revision
alembic downgrade abc123
```

### 3. Resolving Merge Conflicts

```bash
# 1. Check for multiple heads
alembic heads
# 2. Merge heads if needed
alembic merge -m "Merge feature branches" head1 head2
# 3. Apply merged migration
alembic upgrade head
```

### 4. Database Reset

```bash
# 1. Downgrade to base
alembic downgrade base
# 2. Apply all migrations from scratch
alembic upgrade head
```

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Use descriptive migration messages** that explain what changed
3. **Test migrations on a copy of production data** before applying to production
4. **Never edit applied migrations** - create new ones instead
5. **Keep migrations small and focused** on single logical changes
6. **Backup your database** before running migrations in production
7. **Use version control** to track all migration files

## Troubleshooting

### Common Issues

#### Migration conflicts

```bash
# Check for multiple heads
alembic heads
# Merge if necessary
alembic merge -m "Resolve conflicts" <head1> <head2>
```

#### Database out of sync

```bash
# Check current status
alembic current
# Stamp to correct revision if needed
alembic stamp <correct_revision>
```

#### Missing migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "Fix missing changes"
# Review and apply
alembic upgrade head
```

## Environment Variables

Ensure these environment variables are set:

- `POSTGRES_URL`: Database connection string
- Any other database configuration variables your application needs

## File Structure

```
migrations/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Migration template
└── versions/           # Migration files
    ├── 4f6e65ec8029_initial_migration.py
    └── ...
```
