# SmartRoad AI — Free Cloud Deployment Guide

SmartRoad AI is designed for 100% free-tier cloud deployment using:
1. **GitHub Free** (Code repository & version control)
2. **Streamlit Community Cloud** (Zero-cost application hosting)
3. **Supabase Free Tier** (Managed PostgreSQL database, Auth, & Storage)

---

## 1. Supabase Free Setup (5 Minutes)

1. Sign up for free at [supabase.com](https://supabase.com).
2. Create a new organization and project named `smartroad-ai`.
3. In the Supabase Dashboard, open **SQL Editor**.
4. Paste and execute the contents of `database/schema.sql`.
5. Under **Storage**, create a new public bucket named `smartroad-images`.
6. Navigate to **Project Settings → API** and copy:
   - `Project URL`
   - `anon / public key`

---

## 2. GitHub Repository Push

1. Initialize git and commit:
   ```bash
   git add .
   git commit -m "feat: complete SmartRoad AI platform"
   ```
2. Create a new repository on GitHub (e.g., `smartroad-ai`).
3. Push your repository:
   ```bash
   git remote add origin https://github.com/<your-username>/smartroad-ai.git
   git branch -M main
   git push -u origin main
   ```

---

## 3. Deploy to Streamlit Community Cloud (Free)

1. Navigate to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**.
3. Select your repository: `<your-username>/smartroad-ai`, branch `main`, and main file path: `app.py`.
4. Click **Advanced settings → Secrets** and paste your environment variables:
   ```toml
   SUPABASE_URL = "https://your-project-id.supabase.co"
   SUPABASE_KEY = "your-supabase-anon-key"
   SUPABASE_BUCKET_NAME = "smartroad-images"
   WEIGHT_SEVERITY = "0.40"
   WEIGHT_TRAFFIC = "0.30"
   WEIGHT_REPEAT = "0.20"
   WEIGHT_SAFETY = "0.10"
   ```
5. Click **Deploy!**
   Your application will be live at `https://<your-app-name>.streamlit.app` with zero monthly cost.
