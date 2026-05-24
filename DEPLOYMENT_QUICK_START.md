# Phase 4: Quick Start Deployment

**Get your app live in 10 minutes!**

---

## 📋 Prerequisites

- [ ] GitHub account (with your project repo)
- [ ] Railway account (free, takes 2 minutes)
- [ ] Project pushed to GitHub

---

## 🚀 Deploy in 5 Steps

### Step 1: Create Railway Account
Go to **https://railway.app** → Sign up with GitHub → Authorize

### Step 2: Create New Project
Railway dashboard → **"New Project"** → **"Deploy from GitHub"** → Select your repository

### Step 3: Configure Variables
Go to **"Variables"** tab and add:
```
FLASK_ENV=production
SECRET_KEY=any-random-string-here-will-work-for-demo
```

### Step 4: Deploy
Click the **"Deploy"** button. Watch the logs turn green.

### Step 5: Get Your URL
Go to **"Domains"** tab → Click your app URL (looks like `app-abc123.railway.app`)

**Done! Your app is live! 🎉**

---

## ✅ Test Your Deployment

1. **Homepage:** Visit your URL
2. **Analyzer:** Go to `/analyzer`
3. **Test Analysis:** Paste email text and click Analyze

---

## 📝 Files Needed

✅ All created for you in Phase3_development/:
- `wsgi.py` - Production entry point
- `Procfile` - Deployment instructions
- `requirements.txt` - Updated with gunicorn
- `runtime.txt` - Python version
- `.env.example` - Environment template
- `config.py` - Updated for production

---

## 🔐 Generate Secure Secret Key

If you want a more secure key, run this in Python:
```python
import secrets
print(secrets.token_hex(32))
```
Then paste the output as your `SECRET_KEY` in Railway variables.

---

## 🔄 Update Your App

After making changes:
```bash
git add .
git commit -m "Update: description"
git push origin main
```

Railway auto-deploys within seconds!

---

## ❌ If Something Goes Wrong

### Check Logs
1. Railway dashboard → Your app
2. Click "Logs" tab
3. Read error messages

### Common Fixes
- **Model not found:** Check model files are in repo
- **Port error:** Set PORT environment variable
- **Module not found:** Update requirements.txt
- **Import error:** Check config.py paths

---

## 🎯 Next Steps

1. ✅ Deploy app
2. ✅ Get live URL
3. ✅ Share with others
4. ✅ Show in presentations
5. ✅ Add to portfolio

---

## 📊 Monitoring

### View Logs Anytime
Railway dashboard → Logs tab → Live feed of requests

### Check Status
Visit: `https://your-url.railway.app/api/status`

---

## 💡 Pro Tips

- **First request slow?** Normal - model is loading
- **Subsequent requests fast?** Expected behavior
- **Add error handling?** Check logs for issues
- **Want custom domain?** Railway supports it (paid or free)

---

## ❓ Need Help?

1. Check PHASE4_DEPLOYMENT_GUIDE.md for detailed instructions
2. Review Railway documentation: https://docs.railway.app
3. Check app logs for specific error messages

---

**You're ready to deploy! Good luck! 🚀**
