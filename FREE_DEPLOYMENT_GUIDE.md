# 🚀 FREE Deployment Guide - Zero Cost Launch

## 💰 Total Cost: $0/month

Deploy your JobTracker AI to real users completely FREE using these services:

## 🎯 Free Tier Services Stack

### 1. **Render.com** (Backend + Database + Redis)
- ✅ FREE PostgreSQL database (90 days, then $7/month)
- ✅ FREE Redis instance
- ✅ FREE web service (with limitations)
- ✅ Auto-deploy from GitHub
- ✅ HTTPS included

### 2. **Vercel** (Frontend)
- ✅ FREE React hosting
- ✅ Unlimited bandwidth
- ✅ Auto-deploy from GitHub
- ✅ HTTPS + CDN included
- ✅ Custom domain support

### 3. **Alternatives** (All Free)
- Railway.app (Backend + DB)
- Fly.io (Backend)
- Supabase (PostgreSQL)
- Netlify (Frontend)
- Cloudflare Pages (Frontend)

---

## 📋 Step-by-Step Deployment

### OPTION 1: Render.com (Recommended - Easiest)

#### Step 1: Deploy Database (PostgreSQL)

1. Go to https://render.com and sign up (free)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `jobtracker-db`
   - **Database**: `jobtracker`
   - **User**: `jobtracker_user`
   - **Region**: Choose closest to you
   - **Plan**: FREE
4. Click "Create Database"
5. **Copy the Internal Database URL** (starts with `postgresql://`)

#### Step 2: Deploy Redis

1. Click "New +" → "Redis"
2. Configure:
   - **Name**: `jobtracker-redis`
   - **Plan**: FREE
3. Click "Create Redis"
4. **Copy the Internal Redis URL** (starts with `redis://`)

#### Step 3: Deploy Backend

1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `amit0512-lab/jobtracker-ai`
3. Configure:
   - **Name**: `jobtracker-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && alembic upgrade head
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: FREE

4. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   APP_NAME=JobTracker
   APP_ENV=production
   DEBUG=False
   SECRET_KEY=<generate-a-strong-random-key>
   DATABASE_URL=<paste-internal-database-url-from-step-1>
   REDIS_URL=<paste-internal-redis-url-from-step-2>
   USE_LOCAL_STORAGE=True
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   OPENAI_API_KEY=<optional-your-key-or-leave-empty>
   ```

5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes)
7. **Copy your backend URL**: `https://jobtracker-backend.onrender.com`

#### Step 4: Deploy Frontend (Vercel)

1. Go to https://vercel.com and sign up (free)
2. Click "Add New" → "Project"
3. Import your GitHub repository: `amit0512-lab/jobtracker-ai`
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

5. **Add Environment Variable**:
   ```
   REACT_APP_API_URL=https://jobtracker-backend.onrender.com/api/v1
   ```

6. Click "Deploy"
7. Wait for deployment (2-3 minutes)
8. **Your app is live!** 🎉

#### Step 5: Update CORS

1. Go back to Render.com → Your backend service
2. Update `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-app-name.vercel.app
   ```
3. Save and redeploy

---

### OPTION 2: Railway.app (Alternative)

#### All-in-One Deployment

1. Go to https://railway.app and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect and deploy:
   - PostgreSQL database
   - Redis
   - Backend service
   - Frontend (optional)

5. Add environment variables in Railway dashboard
6. Get your deployment URLs
7. Update CORS settings

**Free Tier**: $5 credit/month (enough for small apps)

---

### OPTION 3: Fly.io (Advanced)

1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Login: `flyctl auth login`
3. Deploy backend:
   ```bash
   flyctl launch
   flyctl deploy
   ```
4. Deploy frontend on Vercel (same as Option 1)

---

## 🔧 Pre-Deployment Checklist

### 1. Update Backend for Production

Create `render.yaml` in root:
```yaml
services:
  - type: web
    name: jobtracker-backend
    env: python
    buildCommand: pip install -r requirements.txt && alembic upgrade head
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: APP_ENV
        value: production
      - key: DEBUG
        value: False

databases:
  - name: jobtracker-db
    databaseName: jobtracker
    user: jobtracker_user
```

### 2. Update Frontend API URL

In `frontend/.env.production`:
```env
REACT_APP_API_URL=https://your-backend-url.onrender.com/api/v1
```

### 3. Generate Strong SECRET_KEY

Run locally:
```bash
python generate_secret_key.py
```
Copy the output and use it in environment variables.

### 4. Update CORS in `app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Your Vercel URL
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

---

## 📊 Free Tier Limitations

### Render.com FREE Tier
- ✅ Unlimited apps
- ⚠️ Spins down after 15 min of inactivity (cold start ~30s)
- ⚠️ 750 hours/month (enough for 1 app 24/7)
- ⚠️ PostgreSQL free for 90 days, then $7/month
- ✅ 100GB bandwidth/month

### Vercel FREE Tier
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Unlimited team members
- ✅ Custom domains
- ✅ Automatic HTTPS

### Railway FREE Tier
- ✅ $5 credit/month
- ✅ Enough for small apps
- ✅ No cold starts
- ⚠️ Credit runs out if high traffic

---

## 🚀 Quick Deploy Commands

### Deploy to Render (using render.yaml)

1. Push `render.yaml` to GitHub
2. Connect repository in Render dashboard
3. Render auto-deploys everything

### Deploy Frontend to Vercel

```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

---

## 🔒 Security for Production

### 1. Environment Variables (CRITICAL)

Never commit these to GitHub:
- `SECRET_KEY` - Generate new strong key
- `DATABASE_URL` - Use Render's internal URL
- `REDIS_URL` - Use Render's internal URL
- `OPENAI_API_KEY` - Optional, keep secret

### 2. Update `.env.example`

```env
# Production Environment Variables
APP_NAME=JobTracker
APP_ENV=production
DEBUG=False
SECRET_KEY=<generate-strong-key>
DATABASE_URL=<render-provides-this>
REDIS_URL=<render-provides-this>
ALLOWED_ORIGINS=https://your-app.vercel.app
USE_LOCAL_STORAGE=True
```

### 3. Enable Email Verification (Optional)

For production, enable OTP verification:
1. Get free SMTP from Gmail (App Password)
2. Add to environment variables:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```
3. Uncomment verification code in `auth_controller.py`

---

## 📈 Monitoring (Free)

### 1. Render Dashboard
- View logs
- Monitor uptime
- Check resource usage

### 2. Vercel Analytics
- Page views
- Performance metrics
- Error tracking

### 3. UptimeRobot (Free)
- Monitor uptime
- Get alerts if site goes down
- https://uptimerobot.com

---

## 🎯 Post-Deployment Steps

### 1. Test Your Deployment

```bash
# Test backend
curl https://your-backend.onrender.com/health

# Test frontend
# Open https://your-app.vercel.app in browser
```

### 2. Create First User

1. Go to your app URL
2. Click "Register"
3. Create account
4. Start using!

### 3. Share with Users

Your app is now live at:
- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.onrender.com

---

## 💡 Tips for FREE Hosting

### 1. Prevent Cold Starts (Render)

Use a free uptime monitor to ping your app every 10 minutes:
- UptimeRobot: https://uptimerobot.com
- Ping URL: `https://your-backend.onrender.com/health`

### 2. Optimize for Free Tier

- Use local storage (no S3 costs)
- Template-based cover letters (no OpenAI costs)
- Efficient database queries
- Cache frequently accessed data

### 3. Scale Later

When you outgrow free tier:
- Render: $7/month for PostgreSQL
- Railway: $5/month for more resources
- Vercel: Free tier is usually enough

---

## 🆘 Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify environment variables
- Ensure `requirements.txt` is correct
- Check Python version (3.11)

### Frontend can't connect to backend
- Verify `REACT_APP_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running

### Database connection fails
- Use Render's **Internal Database URL**
- Don't use external URL (costs money)
- Check DATABASE_URL format

### Cold start is slow
- Normal for free tier (15-30 seconds)
- Use UptimeRobot to keep it warm
- Or upgrade to paid tier ($7/month)

---

## 📚 Additional Resources

### Documentation
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app

### Tutorials
- Deploy FastAPI: https://render.com/docs/deploy-fastapi
- Deploy React: https://vercel.com/guides/deploying-react-with-vercel

### Support
- Render Community: https://community.render.com
- Vercel Discord: https://vercel.com/discord

---

## ✅ Deployment Checklist

- [ ] Create Render account
- [ ] Deploy PostgreSQL database
- [ ] Deploy Redis
- [ ] Deploy backend service
- [ ] Add environment variables
- [ ] Create Vercel account
- [ ] Deploy frontend
- [ ] Update CORS settings
- [ ] Test registration
- [ ] Test login
- [ ] Test all features
- [ ] Set up uptime monitoring
- [ ] Share with users!

---

## 🎉 You're Live!

Your JobTracker AI is now deployed and accessible to real users at **ZERO COST**!

**Next Steps:**
1. Share your app URL with friends
2. Gather feedback
3. Monitor usage
4. Scale when needed

**Your App URLs:**
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.onrender.com`
- API Docs: `https://your-backend.onrender.com/docs`

---

**Deployment Date**: March 5, 2026  
**Cost**: $0/month  
**Status**: ✅ PRODUCTION READY  
**Users**: ∞ (unlimited on free tier)

🚀 **Happy Launching!**
