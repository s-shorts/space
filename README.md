# Photo asset fetcher

The video workspace cannot download photos from the web, so this branch does it through GitHub Actions.

1. Edit `request.json`: a new `id`, and up to 30 `files` (`name`, direct image `url` on an allowed host, `credit`, `licence`). Only public-domain or openly licensed images (CC0, CC BY, CC BY-SA), with the credit recorded.
2. Commit and push this branch. The workflow downloads the files and replaces the `assets` branch with them plus `manifest.json` (which repeats the `id` and says which files succeeded).
3. Wait until `manifest.json` on `assets` shows the new `id` (usually under a minute), then `git clone --depth 1 --branch assets`.
