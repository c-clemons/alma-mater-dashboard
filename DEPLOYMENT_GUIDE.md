# GitHub + Streamlit Deployment Guide

## Quick Reference Commands

### First Time Setup

```bash
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model

git init
git add .
git commit -m "Initial commit - Alma Mater dashboard"
git remote add origin https://github.com/YOUR_USERNAME/alma-mater-dashboard.git
git branch -M main
git push -u origin main
```

### Future Updates

After making changes to your code:

```bash
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model

git add .
git commit -m "Updated dashboard features"
git push
```

Streamlit will auto-redeploy in 2-3 minutes!

---

## Detailed Steps

### 1. Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `alma-mater-dashboard`
3. Make it **Private**
4. **Don't** check any boxes (no README, no .gitignore)
5. Click "Create repository"
6. **Copy the URL** - you'll need it!

### 2. Push Your Code

Open Terminal and paste these commands **one at a time**:

```bash
# Navigate to project
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model

# Initialize git
git init

# Add all files
git add .

# Check what will be committed
git status

# Commit with message
git commit -m "Initial commit - Financial dashboard"

# Connect to GitHub (REPLACE with your actual repo URL!)
git remote add origin https://github.com/YOUR_USERNAME/alma-mater-dashboard.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**Important:** Replace `YOUR_USERNAME` with your GitHub username!

If you get an error about authentication, you may need to:
- Use a Personal Access Token instead of password
- Or use GitHub Desktop app (easier)

### 3. Deploy on Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Click "Sign in" (use your GitHub account)
3. Click "New app"
4. Fill in:
   - **Repository:** `YOUR_USERNAME/alma-mater-dashboard`
   - **Branch:** `main`
   - **Main file:** `app_client.py`
   - **App URL:** Choose a name like `almamater-financial`
5. Click "Deploy"
6. Wait 2-3 minutes

### 4. Your App is Live!

You'll get a URL like:
```
https://almamater-financial.streamlit.app
```

Share this with your client!

---

## Troubleshooting

### "Failed to install requirements"
- Check that `requirements_client.txt` exists
- Make sure all packages are spelled correctly

### "App failed to load"
- Check the logs in Streamlit Cloud
- Make sure `app_client.py` is in the root directory
- Verify all imports work

### "Can't push to GitHub"
If you get authentication errors:

**Option A: Personal Access Token**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select "repo" scope
4. Copy the token
5. Use it as your password when pushing

**Option B: GitHub Desktop (Easier!)**
1. Download GitHub Desktop
2. File → Add Local Repository
3. Choose your `alma_mater_model` folder
4. Click "Publish repository"
5. Done!

---

## Making Updates Later

Whenever you make changes:

```bash
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model

git add .
git commit -m "Description of what you changed"
git push
```

Streamlit Cloud will automatically detect the changes and redeploy in 2-3 minutes!

---

## Security Note

Your repo is **private**, so only people you invite can see the code.

Anyone with the Streamlit URL can view the dashboard, but they can't see your code or make changes.

If you want to restrict dashboard access too:
1. In Streamlit Cloud settings
2. Enable "Require login"
3. Add specific email addresses

---

## Files Already Configured

I've created:
- ✅ `.gitignore` - Excludes unnecessary files
- ✅ `README.md` - Project description
- ✅ `.streamlit/config.toml` - App configuration
- ✅ `requirements_client.txt` - Python dependencies

Everything is ready to deploy!

---

## Quick Start (If You Know Git)

```bash
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

Then deploy on https://share.streamlit.io/

**That's it!** 🚀
