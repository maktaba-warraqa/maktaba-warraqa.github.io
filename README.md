# Maktaba Warraqa website

Static, JavaScript-free site in French, English and Arabic (22 pages). Built with `build.py`, deployed free on GitHub Pages by the workflow in `.github/workflows/pages.yml`.

## Deploy (5 minutes)

1. Create a public GitHub repository and push this folder to the `main` branch.
   - Repository named `USERNAME.github.io` gives `https://USERNAME.github.io/` (best: `robots.txt` and `llms.txt` only work at a domain root).
   - Any other name gives `https://USERNAME.github.io/REPO/` (works, but robots.txt is ignored by crawlers).
2. In the repository: Settings > Pages > Build and deployment > Source: **GitHub Actions**.
3. Push a commit (or run the workflow from the Actions tab). The workflow builds the site with the correct URL automatically (canonical, hreflang, sitemap, JSON-LD all use it).

## Custom domain later

Settings > Pages > Custom domain, then add a file named `CNAME` at the repo root containing the domain. Push again, the URLs update by themselves.

## Edit content

Non-technical editing: Pages CMS (https://app.pagescms.org), configured in `.pages.yml`.
Editable text lives in `content/` (boutique.json, fr.json, en.json, ar.json). Each save is a commit on main and the site rebuilds in about a minute. If a build fails, the previous version stays online.
Interface labels, URL slugs and the service list stay in `content.py` (code only).

Preview locally:

```
python build.py --site-url http://localhost:8000
cd dist && python -m http.server 8000
```

## To confirm before launch

- Brand name in `BIZ["brand"]` ("Maktaba Warraqa"). It must match the Google Business Profile name exactly.
- Opening hours (Sat-Thu 7:30-21:00, Fri 14:00-21:00) in `BIZ["hours"]` and `UI[...]["hours_rows"]`.
- The phone number 0773 58 99 54 is active on WhatsApp (the WhatsApp buttons use it).
- The large format page is only accurate once the plotter is installed.
- The Google Maps link in `BIZ["maps"]`.

## After launch (SEO)

1. Add the site URL to the Google Business Profile (website field).
2. Verify the site in Google Search Console and submit `sitemap.xml`.
3. Keep name, address and phone identical everywhere (site, Google profile, social pages).
4. Ask customers for Google reviews and link the profile from the site footer once the review URL exists.

## What is optimized

- No JavaScript, inline CSS, self-hosted WOFF2 fonts, WebP logo: very small pages (about 17 to 21 KB HTML).
- One page per service per language, hreflang (fr, en, ar, x-default), canonical, sitemap with alternates.
- JSON-LD: BookStore (address, hours, phone, services catalog), Service, FAQPage, BreadcrumbList.
- Answer-first copy and visible FAQ on every page, `llms.txt` for AI search engines.
- RTL layout for Arabic, mobile call/WhatsApp/directions bar.
