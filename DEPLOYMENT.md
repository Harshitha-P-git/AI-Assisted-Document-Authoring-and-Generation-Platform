# 🚀 Deployment Guide - Step-by-Step Instructions

This guide will help you deploy your AI Document Generator application to production.

## 📋 Table of Contents

1. [Quick Overview](#quick-overview)
2. [Option 1: Vercel (Frontend) + Railway (Backend) - RECOMMENDED](#option-1-vercel-frontend--railway-backend---recommended)
3. [Option 2: Netlify (Frontend) + Render (Backend)](#option-2-netlify-frontend--render-backend)
4. [Option 3: Full Docker Deployment](#option-3-full-docker-deployment)
5. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Quick Overview

Your application has two parts:
- **Frontend**: React app (needs to be built and hosted)
- **Backend**: FastAPI Python app (needs a server with Python)

**Recommended Approach**: Deploy frontend and backend separately for better scalability and easier management.

---

## Option 1: Vercel (Frontend) + Railway (Backend) - RECOMMENDED

This is the easiest and most reliable option for beginners.

### Part A: Deploy Backend to Railway

#### Step 1: Prepare Your Backend

1. **Create a `Procfile`** (for Railway):
   ```powershell
   cd backend
   ```
   Create a new file called `Procfile` (no extension) with this content:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Create `runtime.txt`** (optional, but recommended):
   Create a file called `runtime.txt` with:
   ```
   python-3.11
   ```

3. **Update `.env` for production**:
   Make sure your `.env` file has production-ready values:
   ```env
   SECRET_KEY=your-super-secret-key-generate-a-new-one
   DATABASE_URL=sqlite:///./app.db
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   GEMINI_API_KEY=your-gemini-api-key
   OPENAI_API_KEY=your-openai-api-key
   USE_OPENAI=true
   MOCK_LLM=false
   ```

#### Step 2: Push to GitHub

1. **Initialize Git** (if not already done):
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create a GitHub repository**:
   - Go to https://github.com/new
   - Name it: `ai-document-generator`
   - Make it **Private** (recommended)
   - Click "Create repository"

3. **Push your code**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/ai-document-generator.git
   git branch -M main
   git push -u origin main
   ```

#### Step 3: Deploy to Railway

1. **Sign up for Railway**:
   - Go to https://railway.app/
   - Click "Start a New Project"
   - Sign up with GitHub (recommended)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `ai-document-generator`

3. **Configure Backend Service**:
   - Railway will detect it's a Python project
   - Click on the service
   - Go to **Settings** → **Root Directory**: Set to `backend`
   - Go to **Variables** tab and add these environment variables:
     ```
     SECRET_KEY=your-generated-secret-key
     DATABASE_URL=sqlite:///./app.db
     CORS_ORIGINS=https://your-frontend-domain.vercel.app
     GEMINI_API_KEY=your-gemini-api-key
     OPENAI_API_KEY=your-openai-api-key
     USE_OPENAI=true
     MOCK_LLM=false
     PORT=8000
     ```

4. **Add PostgreSQL Database** (Optional but recommended):
   - In Railway dashboard, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` variable
   - Update your `DATABASE_URL` in Variables to use the PostgreSQL URL

5. **Deploy**:
   - Railway will automatically start deploying
   - Wait for deployment to complete (2-5 minutes)
   - Click on the service → **Settings** → **Generate Domain**
   - Copy your backend URL (e.g., `https://your-app.up.railway.app`)

✅ **Backend is now live!** Your backend URL: `https://your-app.up.railway.app`

---

### Part B: Deploy Frontend to Vercel

#### Step 1: Prepare Your Frontend

1. **Update API URL**:
   Create/update `frontend/.env.production`:
   ```env
   REACT_APP_API_URL=https://your-backend-url.up.railway.app/api/v1
   ```
   Replace `your-backend-url.up.railway.app` with your actual Railway backend URL.

2. **Update CORS in Backend**:
   Go back to Railway → Your Backend Service → Variables
   Update `CORS_ORIGINS` to include your Vercel URL:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app,https://your-backend.up.railway.app
   ```

#### Step 2: Deploy to Vercel

1. **Sign up for Vercel**:
   - Go to https://vercel.com/
   - Click "Sign Up"
   - Sign up with GitHub (recommended)

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import your GitHub repository: `ai-document-generator`

3. **Configure Project**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

4. **Add Environment Variables**:
   - Go to **Environment Variables** section
   - Add:
     ```
     REACT_APP_API_URL=https://your-backend-url.up.railway.app/api/v1
     ```
   - Replace with your actual Railway backend URL

5. **Deploy**:
   - Click "Deploy"
   - Wait for deployment (2-3 minutes)
   - Vercel will give you a URL like: `https://your-app.vercel.app`

✅ **Frontend is now live!** Your frontend URL: `https://your-app.vercel.app`

---

## Option 2: Netlify (Frontend) + Render (Backend)

### Part A: Deploy Backend to Render

1. **Sign up for Render**:
   - Go to https://render.com/
   - Sign up with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure Service**:
   - **Name**: `ai-doc-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///./app.db
   CORS_ORIGINS=https://your-frontend.netlify.app
   GEMINI_API_KEY=your-key
   OPENAI_API_KEY=your-key
   USE_OPENAI=true
   MOCK_LLM=false
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment
   - Copy your backend URL: `https://your-app.onrender.com`

### Part B: Deploy Frontend to Netlify

1. **Build your frontend locally**:
   ```powershell
   cd frontend
   npm run build
   ```

2. **Sign up for Netlify**:
   - Go to https://www.netlify.com/
   - Sign up with GitHub

3. **Deploy**:
   - Drag and drop your `frontend/build` folder to Netlify dashboard
   - OR: Connect GitHub repo → Select `frontend` folder → Build command: `npm run build` → Publish directory: `build`

4. **Add Environment Variable**:
   - Go to Site Settings → Environment Variables
   - Add: `REACT_APP_API_URL=https://your-backend.onrender.com/api/v1`

5. **Redeploy**:
   - Trigger a new deployment after adding environment variables

✅ **Your app is live!**

---

## Option 3: Full Docker Deployment

### Deploy to DigitalOcean App Platform

1. **Prepare Docker Compose**:
   - Your `docker-compose.yml` is already set up
   - Update environment variables in `docker-compose.yml`

2. **Sign up for DigitalOcean**:
   - Go to https://www.digitalocean.com/
   - Sign up

3. **Create App**:
   - Go to App Platform
   - Click "Create App"
   - Connect GitHub repository
   - Select your repo

4. **Configure Services**:
   - DigitalOcean will detect `docker-compose.yml`
   - Configure environment variables
   - Deploy

### Deploy to AWS/Azure/GCP

For cloud providers, you'll need to:
1. Set up a container registry (Docker Hub, AWS ECR, etc.)
2. Push your Docker images
3. Deploy using their container services (ECS, AKS, Cloud Run)

---

## Post-Deployment Checklist

### ✅ Backend Checklist

- [ ] Backend URL is accessible (test: `https://your-backend.com/docs`)
- [ ] Environment variables are set correctly
- [ ] CORS_ORIGINS includes your frontend URL
- [ ] Database is working (check logs)
- [ ] API keys (Gemini/OpenAI) are configured
- [ ] Test registration/login endpoints

### ✅ Frontend Checklist

- [ ] Frontend URL is accessible
- [ ] `REACT_APP_API_URL` points to your backend
- [ ] Can register a new user
- [ ] Can login
- [ ] Can create projects
- [ ] Can generate content
- [ ] Can export documents

### ✅ Security Checklist

- [ ] `SECRET_KEY` is strong and unique (not the default)
- [ ] `MOCK_LLM=false` in production
- [ ] CORS is properly configured
- [ ] HTTPS is enabled (Vercel/Railway provide this automatically)
- [ ] API keys are stored securely (not in code)

### ✅ Testing Your Live App

1. **Test Registration**:
   - Go to your frontend URL
   - Click "Sign Up"
   - Create a test account

2. **Test Login**:
   - Log in with your test account

3. **Test Project Creation**:
   - Create a new project
   - Add sections/slides
   - Generate content

4. **Test Export**:
   - Export a Word document
   - Export a PowerPoint presentation

---

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- **Solution**: Check Railway/Render logs
- Ensure all environment variables are set
- Verify `Procfile` or start command is correct

**Problem**: CORS errors
- **Solution**: Update `CORS_ORIGINS` to include your frontend URL
- Format: `https://your-frontend.vercel.app` (no trailing slash)

**Problem**: Database errors
- **Solution**: For SQLite, ensure write permissions
- For PostgreSQL, verify connection string

### Frontend Issues

**Problem**: Can't connect to backend
- **Solution**: Check `REACT_APP_API_URL` environment variable
- Ensure backend URL is correct (include `https://`)
- Check browser console for errors

**Problem**: Build fails
- **Solution**: Check build logs
- Ensure all dependencies are in `package.json`
- Try building locally first: `npm run build`

**Problem**: Environment variables not working
- **Solution**: Vercel/Netlify require redeployment after adding env vars
- Ensure variable names start with `REACT_APP_`

---

## Quick Reference: Environment Variables

### Backend (.env or Railway/Render Variables)

```env
SECRET_KEY=generate-a-secure-random-key
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=https://your-frontend.vercel.app
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
USE_OPENAI=true
MOCK_LLM=false
PORT=8000
```

### Frontend (Vercel/Netlify Environment Variables)

```env
REACT_APP_API_URL=https://your-backend.up.railway.app/api/v1
```

---

## Cost Estimates

### Free Tier Options:

- **Vercel**: Free tier includes unlimited deployments
- **Railway**: $5/month free credit (usually enough for small apps)
- **Render**: Free tier available (with limitations)
- **Netlify**: Free tier includes 100GB bandwidth/month

### Paid Options:

- **Railway**: ~$5-20/month depending on usage
- **Render**: ~$7-25/month for production
- **DigitalOcean**: ~$12/month minimum

---

## Need Help?

If you encounter issues:

1. Check the logs in your hosting platform
2. Verify all environment variables are set
3. Test backend API directly: `https://your-backend.com/docs`
4. Check browser console for frontend errors
5. Ensure CORS is configured correctly

---

## Next Steps After Deployment

1. **Set up a custom domain** (optional):
   - Vercel: Add domain in project settings
   - Railway: Add custom domain in service settings

2. **Set up monitoring**:
   - Add error tracking (Sentry, LogRocket)
   - Monitor API usage

3. **Backup your database**:
   - Set up automated backups
   - Export data regularly

4. **Optimize performance**:
   - Enable CDN caching
   - Optimize images
   - Use production builds

---

**Congratulations! Your app is now live! 🎉**

