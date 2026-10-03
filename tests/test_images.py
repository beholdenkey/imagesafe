"""Regression coverage for selective builds and application-version tags."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("images", Path(__file__).resolve().parents[1] / "scripts/images.py")
images = importlib.util.module_from_spec(spec)
spec.loader.exec_module(images)


class SelectionTests(unittest.TestCase):
    names = ["hurl", "opentofu", "wolfi-base"]

    def test_documentation_does_not_rebuild(self):
        self.assertEqual(images.select_images(self.names, ["README.md", "images/hurl/README.md"]), [])

    def test_image_changes_rebuild_even_if_version_tag_exists(self):
        self.assertEqual(images.select_images(self.names, ["images/hurl/apko.yaml"]), ["hurl"])

    def test_locks_trigger_build(self):
        self.assertEqual(images.select_images(self.names, ["images/opentofu/apko.lock.json"]), ["opentofu"])

    def test_source_recipe_and_other_image_changes_are_both_selected(self):
        self.assertEqual(images.select_images(self.names, ["packages/opentofu.yaml", "images/hurl/apko.yaml"]), ["hurl", "opentofu"])

    def test_shared_inputs_rebuild_every_image(self):
        for path in ["images/base/common.yaml", "images/catalog.json", ".mise/config.toml",
                     ".mise/conf.d/common.toml", "scripts/images.py", ".github/workflows/build.yaml"]:
            with self.subTest(path=path):
                self.assertEqual(images.select_images(self.names, [path]), sorted(self.names))

    def test_schedule_and_manual_runs_rebuild_every_image(self):
        self.assertEqual(images.select_images(self.names, [], force=True), sorted(self.names))

    def test_deleted_image_is_not_in_matrix(self):
        self.assertEqual(images.select_images(self.names, ["images/removed/apko.yaml"]), [])


class VersionTests(unittest.TestCase):
    def test_source_package_version_does_not_include_package_name(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(images, "ROOT", Path(directory)), patch.object(images, "recipe", return_value=("", "absent.lock.json")), patch.object(images, "catalog", return_value={"opentofu": {"package": "imagesafe-opentofu", "recipe": "packages/opentofu.yaml"}}), patch.object(images, "run", return_value="imagesafe-opentofu-1.13.1-r0"):
                self.assertEqual(images.version("opentofu"), "1.13.1")

    def test_versions_come_from_resolved_packages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "images/hurl"
            target.mkdir(parents=True)
            (target / "apko.lock.json").write_text(json.dumps({"contents": {"packages": [
                {"name": "hurl", "version": "8.0.1-r0", "architecture": "x86_64"},
                {"name": "hurl", "version": "8.0.1-r1", "architecture": "aarch64"},
            ]}}))
            with patch.object(images, "ROOT", root), patch.object(images, "recipe", return_value=("", "images/hurl/apko.lock.json")), patch.object(images, "catalog", return_value={"hurl": {"package": "hurl"}}):
                self.assertEqual(images.version("hurl"), "8.0.1")
                data = json.loads((target / "apko.lock.json").read_text())
                data["contents"]["packages"][1]["version"] = "8.0.2-r0"
                (target / "apko.lock.json").write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, "versions differ"):
                    images.version("hurl")


if __name__ == "__main__":
    unittest.main()
