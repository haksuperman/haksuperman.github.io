import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from blog import add_series, new_post, reclassify
from content_model import ContentError, DOC_IDS, is_published, read_post, validate_sources, write_post


class ContentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        self.data = {"docs": [{"id": key, "title": key} for key in sorted(DOC_IDS)], "series": [{"id": "first", "title": "First"}, {"id": "second", "title": "Second"}]}
        self.save_catalog()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def save_catalog(self):
        (self.root / "data/navigation.json").write_text(json.dumps(self.data))

    def create(self, slug="example", **kwargs):
        return new_post(self.root, title="한글 제목", slug=slug, **kwargs)

    def test_docs_all_four_categories(self):
        for category in DOC_IDS:
            path = self.create(category, collection="docs", category=category)
            metadata, _ = read_post(path)
            self.assertEqual(metadata["docCategory"], category)
            self.assertTrue(metadata["draft"])
        self.assertEqual(len(validate_sources(self.root)[1]), 4)

    def test_new_series_automatically_appends_after_drafts(self):
        self.create("first-post", collection="series", series="first", order=10)
        path = self.create("second-post", collection="series", series="first", order=None)
        self.assertEqual(read_post(path)[0]["seriesOrder"], 20)
        validate_sources(self.root)

    def test_reclassification_keeps_body_assets_and_path(self):
        path = self.create(collection="docs", category="guide-lab")
        image = path.parent / "diagram.png"
        image.write_bytes(b"image")
        body = read_post(path)[1]
        reclassify(self.root, "example", collection="docs", category="command-tool")
        self.assertEqual(read_post(path)[0]["docCategory"], "command-tool")
        reclassify(self.root, "example", collection="series", series="first", order=20)
        self.assertNotIn("docCategory", read_post(path)[0])
        reclassify(self.root, "example", collection="series", series="second", order=30)
        self.assertEqual(read_post(path)[0]["seriesId"], "second")
        reclassify(self.root, "example", collection="docs", category="theory-reference")
        metadata, result = read_post(path)
        self.assertNotIn("seriesId", metadata)
        self.assertNotIn("seriesOrder", metadata)
        self.assertEqual(body, result)
        self.assertEqual(image.read_bytes(), b"image")
        validate_sources(self.root)

    def test_duplicate_slug_and_order_do_not_overwrite(self):
        path = self.create(collection="series", series="first", order=10)
        original = path.read_text()
        with self.assertRaises(ContentError):
            self.create(collection="docs", category="guide-lab")
        with self.assertRaises(ContentError):
            self.create("other", collection="series", series="first", order=10)
        self.assertEqual(path.read_text(), original)
        self.assertFalse((path.parent.parent / "other").exists())

    def test_new_series_is_single_catalog_entry(self):
        add_series(self.root, "new-series", "새 시리즈", "소개")
        self.create(collection="series", series="new-series", order=10)
        validate_sources(self.root)
        self.assertEqual(len(json.loads((self.root / "data/navigation.json").read_text())["series"]), 3)

    def test_invalid_metadata_and_mixed_classification(self):
        path = self.create(collection="docs", category="guide-lab")
        original, body = read_post(path)
        invalid = [{"draft": "false"}, {"date": "not-a-date"}, {"docCategory": "invalid"}, {"docCategory": []}, {"date": "2026-99-99"}, {"seriesId": "first"}, {"collection": "other"}, {"url": "/override/"}, {"tags": "oci"}, {"title": ""}]
        for change in invalid:
            with self.subTest(change=change):
                write_post(path, {**copy.deepcopy(original), **change}, body)
                with self.assertRaises(ContentError):
                    validate_sources(self.root)

    def test_duplicate_manual_order_and_missing_series_are_rejected(self):
        first = self.create("one", collection="series", series="first", order=10)
        second = self.create("two", collection="series", series="first", order=20)
        metadata, body = read_post(second)
        metadata["seriesOrder"] = 10
        write_post(second, metadata, body)
        with self.assertRaisesRegex(ContentError, "중복"):
            validate_sources(self.root)
        metadata["seriesOrder"] = 20
        metadata["seriesId"] = "missing"
        write_post(second, metadata, body)
        with self.assertRaises(ContentError):
            validate_sources(self.root)

    def test_new_images_and_drafts_do_not_require_inventory(self):
        path = self.create(collection="series", series="first", order=10)
        (path.parent / "extra.png").write_bytes(b"image")
        self.assertEqual(len(validate_sources(self.root)[1]), 1)

    def test_publication_uses_draft_and_schedule(self):
        path = self.create(collection="docs", category="guide-lab")
        metadata, _ = read_post(path)
        metadata["date"] = "2020-01-01T00:00:00+09:00"
        self.assertFalse(is_published(metadata))
        self.assertTrue(is_published(metadata, include_drafts=True))
        metadata["draft"] = False
        self.assertTrue(is_published(metadata))
        metadata["publishDate"] = "2099-01-01T00:00:00+09:00"
        self.assertFalse(is_published(metadata))

    def test_unsafe_slug_cannot_create_outside_posts(self):
        for slug in ("../escape", "UpperCase", "with space", "_index"):
            with self.subTest(slug=slug), self.assertRaises(ContentError):
                self.create(slug, collection="docs", category="guide-lab")

    def test_duplicate_yaml_keys_rejected(self):
        path = self.create(collection="docs", category="guide-lab")
        path.write_text(path.read_text().replace("collection: docs", "collection: docs\ncollection: series"))
        with self.assertRaisesRegex(ContentError, "중복"):
            validate_sources(self.root)


if __name__ == "__main__":
    unittest.main()
