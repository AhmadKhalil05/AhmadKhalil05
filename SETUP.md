# AhmadKhalil05 — Terminal Profile README

A minimal, dark-mode native, terminal-inspired GitHub Profile with animated ASCII portrait, developer metadata, and dynamic contribution activity.

## Architecture

```
.github/
  workflows/
    update-profile.yml       # Daily automatic contribution & asset update
assets/
  profile-hero.svg           # Unified hero (ASCII portrait + profile metadata)
  contributions.svg          # Full-width interactive contribution heatmap
data/
  contributions.json         # Raw GitHub contribution history
scripts/
  fetch_contributions.py     # Pulls contribution stats from GitHub
  generate_profile.py        # Generates assets/profile-hero.svg
  generate_contributions.py  # Generates assets/contributions.svg
  prep_photo.py              # Photo preprocessing helper
source/
  profile-photo.png          # High-resolution source photo
profile-config.json          # Profile configuration & links
requirements.txt             # Python dependencies
README.md                    # Profile README
```

## Local Development & Regeneration

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Fetch latest contributions & generate SVGs
python scripts/fetch_contributions.py
python scripts/generate_contributions.py
python scripts/generate_profile.py

# 3. Commit & push
git add .
git commit -m "feat: update profile"
git push origin main
```

## Customization

- **Profile Details**: Edit `profile-config.json` and run `python scripts/generate_profile.py`.
- **Change Photo**: Replace `source/profile-photo.png` and run `python scripts/generate_profile.py`.
