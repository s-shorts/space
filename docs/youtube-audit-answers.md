# YouTube API audit: draft answers

Form: **YouTube API Services – Audit and Quota Extension Form** (Google help site). Submit it signed in as the Google account that owns the Cloud project.

Fill the items in [brackets] yourself. Check every answer is true for you before sending. Approval is Google's decision and is not guaranteed; they may email follow-up questions.

| Question | Draft answer |
|---|---|
| Name / organisation | [Your name]. Individual creator, no company. |
| Contact email | [The email on the Cloud project] |
| Project number | [Cloud Console → project dashboard → "Project number"] |
| API client name | Shorts Scheduler |
| Website / where the client runs | https://github.com/s-shorts/space (a scheduled GitHub Actions job; there is no public website or sign-in page) |
| Who uses the client | Only me. It is an internal tool for my own YouTube channel [channel URL]. No other users can sign in. |
| Is it available to the public? | No. |
| Does it monetise or show ads? | No. |

**Describe the API client and its use case**

> Shorts Scheduler is a private tool I use to publish my own original videos to my own YouTube channel at set times. A scheduled job reads a queue of video files I have prepared, and at each video's scheduled time it calls `videos.insert` to upload the file with its title, description and tags. It is used only by me, for one channel. It has no other users and no public interface.

**Which API services and methods are used**

> YouTube Data API v3, `videos.insert` only, with the single scope `youtube.upload`. The client does not read, store or display any YouTube data, does not access other users' data, and does not use comments, analytics, search or playback.

**Expected usage**

> Up to 6 uploads per day. No quota extension is requested; the default quota is enough.

**How user data is handled**

> The only authorised user is me. The OAuth refresh token is stored as an encrypted GitHub Actions secret and is used solely to upload my videos. No YouTube API data is stored, shared or sold. I can revoke access at any time from my Google Account permissions page.

**Content**

> Original short educational science videos (space, Earth history, wildlife) that I produce. Facts are checked against sources such as NASA and ESA. Videos comply with YouTube's Community Guidelines, and altered or synthetic content is disclosed where YouTube requires it.

**Things Google may ask for**

- A screenshot or short screen recording of the tool working: record the Actions run log of a `private` test upload, plus the video appearing in YouTube Studio.
- A privacy policy link. A short page in this repo stating the points under "How user data is handled" is usually what they want; ask Claude to add one if requested.
