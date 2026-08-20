# AhmadKhalil05 profile README — setup

## Fastest install

If the repo already exists locally:

```bash
cp -R . /path/to/AhmadKhalil05/
cd /path/to/AhmadKhalil05
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r scripts/requirements.txt
python scripts/prep_photo.py
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
git add .
git commit -m "feat: animated terminal profile"
git push origin main
```

The GitHub Action runs on the push, fetches the real contribution calendar, generates `contrib-heatmap.svg`, and commits the refreshed output.

## Change the portrait

Replace `source-photo.png` with a clear portrait, then run:

```bash
python scripts/prep_photo.py
python scripts/make_ascii_svg.py
```

Commit `source-photo.png`, `source-prepped.png`, and `ahmad-ascii.svg`.

## Change profile text

Edit `profile-config.json`, then run:

```bash
python scripts/make_info_card.py
```

## Manual refresh

Open GitHub → Actions → **Update profile art** → **Run workflow**.
