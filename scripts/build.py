# -*- coding: utf-8 -*-
import re, shutil
from pathlib import Path
from html import escape as e
from datetime import date
from content import load_markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
posts = load_markdown(ROOT)
slugs = set()
for p in posts:
    assert re.fullmatch(r'[a-z0-9-]+', p['slug']) and p['slug'] not in slugs
    slugs.add(p['slug'])
    date.fromisoformat(p['date'])
posts.sort(key=lambda p: p['date'], reverse=True)
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(exist_ok=True)
if (ROOT / 'images').exists():
    shutil.copytree(ROOT / 'images', OUT / 'images', ignore=shutil.ignore_patterns('*.md', '.DS_Store'))
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
(OUT / '.nojekyll').touch()

def page(title, body, prefix='./', description='风笺，一本关于技术、开源与时间的阅读笔记。'):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(description, quote=True)}"><title>{e(title)} · 风笺</title><link rel="stylesheet" href="{prefix}assets/style.css"></head><body><header><a class="brand" href="{prefix}index.html"><span>风</span>风笺 / FIELDNOTES</a><nav aria-label="主导航"><a href="{prefix}index.html">文章</a><a href="{prefix}archive.html">归档</a><a href="{prefix}about.html">关于</a></nav></header><main class="wrap">{body}</main><footer><span>风笺 · 记录值得重读的想法</span><span class="site-stats" id="busuanzi_container_site_pv" style="display:none">全站访问 <span id="busuanzi_value_site_pv"></span> 次</span></footer><script src="{prefix}assets/search.js" defer></script><script src="{prefix}assets/stats.js" defer></script></body></html>'''

def card(p):
    return f'''<article class="post" data-tag="{e(p['category'])}"><div class="meta">发布 {p['date']}<span class="tag">{e(p['category'])}</span></div><h2><a href="posts/{p['slug']}.html">{e(p['title'])}</a></h2><p>{e(p['excerpt'])}</p><a class="read" href="posts/{p['slug']}.html">阅读全文 ↗</a></article>'''

years = sorted({p['date'][:4] for p in posts}, reverse=True)
archive_links = ''.join(f'<a class="archive-link" href="archive.html#year-{y}"><span>{y}</span><span class="count">{sum(p["date"].startswith(y) for p in posts):02d} 篇 ↗</span></a>' for y in years)
filters = ''.join(f'<button type="button" data-category="{e(c, quote=True)}" aria-pressed="{str(c=="全部").lower()}">{e(c)}</button>' for c in ['全部']+sorted({p['category'] for p in posts}))
home = f'''<section class="hero"><div class="eyebrow">A SMALL COLLECTION OF GOOD IDEAS</div><h1>让值得读的，<br>留在时间里。</h1><p class="intro">关于代码、开源和技术演进的阅读笔记。<br>从旧文章里，发现仍然有用的新想法。</p><div class="stamp"><span>THE READING ROOM</span><strong>风 笺</strong><span>NOTES THROUGH TIME</span></div></section><div class="layout"><section aria-label="文章列表"><div class="toolbar">{filters}</div><span id="result-count" class="count" aria-live="polite">{len(posts)} 篇文章</span>{''.join(map(card,posts))}<p id="empty" class="empty" {'hidden' if posts else ''}>{'没有找到相关文章，试试其他关键词或分类。' if posts else '暂无文章，第一篇内容正在准备中。'}</p></section><aside><section><h3>搜索笔记</h3><label for="search" class="count">标题、语言或关键词</label><input id="search" type="search" placeholder="输入关键词…"></section><section><h3>关于这本笔记</h3><p>慢一点阅读，多一点思考。这里收集开源世界的关键时刻，也记录技术背后的选择。</p><a class="read" href="about.html">了解风笺 ↗</a></section><section><h3>时间档案</h3>{archive_links}</section><p class="count">文章按发布日期排列，记录每一次思考与分享。</p></aside></div>'''
(OUT / 'index.html').write_text(page('文章',home))
(OUT / 'posts').mkdir(exist_ok=True)
for p in posts:
    body = f'''<article class="article"><a class="back" href="../index.html">← 返回文章</a><div class="eyebrow" style="margin-top:32px">{e(p['category'])} / 原创文章</div><h1>{e(p['title'])}</h1><div class="meta">发布：{p['date']} · 作者：{e(p['author'])}<span class="article-stats" id="busuanzi_container_page_pv" style="display:none"> · 阅读 <span id="busuanzi_value_page_pv"></span> 次</span></div><div class="markdown-body">{p['html']}</div></article>'''
    (OUT / 'posts' / (p['slug']+'.html')).write_text(page(p['title'],body,'../',p['excerpt']))
archive='<section class="hero"><div class="eyebrow">THE ARCHIVE</div><h1>沿着时间，重新阅读。</h1><p class="intro">按年份，收藏文章与阅读的足迹。</p></section>'
if not years:
    archive += '<p class="empty">暂无文章归档。</p>'
for y in years:
    archive+=f'<section id="year-{y}"><h2 class="archive-year">{y}</h2>'+''.join(card(p) for p in posts if p['date'].startswith(y))+'</section>'
(OUT / 'archive.html').write_text(page('时间归档',archive))
(OUT / 'about.html').write_text(page('关于','''<article class="article"><div class="eyebrow">ABOUT FIELDNOTES</div><h1>读过，也留下。</h1><p>风笺是一个关于技术与开源的阅读博客。这里记录学习、实践与日常思考，让每一次积累都有迹可循。</p><h2>关于文章与日期</h2><p>文章显示作者和发布日期，并按年份整理归档。愿每一篇记录，都能成为日后重读的收获。</p><h2>持续更新</h2><p>这里关注语言设计、开发工具与工程实践。在不断变化的技术里，保留对问题本身的耐心。</p><a class="back" href="index.html">开始阅读 →</a></article>'''))
(OUT / '404.html').write_text(page('页面未找到','<article class="article"><h1>这一页，暂时空白。</h1><p>请检查链接，或使用浏览器返回上一页。</p></article>'))
print(f'Built {len(posts)} posts and 4 pages in {OUT}')
