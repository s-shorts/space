# One-time setup

You do this once. Everything here is free. Button names on GitHub's, Google's and Meta's sites change now and then, so a label may differ slightly.

---

## Part 0: Open your dashboard

1. **Switch the dashboard on.** In this repo: Settings → Pages → under "Build and deployment" choose **Deploy from a branch**, branch **main**, folder **/docs** → Save. After a minute or two the dashboard is at **https://s-shorts.github.io/space/**
2. **Make your GitHub key.** The dashboard's first screen lists the steps. The key needs Contents, Secrets and Actions set to "Read and write" for this repo only. Paste it into the dashboard. It is kept in your browser on that device and nowhere else; do not share it.

All the keys below are pasted into the dashboard's **Channels** tab. It encrypts them and saves them as GitHub secrets; nobody can read them back, not even you.

---

## Part A: Instagram (works straight away, no review needed)

Posting to your own account needs no Meta App Review.

1. **Make the Instagram account professional.** In Instagram: Settings → Account type and tools → Switch to professional account → Creator. Free.
2. **Create a Meta app.** Go to developers.facebook.com → My Apps → Create App. Pick the Instagram use case ("Manage messaging & content on Instagram").
3. In the app, open **Instagram → API setup with Instagram login**.
4. **Add yourself as a tester.** App roles → Roles → Add People → Instagram Tester → your Instagram username. Then in Instagram: Settings → Apps and websites → Tester invites → Accept.
5. Back in **API setup with Instagram login**, under "Generate access tokens", add your account and press **Generate token**. Allow the content publishing permission (`instagram_business_content_publish`). Copy the token and the Instagram user ID shown beside the account.
6. In the dashboard → Channels → your Instagram channel → "Add the key": paste the token and save. Then set the channel to **On**.

**More Instagram accounts.** Add each one as an Instagram Tester on the same Meta app (step 4), generate its token (step 5), then in the dashboard use "Add a channel" and paste that token.

**Token renewal.** Instagram tokens last 60 days. To have them renewed automatically every week, save a GitHub key as a secret named `GH_PAT` (repo Settings → Secrets and variables → Actions → New repository secret). A key like the dashboard one works; it needs **Secrets: Read and write**. Without it, repeat step 5 every 60 days.

---

## Part B: YouTube

### B1. Create the Google project
1. Go to console.cloud.google.com, sign in with the Google account that owns the channel, and create a new project (for example "Shorts Scheduler").
2. APIs & Services → Library → search **YouTube Data API v3** → Enable.
3. APIs & Services → OAuth consent screen: user type **External**, app name, your email. Add the scope `https://www.googleapis.com/auth/youtube.upload`.
4. On the same screen press **Publish app** so the status is "In production". If it stays in "Testing", the sign-in expires every 7 days.
5. APIs & Services → Credentials → Create credentials → **OAuth client ID** → type **Web application**. Under "Authorized redirect URIs" add exactly:
   `https://developers.google.com/oauthplayground`
   Copy the **Client ID** and **Client secret**.

### B2. Connect your channel (no code needed)
1. Open developers.google.com/oauthplayground.
2. Click the gear icon (top right) → tick **Use your own OAuth credentials** → paste the Client ID and Client secret.
3. On the left, in "Input your own scopes", paste `https://www.googleapis.com/auth/youtube.upload` → **Authorize APIs**.
4. Choose your channel. Google shows an "unverified app" warning because it is your own private app: Advanced → Go to (app name) → Allow.
5. Press **Exchange authorization code for tokens** and copy the **Refresh token**.

### B3. Add the keys in the dashboard
In Channels:
- "Google app keys": paste the Client ID and Client secret (once, shared by all YouTube channels).
- Your YouTube channel → "Add the key": paste the Refresh token.
- Set the channel to **Private test** for now.

With Private test, uploads work but nobody else can see them. That is enough to prove the app works for the audit.

**More YouTube channels.** Repeat B2 for each channel (choose that channel in step 4), then in the dashboard use "Add a channel" and paste its Refresh token. The Google app keys stay the same.

### B4. The audit
Until Google audits the project, every upload made through it is locked as private and cannot be switched to public later. So keep uploading to YouTube by hand until approval.

1. Fill in the "YouTube API Services – Audit and Quota Extension Form" (search that name on Google's help site). Draft answers are in [youtube-audit-answers.md](youtube-audit-answers.md).
2. When Google emails that the project is approved, set each YouTube channel to **Public** in the dashboard.

---

## Check it works

In the dashboard, add a video and press **Post now**, or wait for its time. The top of the dashboard shows whether the last check went fine. Full logs are in the repo's Actions tab.
