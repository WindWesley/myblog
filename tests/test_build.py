import unittest, tempfile, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class BuildTest(unittest.TestCase):
 def test_markdown_and_draft_removal(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'blog';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','dist'))
   # Keep fixture assertions independent of the real published articles.
   shutil.rmtree(root/'content/posts')
   (root/'content/posts').mkdir(parents=True)
   (root/'content/posts/my-first-post.md').write_text('---\ntitle: 草稿\ndate: 2020-01-01\ncategory: 测试\ndraft: true\n---\n不应发布')
   post=root/'content/posts/test-post.md'
   post.write_text('---\ntitle: 测试文章\ndate: 2020-05-06\ncategory: 随笔\nauthor: 测试作者\ndraft: false\n---\n\n## 标题\n\n**粗体**\n\n```python\nprint(1)\n```\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\n![图](../images/test.svg)\n')
   (root/'images/test.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
   def build():subprocess.run([sys.executable,str(root/'scripts/build.py')],check=True)
   build();html=(root/'dist/posts/test-post.html').read_text()
   for expected in ['<h2>标题</h2>','<strong>粗体</strong>','<table>','language-python','测试作者','2020-05-06','../images/test.svg']:self.assertIn(expected,html)
   self.assertNotIn('本站收录',html)
   self.assertEqual(html.count('id="busuanzi_value_page_pv"'), 1)
   self.assertEqual(html.count('id="busuanzi_value_site_pv"'), 1)
   self.assertIn('../assets/stats.js', html)
   home=(root/'dist/index.html').read_text()
   self.assertIn('id="busuanzi_value_site_pv"', home)
   self.assertNotIn('id="busuanzi_value_page_pv"', home)
   self.assertTrue((root/'dist/assets/stats.js').exists())
   self.assertTrue((root/'dist/images/test.svg').exists())
   self.assertFalse((root/'dist/posts/my-first-post.html').exists())
   self.assertFalse((root/'dist/posts/go-one.html').exists())
   post.write_text(post.read_text().replace('draft: false','draft: true'));build()
   self.assertFalse((root/'dist/posts/test-post.html').exists())
   self.assertNotIn('测试文章',(root/'dist/index.html').read_text())
   self.assertNotIn('测试文章',(root/'dist/archive.html').read_text())
   self.assertIn('暂无文章',(root/'dist/index.html').read_text())
   self.assertIn('暂无文章归档',(root/'dist/archive.html').read_text())
 def test_invalid_metadata(self):
  sys.path.insert(0,str(ROOT/'scripts'))
  from content import load_markdown
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'content/posts').mkdir(parents=True)
   p=root/'content/posts/bad.md';p.write_text('---\ntitle: test\ndate: 2020-01-01\ncategory: test\ndraft: "false"\n---\ntext')
   with self.assertRaises(ValueError):load_markdown(root)
if __name__=='__main__':unittest.main()
