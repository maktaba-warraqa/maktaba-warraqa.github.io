# -*- coding: utf-8 -*-
"""Site copy (FR / EN / AR).

Editable text lives in content/*.json (edited through Pages CMS, see .pages.yml).
This file loads it and keeps the fixed parts: interface labels, URL slugs, service order.
"""
import json
import re
from pathlib import Path

_DIR = Path(__file__).parent / "content"


def _load(name):
    return json.loads((_DIR / name).read_text(encoding="utf-8"))


_shop = _load("boutique.json")
_digits = re.sub(r"\D", "", _shop["telephone"])
_intl = "213" + _digits.lstrip("0") if not _digits.startswith("213") else _digits

BIZ = {
    "brand": "Maktaba Warraqa",
    "brand_ar": "مكتبة ووراقة",
    "phone": _shop["telephone"].strip(),
    "phone_e164": "+" + _intl,
    "whatsapp": _intl,
    "maps": _shop["google_maps"].strip(),
    # Google Business Profile: public profile (reviews) and optional "leave a review" link
    "gbp": (_shop.get("fiche_google") or "").strip(),
    "review": (_shop.get("lien_avis") or "").strip(),
    "street": _shop["rue"].strip(),
    "city": _shop["ville"].strip(),
    "postal": _shop["code_postal"].strip(),
    "country": "DZ",
    # opening hours: (days, opens, closes) used for JSON-LD and llms.txt
    "hours": [(list(h["jours"]), h["ouverture"], h["fermeture"]) for h in _shop["horaires"]],
}

LANGS = ("fr", "en", "ar")
LOCALE = {"fr": "fr_DZ", "en": "en_US", "ar": "ar_DZ"}
LANG_LABEL = {"fr": "Français", "en": "English", "ar": "العربية"}
LANG_SHORT = {"fr": "FR", "en": "EN", "ar": "AR"}

UI = {
    "fr": {
        "skip": "Aller au contenu",
        "home": "Accueil",
        "services": "Nos services",
        "offer": "Ce que nous proposons",
        "faq": "Questions fréquentes",
        "more": "En savoir plus",
        "others": "Autres services",
        "visit": "Venez en boutique",
        "address": "Adresse",
        "address_full": "Rue des frères Abbabsa, 05000 Batna, Algérie",
        "hours": "Horaires",
        "hours_rows": [("Samedi au jeudi", "7h30 - 21h"), ("Vendredi", "14h - 21h")],
        "phone": "Téléphone",
        "call": "Appeler",
        "wa": "WhatsApp",
        "route": "Itinéraire",
        "ask": "Demandez votre devis par téléphone ou WhatsApp.",
        "why": "Pourquoi nous choisir",
        "contact": "Contact",
        "arrow": "→",
        "brand_line": "Librairie, imprimerie et services digitaux à Batna",
        "rights": "Tous droits réservés.",
        "nf_title": "Page introuvable",
        "nf_text": "Cette page n'existe pas. Retournez à l'accueil.",
        "lang_name": "Langue",
    },
    "en": {
        "skip": "Skip to content",
        "home": "Home",
        "services": "Our services",
        "offer": "What we offer",
        "faq": "Frequently asked questions",
        "more": "Learn more",
        "others": "Other services",
        "visit": "Visit the shop",
        "address": "Address",
        "address_full": "Rue des frères Abbabsa, 05000 Batna, Algeria",
        "hours": "Opening hours",
        "hours_rows": [("Saturday to Thursday", "7:30 am - 9 pm"), ("Friday", "2 pm - 9 pm")],
        "phone": "Phone",
        "call": "Call",
        "wa": "WhatsApp",
        "route": "Directions",
        "ask": "Ask for a quote by phone or WhatsApp.",
        "why": "Why choose us",
        "contact": "Contact",
        "arrow": "→",
        "brand_line": "Bookstore, print shop and digital services in Batna",
        "rights": "All rights reserved.",
        "nf_title": "Page not found",
        "nf_text": "This page does not exist. Go back to the home page.",
        "lang_name": "Language",
    },
    "ar": {
        "skip": "انتقل إلى المحتوى",
        "home": "الرئيسية",
        "services": "خدماتنا",
        "offer": "ما نقدمه",
        "faq": "أسئلة شائعة",
        "more": "اعرف المزيد",
        "others": "خدمات أخرى",
        "visit": "زورونا في المحل",
        "address": "العنوان",
        "address_full": "شارع الإخوة عبابسة، باتنة 05000، الجزائر",
        "hours": "أوقات العمل",
        "hours_rows": [("من السبت إلى الخميس", "7:30 صباحا - 9:00 مساء"), ("الجمعة", "2:00 - 9:00 مساء")],
        "phone": "الهاتف",
        "call": "اتصل بنا",
        "wa": "واتساب",
        "route": "الاتجاهات",
        "ask": "اطلب عرض سعر عبر الهاتف أو واتساب.",
        "why": "لماذا تختارنا",
        "contact": "تواصل معنا",
        "arrow": "←",
        "brand_line": "مكتبة ومطبعة وخدمات رقمية في باتنة",
        "rights": "جميع الحقوق محفوظة.",
        "nf_title": "الصفحة غير موجودة",
        "nf_text": "هذه الصفحة غير موجودة. عد إلى الصفحة الرئيسية.",
        "lang_name": "اللغة",
    },
}

SVC_ORDER = ["print", "largeformat", "design", "reports", "school", "digital", "shopping"]

SLUGS = {
    "print": {
        "fr": "impression-photocopie-batna",
        "en": "printing-copying-batna",
        "ar": "printing-copying-batna",
    },
    "largeformat": {
        "fr": "impression-grand-format-architectes-batna",
        "en": "large-format-printing-architects-batna",
        "ar": "large-format-printing-architects-batna",
    },
    "reports": {
        "fr": "mise-en-page-memoires-rapports-batna",
        "en": "thesis-report-formatting-batna",
        "ar": "thesis-report-formatting-batna",
    },
    "school": {
        "fr": "fournitures-impression-ecoles-batna",
        "en": "school-supplies-printing-batna",
        "ar": "school-supplies-printing-batna",
    },
    "design": {
        "fr": "creation-logo-carte-visite-site-vitrine-batna",
        "en": "logo-business-card-website-design-batna",
        "ar": "logo-business-card-website-design-batna",
    },
    "digital": {
        "fr": "services-digitaux-ia-batna",
        "en": "digital-ai-services-batna",
        "ar": "digital-ai-services-batna",
    },
    "shopping": {
        "fr": "achats-en-ligne-aliexpress-batna",
        "en": "online-shopping-aliexpress-batna",
        "ar": "online-shopping-aliexpress-batna",
    },
}


_text = {lang: _load(f"{lang}.json") for lang in LANGS}

for _lang, _t in _text.items():
    UI[_lang]["address_full"] = _t["adresse_complete"]
    UI[_lang]["hours_rows"] = [(r["jours"], r["heures"]) for r in _t["horaires_affiches"]]


def _qa(rows):
    return [(r["question"], r["reponse"]) for r in rows]


HOME = {
    lang: {
        "title": t["accueil"]["title"],
        "meta": t["accueil"]["meta"],
        "kicker": t["accueil"].get("kicker") or "",
        "h1": t["accueil"]["h1"],
        "lead": t["accueil"]["lead"],
        "why": [(r["titre"], r["texte"]) for r in t["accueil"]["atouts"]],
        "faq": _qa(t["accueil"]["faq"]),
    }
    for lang, t in _text.items()
}

SVC = {
    lang: {
        key: {
            "name": s["name"],
            "card": s["card"],
            "title": s["title"],
            "h1": s["h1"],
            "meta": s["meta"],
            "summary": s["summary"],
            "items": [i for i in s["items"] if i and i.strip()],
            "faq": _qa(s["faq"]),
        }
        for key, s in ((k, t["services"][k]) for k in SVC_ORDER)
    }
    for lang, t in _text.items()
}


# ---------- blog ----------
BLOG_UI = {
    "fr": {"blog": "Blog", "blog_title": "Conseils et actualités", "blog_lead": "Nos conseils pour vos impressions, mémoires, plans et démarches en ligne à Batna.", "latest": "Derniers articles", "read": "Lire l'article", "published": "Publié le", "all_posts": "Tous les articles", "related": "Nos conseils sur ce sujet", "reviews": "Nos avis Google", "leave_review": "Laisser un avis Google", "find_us": "Retrouvez-nous sur Google"},
    "en": {"blog": "Blog", "blog_title": "Tips and news", "blog_lead": "Our tips for printing, thesis formatting, plans and online services in Batna.", "latest": "Latest articles", "read": "Read the article", "published": "Published on", "all_posts": "All articles", "related": "Our tips on this topic", "reviews": "Our Google reviews", "leave_review": "Leave a Google review", "find_us": "Find us on Google"},
    "ar": {"blog": "المدونة", "blog_title": "نصائح وأخبار", "blog_lead": "نصائحنا للطباعة والمذكرات والمخططات والخدمات الرقمية في باتنة.", "latest": "آخر المقالات", "read": "اقرأ المقال", "published": "نُشر في", "all_posts": "كل المقالات", "related": "نصائح حول هذا الموضوع", "reviews": "آراء زبائننا على Google", "leave_review": "اترك رأيك على Google", "find_us": "تجدوننا على Google"},
}
for _lang in LANGS:
    UI[_lang].update(BLOG_UI[_lang])

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _posts():
    out, seen = [], set()
    folder = _DIR / "blog"
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            raise SystemExit(f"Article illisible {f.name}: {e}")
        if p.get("brouillon"):
            continue
        slug = (p.get("slug") or "").strip().lower()
        lang = p.get("langue") or "fr"
        if not (p.get("titre") and p.get("contenu") and _SLUG.match(slug) and lang in LANGS):
            print(f"article ignoré (titre, slug, langue ou contenu manquant): {f.name}")
            continue
        if (lang, slug) in seen:
            raise SystemExit(f"Deux articles ont la même adresse: {lang}/{slug}")
        seen.add((lang, slug))
        out.append({
            "lang": lang,
            "slug": slug,
            "title": p["titre"].strip(),
            "date": str(p.get("date") or "")[:10],
            "summary": (p.get("resume") or "").strip(),
            "image": (p.get("image") or "").strip(),
            "html": p["contenu"],
            "service": p.get("service") or "",
        })
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


POSTS = _posts()
