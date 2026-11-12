# One-time setup

You do this once. Everything here is free. Button names on Google's and Meta's sites change now and then, so a label may differ slightly.

All keys go in this repo under **Settings → Secrets and variables → Actions**. "Secret" and "Variable" are two tabs on that page.

---

## Part A: Instagram (works straight away, no review needed)

Posting to your own account needs no Meta App Review.

1. **Make the Instagram account professional.** In Instagram: Settings → Account type and tools → Switch to professional account → Creator. Free.
2. **Create a Meta app.** Go to developers.facebook.com → My Apps → Create App. Pick the Instagram use case ("Manage messaging & content on Instagram").
3. In the app, open **Instagram → API setup with Instagram login**.
4. **Add yourself as a tester.** App roles → Roles → Add People → Instagram Tester → your Instagram username. Then in Instagram: Settings → Apps and websites → Tester invites → Accept.
5. Back in **API setup with Instagram login**, under "Generate access tokens", add your account and press **Generate token**. Allow the content publishing permission (`instagram_business_content_publish`). Copy the token and the Instagram user ID shown beside the account.
6. Add in GitHub:
   - Secret `IG_ACCESS_TOKEN` = the token
   - Secret `IG_USER_ID` = the number
   - Variable `INSTAGRAM_MODE` = `on`

**Token renewal.** The token lasts 60 days. To have it renewed automatically every week, create a fine-grained GitHub token (GitHub → Settings → Developer settings → Fine-grained tokens) limited to this repo with **Secrets: Read and write**, and save it as secret `GH_PAT`. Without it, repeat step 5 every 60 days.

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

### B3. Add in GitHub
- Secret `YT_CLIENT_ID`
- Secret `YT_CLIENT_SECRET`
- Secret `YT_REFRESH_TOKEN`
- Variable `YOUTUBE_MODE` = `private` for now

With `private`, uploads work but nobody can see them. That is enough to prove the app works for the audit.

### B4. The audit
Until Google audits the project, every upload made through it is locked as private and cannot be switched to public later. So keep uploading to YouTube by hand until approval.

1. Fill in the "YouTube API Services – Audit and Quota Extension Form" (search that name on Google's help site). Draft answers are in [youtube-audit-answers.md](youtube-audit-answers.md).
2. When Google emails that the project is approved, change variable `YOUTUBE_MODE` to `public`.

---

## Check it works

Actions → **Post due videos** → Run workflow → tick **Test only**. Read the log: it lists which platforms are on and what would be posted.
