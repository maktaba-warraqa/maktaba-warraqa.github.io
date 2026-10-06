#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator. Usage: python build.py --site-url https://user.github.io/repo"""
import argparse
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

from content import BIZ, HOME, LANG_LABEL, LANG_SHORT, LANGS, LOCALE, SLUGS, SVC, SVC_ORDER, UI

ROOT = Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("--site-url", default="https://example.github.io/maktaba")
ap.add_argument("--out", default="dist")
args = ap.parse_args()

SITE = args.site_url.rstrip("/")
BASE = urlparse(SITE).path.rstrip("/")
OUT = ROOT / args.out
TODAY = datetime.date.today().isoformat()
esc = html.escape


def rich(text):
    """Escape text and isolate the phone number so RTL pages do not reorder its digit groups."""
    return esc(text).replace(esc(BIZ["phone"]), f'<bdi dir="ltr">{BIZ["phone"]}</bdi>')


ARABIC_RANGE = "U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC"
LATIN_RANGE = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2212"


# ---------- paths ----------
def prefix(lang):
    return "" if lang == "fr" else f"/{lang}"


def home_path(lang):
    return f"{prefix(lang)}/"


def svc_path(lang, key):
    return f"{prefix(lang)}/{SLUGS[key][lang]}/"


def href(path):
    return BASE + path


def url(path):
    return SITE + path


def asset(path):
    return f"{BASE}/assets/{path}"


# ---------- css ----------
def font_face(family, weight, file, rng):
    return (
        f'@font-face{{font-family:"{family}";font-weight:{weight};font-display:swap;'
        f'src:url({asset("fonts/" + file)}) format("woff2");unicode-range:{rng}}}'
    )


CSS = "".join(
    [
        font_face("Barlow", 500, "barlow-500.woff2", LATIN_RANGE),
        font_face("Barlow", 600, "barlow-600.woff2", LATIN_RANGE),
        font_face("Barlow", 700, "barlow-700.woff2", LATIN_RANGE),
        font_face("Barlow Condensed", 800, "barlow-condensed-800.woff2", LATIN_RANGE),
        font_face("Cairo", 700, "cairo-arabic-700.woff2", ARABIC_RANGE),
        font_face("Cairo", 900, "cairo-arabic-900.woff2", ARABIC_RANGE),
    ]
) + """
:root{--ink:#121212;--or:#F26B1D;--am:#FDB515;--rd:#D92B1F;--mu:rgba(255,255,255,.8);--line:#e4e4e4}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:500 18px/1.6 Barlow,system-ui,sans-serif;color:var(--ink);background:#fff}
[lang=ar] body{font-family:Cairo,Barlow,system-ui,sans-serif;font-weight:700;line-height:1.8}
img{max-width:100%;height:auto}
a{color:inherit}
a:focus-visible{outline:3px solid var(--or);outline-offset:3px}
.skip{position:absolute;inset-inline-start:-9999px;top:0;background:var(--am);padding:10px 16px;z-index:20}
.skip:focus{inset-inline-start:8px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.top{background:#fff}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:88px}
.logo{display:block;line-height:0}
.logo img{height:68px;width:auto}
.tools{display:flex;align-items:center;gap:14px}
.langs{display:flex;gap:6px;margin:0;padding:0;list-style:none}
.langs a{display:block;padding:5px 11px;border-radius:20px;text-decoration:none;font-weight:700;font-size:15px;border:2px solid var(--ink);line-height:1.5}
.langs a[aria-current]{background:var(--ink);color:var(--am)}
.btn{display:inline-block;padding:12px 24px;border-radius:40px;font-weight:700;text-decoration:none;background:var(--am);color:var(--ink);border:2px solid var(--am);line-height:1.3}
.btn:hover{background:#ffc83d}
.btn.alt{background:transparent;color:#fff;border-color:var(--or)}
.btn.alt:hover{background:var(--or)}
.stripe{display:flex;height:10px}
.stripe i{display:block}
.stripe i:nth-child(1){flex:5;background:var(--or)}
.stripe i:nth-child(2){flex:2;background:var(--am)}
.stripe i:nth-child(3){flex:1;background:var(--rd)}
.hero{background:var(--ink);color:#fff;padding:48px 0 60px}
.hero .wrap{display:grid;grid-template-columns:1.5fr 1fr;gap:40px;align-items:center}
.hero.s .wrap{grid-template-columns:1fr}
h1{font:800 clamp(34px,6vw,58px)/1.04 "Barlow Condensed",Barlow,sans-serif;text-transform:uppercase;letter-spacing:.01em;margin:0 0 .4em}
h2{font:800 clamp(26px,4vw,38px)/1.1 "Barlow Condensed",Barlow,sans-serif;text-transform:uppercase;margin:0 0 .6em}
h3{font:700 22px/1.25 Barlow,sans-serif;margin:0 0 .3em}
[lang=ar] h1,[lang=ar] h2,[lang=ar] h3{font-family:Cairo,Barlow,sans-serif;font-weight:900;text-transform:none;letter-spacing:0;line-height:1.4}
[lang=ar] h1{font-size:clamp(30px,5.2vw,50px)}
.kick{color:var(--am);font:900 clamp(30px,5vw,46px)/1.3 Cairo,sans-serif;margin:0 0 .2em}
.lead{font-size:20px;color:var(--mu);max-width:64ch;margin:0}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
.note{color:var(--mu);margin:18px 0 0;font-size:16px}
.card-logo{background:#fff;border-radius:28px;padding:22px;justify-self:center;line-height:0}
.crumb ol{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:0 0 20px;font-size:15px;color:var(--mu)}
.crumb li+li::before{content:"/";margin-inline-end:8px}
.crumb a{text-decoration:none}
.crumb a:hover{text-decoration:underline}
section{padding:56px 0}
.alt-bg{background:#f4f2ee}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;list-style:none;margin:0;padding:0}
.card{position:relative;background:var(--ink);color:#fff;border-top:6px solid var(--or);border-radius:14px;padding:22px;height:100%;display:flex;flex-direction:column;gap:10px}
.card h3{margin:0;font-size:24px}
.card h3 a{color:var(--am);text-decoration:none}
.card h3 a::after{content:"";position:absolute;inset:0;border-radius:14px}
.card p{margin:0;color:var(--mu);font-size:17px}
.card .more{margin-top:auto;color:var(--or);font-weight:700}
.items{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(2,1fr);gap:0 32px}
.items li{display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-top:2px solid var(--line)}
.items li::before{content:"";flex:none;width:14px;height:14px;margin-top:.55em;background:var(--or)}
.why{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;list-style:none;margin:0;padding:0}
.why li{border-top:6px solid var(--or);padding-top:14px}
.why p{margin:0}
.faq>div{padding:18px 0;border-top:2px solid var(--line)}
.faq p{margin:0;max-width:70ch}
.visit{background:var(--ink);color:#fff}
.visit h2{color:var(--am)}
.vgrid{display:grid;grid-template-columns:1.2fr 1fr;gap:40px;align-items:start}
.vgrid dl{margin:0}
.vgrid dt{color:var(--am);font-weight:700;margin-top:14px}
.vgrid dd{margin:0}
.vgrid address{font-style:normal}
.vbtns{display:flex;flex-direction:column;gap:12px;align-items:flex-start}
footer{background:var(--ink);color:var(--mu);padding:36px 0 40px;border-top:6px solid var(--or);font-size:16px}
footer .wrap{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:32px}
footer h2{font:800 18px/1.2 "Barlow Condensed",Barlow,sans-serif;color:var(--am);margin:0 0 10px}
[lang=ar] footer h2{font-family:Cairo,Barlow,sans-serif;font-weight:900}
footer ul{list-style:none;margin:0;padding:0}
footer a{color:#fff}
footer p{margin:0 0 6px}
.copy{grid-column:1/-1;border-top:1px solid rgba(255,255,255,.18);padding-top:16px}
.bar{display:none}
@media(max-width:820px){
.hero .wrap,.vgrid,footer .wrap{grid-template-columns:1fr}
.card-logo{display:none}
.grid,.items{grid-template-columns:1fr}
.why{grid-template-columns:1fr 1fr}
.top .btn{display:none}
.top .wrap{min-height:76px}
.logo img{height:58px}
section{padding:40px 0}
.hero{padding:32px 0 44px}
body{padding-bottom:58px}
.bar{display:grid;grid-template-columns:repeat(3,1fr);position:fixed;inset-inline:0;bottom:0;background:var(--ink);border-top:3px solid var(--or);z-index:10}
.bar a{padding:14px 6px;text-align:center;color:#fff;font-weight:700;text-decoration:none}
.bar a:first-child{background:var(--am);color:var(--ink)}
}
@media(max-width:480px){.why{grid-template-columns:1fr}}
"""
CSS = re.sub(r"\n+", "\n", CSS).strip()


# ---------- helpers ----------
def tel():
    return "tel:" + BIZ["phone_e164"]


def wa():
    return "https://wa.me/" + BIZ["whatsapp"]


def buttons(lang, alt_wa=True):
    u = UI[lang]
    return (
        f'<a class="btn" href="{tel()}">{esc(u["call"])} <bdi dir="ltr">{BIZ["phone"]}</bdi></a>'
        f'<a class="btn alt" href="{wa()}" rel="noopener">{esc(u["wa"])}</a>'
    )


def other_lang_paths(page):
    """page = ('home',) or ('svc', key) -> dict lang -> path"""
    if page[0] == "home":
        return {l: home_path(l) for l in LANGS}
    return {l: svc_path(l, page[1]) for l in LANGS}


def lang_switch(lang, page):
    paths = other_lang_paths(page)
    items = []
    for l in LANGS:
        cur = ' aria-current="page"' if l == lang else ""
        items.append(
            f'<li><a href="{href(paths[l])}" lang="{l}" hreflang="{l}" aria-label="{esc(LANG_LABEL[l])}"{cur}>{LANG_SHORT[l]}</a></li>'
        )
    return f'<ul class="langs">{"".join(items)}</ul>'


def opening_ld():
    out = []
    for days, opens, closes in BIZ["hours"]:
        out.append(
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": days if len(days) > 1 else days[0],
                "opens": opens,
                "closes": closes,
            }
        )
    return out


def business_ld(lang):
    offers = []
    for key in SVC_ORDER:
        offers.append(
            {
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": SVC[lang][key]["h1"],
                    "url": url(svc_path(lang, key)),
                },
            }
        )
    return {
        "@type": "BookStore",
        "@id": SITE + "/#business",
        "name": BIZ["brand"],
        "alternateName": BIZ["brand_ar"],
        "url": url(home_path(lang)),
        "image": SITE + "/assets/img/og.jpg",
        "logo": SITE + "/assets/img/icon-512.png",
        "telephone": BIZ["phone_e164"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": BIZ["street"],
            "addressLocality": BIZ["city"],
            "postalCode": BIZ["postal"],
            "addressCountry": BIZ["country"],
        },
        "hasMap": BIZ["maps"],
        "areaServed": {"@type": "City", "name": "Batna"},
        "openingHoursSpecification": opening_ld(),
        "knowsLanguage": ["fr", "ar", "en"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": UI[lang]["services"],
            "itemListElement": offers,
        },
    }


def faq_ld(faq):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq
        ],
    }


def ld_script(graph):
    data = {"@context": "https://schema.org", "@graph": graph}
    txt = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{txt}</script>'


def head(lang, page, title, meta, graph):
    paths = other_lang_paths(page)
    own = paths[lang]
    alts = "".join(
        f'<link rel="alternate" hreflang="{l}" href="{url(paths[l])}">' for l in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{url(paths["fr"])}">'
    others = "".join(
        f'<meta property="og:locale:alternate" content="{LOCALE[l]}">' for l in LANGS if l != lang
    )
    if lang == "ar":
        pre = [("cairo-arabic-900.woff2"), ("cairo-arabic-700.woff2")]
    else:
        pre = ["barlow-condensed-800.woff2", "barlow-500.woff2"]
    preload = "".join(
        f'<link rel="preload" href="{asset("fonts/" + f)}" as="font" type="font/woff2" crossorigin>' for f in pre
    )
    return (
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title>"
        f'<meta name="description" content="{esc(meta)}">'
        '<meta name="robots" content="index,follow,max-image-preview:large">'
        '<meta name="theme-color" content="#121212">'
        '<meta name="google-site-verification" content="c1eWeyqJIzoh718gMN-DgbD9hQAGho_J9hb_zIfSAcM">'
        f'<link rel="canonical" href="{url(own)}">'
        f"{alts}"
        f'<meta property="og:type" content="website">'
        f'<meta property="og:site_name" content="{esc(BIZ["brand"])}">'
        f'<meta property="og:title" content="{esc(title)}">'
        f'<meta property="og:description" content="{esc(meta)}">'
        f'<meta property="og:url" content="{url(own)}">'
        f'<meta property="og:image" content="{SITE}/assets/img/og.jpg">'
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        f'<meta property="og:locale" content="{LOCALE[lang]}">{others}'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<link rel="icon" href="{BASE}/favicon.ico" sizes="48x48">'
        f'<link rel="icon" type="image/png" sizes="192x192" href="{asset("img/icon-192.png")}">'
        f'<link rel="apple-touch-icon" href="{asset("img/icon-180.png")}">'
        f"{preload}"
        f"<style>{CSS}</style>"
        f"{ld_script(graph)}"
    )


def header(lang, page):
    u = UI[lang]
    return (
        f'<a class="skip" href="#main">{esc(u["skip"])}</a>'
        '<header class="top"><div class="wrap">'
        f'<a class="logo" href="{href(home_path(lang))}">'
        f'<img src="{asset("img/logo-190.webp")}" srcset="{asset("img/logo-190.webp")} 1x,{asset("img/logo-380.webp")} 2x" '
        f'width="95" height="64" alt="{esc(BIZ["brand"])} - {esc(BIZ["brand_ar"])}"></a>'
        f'<div class="tools">{lang_switch(lang, page)}'
        f'<a class="btn" href="{tel()}">{esc(u["call"])}</a></div>'
        "</div></header>"
        '<div class="stripe" aria-hidden="true"><i></i><i></i><i></i></div>'
    )


def visit_section(lang):
    u = UI[lang]
    return (
        '<section class="visit" id="contact"><div class="wrap">'
        f'<h2>{esc(u["visit"])}</h2><div class="vgrid"><dl>'
        f'<dt>{esc(u["address"])}</dt><dd><address>{esc(u["address_full"])}</address></dd>'
        f'<dt>{esc(u["hours"])}</dt><dd>'
        + "".join(f"{esc(d)} : {esc(h)}<br>" for d, h in u["hours_rows"])
        + f'</dd><dt>{esc(u["phone"])}</dt><dd><a href="{tel()}"><bdi dir="ltr">{BIZ["phone"]}</bdi></a></dd></dl>'
        f'<div class="vbtns"><a class="btn" href="{tel()}">{esc(u["call"])}</a>'
        f'<a class="btn alt" href="{wa()}" rel="noopener">{esc(u["wa"])}</a>'
        f'<a class="btn alt" href="{BIZ["maps"]}" rel="noopener">{esc(u["route"])}</a></div>'
        "</div></div></section>"
    )


def footer(lang):
    u = UI[lang]
    svc_links = "".join(
        f'<li><a href="{href(svc_path(lang, k))}">{esc(SVC[lang][k]["name"])}</a></li>' for k in SVC_ORDER
    )
    hours = "".join(f"<p>{esc(d)} : {esc(h)}</p>" for d, h in u["hours_rows"])
    year = datetime.date.today().year
    return (
        "<footer><div class=\"wrap\">"
        f'<div><h2>{esc(BIZ["brand"])} · {esc(BIZ["brand_ar"])}</h2><p>{esc(u["brand_line"])}</p>'
        f'<address style="font-style:normal"><p>{esc(u["address_full"])}</p>'
        f'<p><a href="{tel()}"><bdi dir="ltr">{BIZ["phone"]}</bdi></a></p></address></div>'
        f'<div><h2>{esc(u["services"])}</h2><ul>{svc_links}</ul></div>'
        f'<div><h2>{esc(u["hours"])}</h2>{hours}</div>'
        f'<p class="copy">© {year} {esc(BIZ["brand"])}. {esc(u["rights"])}</p>'
        "</div></footer>"
        f'<nav class="bar" aria-label="{esc(u["contact"])}">'
        f'<a href="{tel()}">{esc(u["call"])}</a>'
        f'<a href="{wa()}" rel="noopener">{esc(u["wa"])}</a>'
        f'<a href="{BIZ["maps"]}" rel="noopener">{esc(u["route"])}</a></nav>'
    )


def faq_section(lang, faq, alt=False):
    u = UI[lang]
    rows = "".join(f"<div><h3>{rich(q)}</h3><p>{rich(a)}</p></div>" for q, a in faq)
    cls = ' class="alt-bg"' if alt else ""
    return f'<section{cls}><div class="wrap"><h2>{esc(u["faq"])}</h2><div class="faq">{rows}</div></div></section>'


def page(lang, pg, title, meta, graph, main):
    d = "rtl" if lang == "ar" else "ltr"
    return (
        f'<!doctype html><html lang="{lang}" dir="{d}"><head>{head(lang, pg, title, meta, graph)}</head>'
        f"<body>{header(lang, pg)}<main id=\"main\">{main}</main>{footer(lang)}</body></html>"
    )


def write(path, content):
    p = OUT / path.lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ---------- pages ----------
def build_home(lang):
    h = HOME[lang]
    u = UI[lang]
    kicker = f'<p class="kick" lang="ar">{esc(h["kicker"])}</p>' if h["kicker"] else ""
    cards = "".join(
        f'<li><div class="card"><h3><a href="{href(svc_path(lang, k))}">{esc(SVC[lang][k]["name"])}</a></h3>'
        f'<p>{esc(SVC[lang][k]["card"])}</p><span class="more" aria-hidden="true">{esc(u["more"])} {u["arrow"]}</span></div></li>'
        for k in SVC_ORDER
    )
    why = "".join(f"<li><h3>{esc(t)}</h3><p>{esc(x)}</p></li>" for t, x in h["why"])
    main = (
        '<section class="hero"><div class="wrap"><div>'
        f'{kicker}<h1>{esc(h["h1"])}</h1><p class="lead">{rich(h["lead"])}</p>'
        f'<div class="cta">{buttons(lang)}</div></div>'
        f'<div class="card-logo"><img src="{asset("img/logo-380.webp")}" width="380" height="257" alt="" loading="lazy" decoding="async"></div>'
        "</div></section>"
        f'<section><div class="wrap"><h2>{esc(u["services"])}</h2><ul class="grid">{cards}</ul></div></section>'
        f'<section class="alt-bg"><div class="wrap"><h2>{esc(u["why"])}</h2><ul class="why">{why}</ul></div></section>'
        f'{faq_section(lang, h["faq"])}'
        f"{visit_section(lang)}"
    )
    graph = [
        business_ld(lang),
        {
            "@type": "WebPage",
            "@id": url(home_path(lang)) + "#webpage",
            "url": url(home_path(lang)),
            "name": h["title"],
            "inLanguage": lang,
            "about": {"@id": SITE + "/#business"},
        },
        faq_ld(h["faq"]),
    ]
    write(home_path(lang), page(lang, ("home",), h["title"], h["meta"], graph, main))


def build_service(lang, key):
    s = SVC[lang][key]
    u = UI[lang]
    items = "".join(f"<li>{esc(i)}</li>" for i in s["items"])
    others = "".join(
        f'<li><div class="card"><h3><a href="{href(svc_path(lang, k))}">{esc(SVC[lang][k]["name"])}</a></h3>'
        f'<p>{esc(SVC[lang][k]["card"])}</p></div></li>'
        for k in SVC_ORDER
        if k != key
    )
    main = (
        '<section class="hero s"><div class="wrap"><div>'
        f'<nav class="crumb" aria-label="Breadcrumb"><ol><li><a href="{href(home_path(lang))}">{esc(u["home"])}</a></li>'
        f'<li aria-current="page">{esc(s["name"])}</li></ol></nav>'
        f'<h1>{esc(s["h1"])}</h1><p class="lead">{rich(s["summary"])}</p>'
        f'<div class="cta">{buttons(lang)}</div><p class="note">{esc(u["ask"])}</p></div></div></section>'
        f'<section><div class="wrap"><h2>{esc(u["offer"])}</h2><ul class="items">{items}</ul></div></section>'
        f'{faq_section(lang, s["faq"], alt=True)}'
        f'<section><div class="wrap"><h2>{esc(u["others"])}</h2><ul class="grid">{others}</ul></div></section>'
        f"{visit_section(lang)}"
    )
    pth = svc_path(lang, key)
    graph = [
        {
            "@type": "Service",
            "@id": url(pth) + "#service",
            "name": s["h1"],
            "description": s["summary"],
            "url": url(pth),
            "inLanguage": lang,
            "areaServed": {"@type": "City", "name": "Batna"},
            "provider": {"@type": "BookStore", "@id": SITE + "/#business", "name": BIZ["brand"], "telephone": BIZ["phone_e164"], "address": {"@type": "PostalAddress", "streetAddress": BIZ["street"], "addressLocality": BIZ["city"], "postalCode": BIZ["postal"], "addressCountry": BIZ["country"]}},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": u["home"], "item": url(home_path(lang))},
                {"@type": "ListItem", "position": 2, "name": s["name"], "item": url(pth)},
            ],
        },
        faq_ld(s["faq"]),
    ]
    write(pth, page(lang, ("svc", key), s["title"], s["meta"], graph, main))


def build_404():
    lang = "fr"
    u = UI[lang]
    main = (
        '<section class="hero s"><div class="wrap"><div>'
        f'<h1>{esc(u["nf_title"])}</h1><p class="lead">{esc(u["nf_text"])}</p>'
        f'<div class="cta"><a class="btn" href="{href(home_path(lang))}">{esc(u["home"])}</a></div></div></div></section>'
    )
    doc = (
        f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(u["nf_title"])} | {esc(BIZ["brand"])}</title><meta name="robots" content="noindex">'
        f"<style>{CSS}</style></head><body>{header(lang, ('home',))}<main id=\"main\">{main}</main>{footer(lang)}</body></html>"
    )
    write("/404.html", doc)


def build_sitemap():
    rows = []
    pages = [("home",)] + [("svc", k) for k in SVC_ORDER]
    for pg in pages:
        paths = other_lang_paths(pg)
        for l in LANGS:
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{m}" href="{url(paths[m])}"/>' for m in LANGS
            ) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{url(paths["fr"])}"/>'
            rows.append(f"<url><loc>{url(paths[l])}</loc><lastmod>{TODAY}</lastmod>{alts}</url>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
        + "".join(rows)
        + "</urlset>"
    )
    write("/sitemap.xml", xml)


def build_text_files():
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    write("/09179b15a8c42e416cc7712b095079b1.txt", "09179b15a8c42e416cc7712b095079b1")
    lines = [
        f"# {BIZ['brand']} ({BIZ['brand_ar']})",
        "",
        "> Bookstore and print shop in Batna, Algeria. Printing and photocopying, large format printing for architects, "
        "thesis and report formatting, school supplies and printing, digital and AI services, and online shopping help "
        "(AliExpress, France, Europe). Languages: French, Arabic, English.",
        "",
        "## Contact",
        f"- Address: {UI['en']['address_full']}",
        f"- Phone and WhatsApp: {BIZ['phone']} ({BIZ['phone_e164']})",
        "- Hours: Saturday to Thursday 7:30-21:00, Friday 14:00-21:00",
        f"- Map: {BIZ['maps']}",
        "",
    ]
    for lang in LANGS:
        lines.append(f"## Services ({LANG_LABEL[lang]})")
        lines.append(f"- [{UI[lang]['home']}]({url(home_path(lang))}): {HOME[lang]['h1']}")
        for k in SVC_ORDER:
            lines.append(f"- [{SVC[lang][k]['h1']}]({url(svc_path(lang, k))}): {SVC[lang][k]['card']}")
        lines.append("")
    write("/llms.txt", "\n".join(lines))


# ---------- run ----------
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
shutil.copytree(ROOT / "assets", OUT / "assets")
shutil.copy(ROOT / "assets/img/favicon.ico", OUT / "favicon.ico")
(OUT / ".nojekyll").write_text("")
if (ROOT / "CNAME").exists():
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

for lang in LANGS:
    build_home(lang)
    for key in SVC_ORDER:
        build_service(lang, key)
build_404()
build_sitemap()
build_text_files()

# ---------- checks ----------
bad = []
pages_n = 0
for f in OUT.rglob("*.html"):
    pages_n += 1
    t = f.read_text(encoding="utf-8")
    for m in re.finditer(r'(?:href|src)="([^"#?]+)"', t):
        u = m.group(1)
        if u.startswith(("http", "mailto:", "tel:", "data:")):
            continue
        if BASE and u.startswith(BASE + "/"):
            u = u[len(BASE):]
        p = OUT / u.lstrip("/")
        if p.is_dir():
            p = p / "index.html"
        if not p.exists():
            bad.append((str(f.relative_to(OUT)), m.group(1)))
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        json.loads(m.group(1).replace("<\\/", "</"))
    tt = re.search(r"<title>(.*?)</title>", t)
    md = re.search(r'<meta name="description" content="(.*?)">', t)
    if tt and len(html.unescape(tt.group(1))) > 70:
        print("long title:", f.relative_to(OUT), len(html.unescape(tt.group(1))))
    if md and len(html.unescape(md.group(1))) > 165:
        print("long description:", f.relative_to(OUT), len(html.unescape(md.group(1))))

print(f"built {pages_n} html pages -> {OUT} (site url: {SITE}, base path: '{BASE}')")
if bad:
    print("BROKEN LINKS:", bad)
    sys.exit(1)
print("links ok, JSON-LD ok")
