# Photo asset fetcher

The video workspace cannot download photos from the web, so this branch does it through GitHub Actions.

1. Edit `request.json`: a new `id`, and up to 30 `files` (`name`, direct image `url` on an allowed host, `credit`, `licence`). Only public-domain or openly licensed images (CC0, CC BY, CC BY-SA), with the credit recorded.
2. Commit and push this branch. The workflow downloads the files and replaces the `assets` branch with them plus `manifest.json` (which repeats the `id` and says which files succeeded).
3. Wait until `manifest.json` on `assets` shows the new `id` (usually under a minute), then `git clone --depth 1 --branch assets`.

## AI-generated images and video
`request.json` may also hold a `generate` list (max 24): `{"name": "x.jpg", "prompt": "...", "width": 1920, "height": 1080, "seed": 1}` makes an AI image with Pollinations (free, no key, about one image every 16 seconds). With the repository secret `POLLINATIONS_API_KEY` set, images are faster and `{"kind": "video", "name": "x.mp4", "prompt": "...", "duration": 5, "model": "...", "image": "<start image URL>"}` makes a short AI video clip; `manifest.json` then lists the available models. Results are in `manifest.json` under `generated`.

## Free, watermark-free AI images (Cloudflare Workers AI)
With repository secrets `CF_ACCOUNT_ID` and `CF_API_TOKEN` (a free Cloudflare account; token with the "Workers AI" permission), every `generate` image goes to Cloudflare's FLUX.1 schnell instead of Pollinations: 1024x1024 JPEG, no watermark, about 170 images a day on the free tier (10,000 neurons/day, resets 00:00 UTC). Optional per item: `steps` (1-8, default 6), `seed`, `cf_model`, or `"provider": "pollinations"` to force Pollinations. Up to 40 images per request. `manifest.json` shows `"cloudflare": true` when the secrets are set and each generated item's `provider`.
