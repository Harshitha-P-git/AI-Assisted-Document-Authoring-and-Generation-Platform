# ⚡ Quick Deployment Guide (5 Minutes)

## Fastest Way: Vercel + Railway

### Step 1: Push to GitHub (2 minutes)

```powershell
# If you haven't initialized git yet
git init
git add .
git commit -m "Ready for deployment"

# Create a new repository on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Railway (2 minutes)

1. Go to https://railway.app/
2. Click "Start a New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Click on the service → **Settings** → **Root Directory**: Set to `backend`
5. Go to **Variables** tab → Add these:
   ```
   SECRET_KEY=your-random-secret-key-here
   CORS_ORIGINS=https://your-frontend.vercel.app
   GEMINI_API_KEY=your-key
   OPENAI_API_KEY=your-key
   USE_OPENAI=true
   MOCK_LLM=false
   ```
6. Click **Settings** → **Generate Domain** → Copy your backend URL

✅ Backend URL: `https://your-app.up.railway.app`

### Step 3: Deploy Frontend to Vercel (1 minute)

1. Go to https://vercel.com/
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Create React App
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
5. Add Environment Variable:
   ```
   REACT_APP_API_URL=https://your-backend.up.railway.app/api/v1
   ```
   (Replace with your actual Railway backend URL)
6. Click "Deploy"

✅ Frontend URL: `https://your-app.vercel.app`

### Step 4: Update CORS (30 seconds)

1. Go back to Railway → Your Backend → Variables
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
3. Railway will auto-redeploy

### Step 5: Test Your Live App

1. Visit your Vercel URL
2. Register a new account
3. Create a project
4. Generate content

🎉 **Done! Your app is live!**

---

## Need Help?

- **Backend not starting?** Check Railway logs
- **CORS errors?** Make sure frontend URL is in CORS_ORIGINS
- **Frontend can't connect?** Check REACT_APP_API_URL is correct

For detailed instructions, see `DEPLOYMENT.md`

