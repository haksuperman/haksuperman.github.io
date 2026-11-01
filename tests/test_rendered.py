"""Exercise complete Hugo rendering in an isolated site, with no production edits."""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from blog import add_series, hugo, new_post, reclassify
from content_model import ContentError, read_post, write_post
from validate_build import PageLinks, validate


@unittest.skipUnless(os.environ.get("BLOG_HUGO_INTEGRATION") == "1", "전체 Hugo 동작 검사는 BLOG_HUGO_INTEGRATION=1로 실행")
class RenderedWorkflowTests(unittest.TestCase):
    def test_registration_drafts_reclassification_and_new_series(self):
        with tempfile.TemporaryDirectory(prefix="blog-render-check-") as temporary:
            root = Path(temporary)
            for name in ("layouts", "assets", "static", "i18n", "data"):
                shutil.copytree(ROOT / name, root / name)
            for name in ("hugo.yaml", "go.mod", "go.sum", "Dockerfile.verify"):
                shutil.copyfile(ROOT / name, root / name)
            config = root / "hugo.yaml"
            config.write_text(config.read_text().replace("enableGitInfo: true", "enableGitInfo: false"))
            for name in ("_index.md", "_content.gotmpl", "about/_index.md", "docs/_index.md", "series/_index.md", "posts/_index.md"):
                target = root / "content" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "content" / name, target)
            def create(slug, collection, **kwargs):
                with contextlib.redirect_stdout(io.StringIO()):
                    path = new_post(root, title=slug, slug=slug, collection=collection, **kwargs)
                metadata, body = read_post(path)
                metadata.update(date="2020-01-01T00:00:00+09:00", draft=False)
                write_post(path, metadata, body)
                return path
            create("doc", "docs", category="guide-lab")
            create("first", "series", series="kubernetes-cluster", order=10)
            create("last", "series", series="kubernetes-cluster", order=30)
            draft = create("draft", "series", series="kubernetes-cluster", order=20)
            metadata, body = read_post(draft)
            metadata["draft"] = True
            metadata["aliases"] = ["/study/sample/draft/"]
            write_post(draft, metadata, body)
            # New image and new draft must not depend on any historical inventory.
            (root / "content/posts/doc/diagram.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>')
            path = root / "content/posts/doc/index.md"
            metadata, body = read_post(path)
            metadata["aliases"] = ["/study/sample/doc/", "/series/sample/doc/"]
            write_post(path, metadata, body + "\n![diagram](diagram.svg)\n")
            hugo(root)
            self.assertEqual(validate(root)["공개 글"], 3)
            legacy = root / "public/study/sample/doc/index.html"
            self.assertEqual(PageLinks(legacy.read_text()).redirects, ["/posts/doc/"])
            original_redirect = legacy.read_text()
            legacy.unlink()
            with self.assertRaisesRegex(ContentError, "이전 주소 연결"):
                validate(root)
            legacy.write_text(original_redirect)
            self.assertFalse((root / "public/study/sample/draft/index.html").exists())
            image = root / "public/posts/doc/diagram.svg"
            original_image = image.read_bytes()
            image.unlink()
            with self.assertRaisesRegex(ContentError, "연결 대상이 없습니다"):
                validate(root)
            image.write_bytes(original_image)
            first = PageLinks((root / "public/posts/first/index.html").read_text())
            self.assertEqual(first.pager, [("next", "/posts/last/")])
            self.assertEqual(first.sidebar_open["/series/kubernetes-cluster/"], [True, True])
            self.assertEqual(first.sidebar_open["/series/oci-foundations/"], [False, False])
            initial_doc = PageLinks((root / "public/posts/doc/index.html").read_text())
            self.assertEqual(initial_doc.sidebar_open["/docs/guide-lab/"], [True, True])
            self.assertNotIn("/posts/draft/", [link for _, link in first.pager])
            with contextlib.redirect_stdout(io.StringIO()):
                reclassify(root, "doc", collection="docs", category="theory-reference")
                reclassify(root, "last", collection="series", series="oci-foundations", order=10)
                add_series(root, "new-series", "신규 시리즈", "자동 생성 확인")
                reclassify(root, "first", collection="docs", category="command-tool")
            hugo(root)
            self.assertEqual(validate(root)["시리즈"], 10)
            moved = PageLinks((root / "public/posts/last/index.html").read_text())
            self.assertEqual(moved.sidebar_open["/series/oci-foundations/"], [True, True])
            self.assertEqual(moved.sidebar_open["/series/kubernetes-cluster/"], [False, False])
            moved_doc = PageLinks((root / "public/posts/first/index.html").read_text())
            self.assertEqual(moved_doc.sidebar_open["/docs/command-tool/"], [True, True])
            self.assertTrue((root / "public/series/new-series/index.html").exists())
            theory = PageLinks((root / "public/docs/theory-reference/index.html").read_text())
            self.assertEqual(theory.lists, ["/posts/doc/"])
            with contextlib.redirect_stdout(io.StringIO()):
                reclassify(root, "doc", collection="series", series="new-series", order=20)
                reclassify(root, "first", collection="series", series="new-series", order=10)
            hugo(root)
            validate(root)
            group = PageLinks((root / "public/series/new-series/index.html").read_text())
            self.assertEqual(group.lists, ["/posts/first/", "/posts/doc/"])
            for slug in ("first", "doc"):
                article = PageLinks((root / f"public/posts/{slug}/index.html").read_text())
                self.assertEqual(article.sidebar_open["/series/new-series/"], [True, True])
            self.assertFalse((root / "public/posts/draft/index.html").exists())
            hugo(root, include_drafts=True)
            self.assertEqual(validate(root, include_drafts=True)["공개 글"], 4)
            self.assertTrue((root / "public/posts/draft/index.html").exists())
            self.assertEqual(PageLinks((root / "public/study/sample/draft/index.html").read_text()).redirects, ["/posts/draft/"])
            self.assertEqual(PageLinks((root / "public/study/sample/doc/index.html").read_text()).redirects, ["/posts/doc/"])


if __name__ == "__main__":
    unittest.main()
