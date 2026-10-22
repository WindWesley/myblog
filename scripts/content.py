"""Load Markdown posts with YAML front matter as the sole article source."""
import re
from datetime import date
from pathlib import Path
import markdown
import yaml

def load_markdown(root):
    posts = []
    for path in sorted((root / 'content/posts').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        match = re.match(r'\A---\s*\n(.*?)\n---\s*\n(.*)\Z', text, re.S)
        if not match:
            raise ValueError(f'{path.name}: 缺少 YAML 头部 ---')
        meta = yaml.safe_load(match[1])
        if not isinstance(meta, dict):
            raise ValueError(f'{path.name}: 头部必须为字段映射')
        draft = meta.get('draft', False)
        if not isinstance(draft, bool):
            raise ValueError(f'{path.name}: draft 必须为 true 或 false，不加引号')
        if draft:
            continue
        for field in ('title', 'date', 'category'):
            if field not in meta or not str(meta[field]).strip():
                raise ValueError(f'{path.name}: 缺少 {field}')
        slug = str(meta.get('slug', path.stem))
        if not re.fullmatch(r'[a-z0-9-]+', slug):
            raise ValueError(f'{path.name}: 文件名或 slug 请使用英文小写、数字、连字符')
        published = str(meta['date'])
        date.fromisoformat(published)
        body = match[2]
        excerpt = str(meta.get('excerpt') or re.sub(r'[#*`>\[\]]', '', body).strip().split('\n\n')[0][:120])
        posts.append(dict(slug=slug, title=str(meta['title']), date=published,
                          category=str(meta['category']), author=str(meta.get('author', 'Wesley')),
                          excerpt=excerpt,
                          html=markdown.markdown(body, extensions=['fenced_code', 'tables', 'sane_lists'])))
    return posts
