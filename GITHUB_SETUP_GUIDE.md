# GitHub Setup Guide for MyCIRCLE Project

## Pre-Deployment Checklist

### 1. Secure Sensitive Files ✓

The following files should **NOT** be committed:
- `instance/config.py` - Contains SECRET_KEY (template provided: `instance/config.py.example`)
- `.env` - Environment variables (template provided: `.env.example`)
- `vcircleapp/` - Virtual environment folder
- `__pycache__/` - Python cache files
- Migration database files

All these are already configured in `.gitignore`.

### 2. Environment Variables Setup

Before running the project locally, set up your environment:

#### Option A: Using .env file (Development)
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Edit `.env` and fill in your actual credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_actual_password
   DB_NAME=mycircledb
   SECRET_KEY=your_generated_secret_key
   ```

#### Option B: Using instance/config.py (Current Setup)
1. Copy `instance/config.py.example` to `instance/config.py`:
   ```bash
   copy instance\config.py.example instance\config.py
   ```
2. Edit `instance/config.py` with your actual secret key:
   ```python
   SECRET_KEY='your_actual_secret_key_here'
   ```

### 3. Database Configuration

Update your database credentials in one of these files:
- `.env` (if using python-dotenv)
- `mycirclepkg/config.py` - **This file WILL be tracked, so use environment variables**

**IMPORTANT**: Update `mycirclepkg/config.py` to use environment variables instead of hardcoded credentials:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class General(object):
    APP_NAME = 'MYCircle'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'mysql+mysqlconnector://root@localhost/mycircledb'
    )
    SQLALCHEMY_TRACK_MODIFICATION = False

class LiveConfig(General):
    DATABASE = 'mycircledb'
    
class TestConfig(General):
    DATABASE = 'mycircledb'
```

## Steps to Push to GitHub

### Initial Setup (First Time)

1. **Initialize Git repository**:
   ```bash
   cd c:\Users\HomePC\Desktop\mycircle\mycircleapp
   git init
   ```

2. **Configure Git**:
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

3. **Create initial commit**:
   ```bash
   git add .
   git commit -m "Initial commit: MyCIRCLE project setup"
   ```

### Create Repository on GitHub

1. Go to [GitHub.com](https://github.com)
2. Log in to your account (or sign up if needed)
3. Click "New" (top left, under your avatar) or go to github.com/new
4. Fill in:
   - **Repository name**: `mycircle` (or your preferred name)
   - **Description**: "A Flask-based web platform for community engagement"
   - **Public/Private**: Choose based on your preference
   - **DO NOT** initialize with README, .gitignore, or license (you have your own)
5. Click "Create repository"

### Connect Local Repository to GitHub

1. **Add remote connection**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/mycircle.git
   ```
   Or if using SSH:
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/mycircle.git
   ```

2. **Rename branch to main** (if needed):
   ```bash
   git branch -M main
   ```

3. **Push to GitHub**:
   ```bash
   git push -u origin main
   ```

### For Future Updates

After initial setup, use these commands:

```bash
# Check status
git status

# Stage changes
git add .
# or add specific files:
# git add mycirclepkg/
# git add requirements.txt

# Commit
git commit -m "Your descriptive commit message"

# Push to GitHub
git push origin main
```

## What Gets Tracked

### ✅ WILL be pushed to GitHub:
- `mycirclepkg/` - All source code
- `templates/` - HTML templates
- `static/` (except uploads) - CSS, JS, Font Awesome
- `migrations/versions/` - Database migration scripts
- `run.py` - Application entry point
- `requirements.txt` - Python dependencies
- `PROJECT_DOCUMENTATION.md` - Documentation
- `.gitignore` - Git configuration
- `.env.example` - Template for environment variables
- `instance/config.py.example` - Template for instance config
- `README.md` - (Create one if needed)

### ❌ NOT pushed to GitHub:
- `vcircleapp/` - Virtual environment
- `__pycache__/` - Python cache
- `instance/config.py` - Actual configuration with SECRET_KEY
- `.env` - Actual environment variables
- `mycirclepkg/static/uploads/*` - User-uploaded files
- `*.pyc` - Compiled Python files

## After Cloning on Another Machine

When someone (including you) clones this project on another machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mycircle.git
   cd mycircle
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv vcircleapp
   vcircleapp\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration files**:
   - Copy `instance/config.py.example` to `instance/config.py`
   - Copy `.env.example` to `.env`
   - Fill in actual values (database credentials, secret key, etc.)

5. **Set up database**:
   ```bash
   flask db upgrade
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

## Important Security Notes

1. **Never commit sensitive data**: Credentials, secret keys, and API keys should only be in `.env` or local config files.

2. **Generate a strong SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Use this command to generate a cryptographically secure key.

3. **Database credentials**: Store in `.env` file for development, and use environment variables in production.

4. **Review before pushing**: Always run `git status` and `git diff` before committing to ensure no sensitive data is included.

## Troubleshooting

### "Failed to push" errors:
- Check your internet connection
- Verify your GitHub credentials
- Ensure the repository on GitHub exists
- Use `git remote -v` to verify the correct remote URL

### ".gitignore not working":
If files that should be ignored are already tracked:
```bash
git rm --cached instance/config.py
git rm --cached .env
git commit -m "Remove sensitive files from tracking"
git push
```

### Need to update .env variables without committing:
```bash
# Add .env to .gitignore (already done)
# Files in .env won't affect other developers since they use .env.example
```

## Additional Recommendations

1. **Create a README.md** with project setup instructions
2. **Add a LICENSE** file (MIT, Apache 2.0, etc.)
3. **Consider adding**:
   - `.github/CONTRIBUTING.md` - Contribution guidelines
   - `.github/ISSUE_TEMPLATE/` - Issue templates
   - `tests/` - Unit tests

---

**You're ready to push to GitHub! Happy coding! 🚀**
