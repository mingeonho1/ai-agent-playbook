#!/usr/bin/env python3

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


INSTALLER = Path(__file__).with_name("install.py")


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        # macOS exposes its temporary directory through the /var -> /private/var
        # system symlink. Resolve that trusted test fixture prefix before testing
        # the installer's deliberate refusal of symlinked destinations.
        self.root = Path(self.temporary.name).resolve()
        self.package = self.root / "package"
        (self.package / "scripts").mkdir(parents=True)
        shutil.copy2(INSTALLER, self.package / "scripts" / "install.py")
        for runtime in ("claude", "codex"):
            (self.package / runtime / "agents").mkdir(parents=True)
            (self.package / runtime / "skills" / "news-card").mkdir(parents=True)
            (self.package / runtime / "agents" / "builder.txt").write_text(
                runtime + " agent\n", encoding="utf-8"
            )
            (self.package / runtime / "skills" / "news-card" / "SKILL.md").write_text(
                runtime + " skill\n", encoding="utf-8"
            )
            red_agents = self.package / "red-team" / runtime / "agents"
            red_agents.mkdir(parents=True)
            (red_agents / "red-team.txt").write_text(runtime + " red team\n", encoding="utf-8")
        for package, skill in (("evaluation-loop", "agent-evaluation-loop"), ("red-team", "adversarial-review")):
            skill_dir = self.package / package / "skills" / skill
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(skill + "\n", encoding="utf-8")
        hook = {
            "hooks": {
                "SessionStart": [
                    {"matcher": "compact", "hooks": [{"type": "command", "command": "remind"}]}
                ]
            }
        }
        hook_dir = self.package / "claude" / "hooks"
        hook_dir.mkdir()
        (hook_dir / "compact-reminder.json").write_text(
            json.dumps(hook), encoding="utf-8"
        )
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def run_installer(self, *arguments, environment_overrides=None):
        environment = os.environ.copy()
        environment["HOME"] = str(self.home)
        environment["CODEX_HOME"] = str(self.root / "codex-home")
        environment.pop("CLAUDE_CONFIG_DIR", None)
        environment.update(environment_overrides or {})
        return subprocess.run(
            [sys.executable, str(self.package / "scripts" / "install.py"), *arguments],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )

    def test_project_install_for_both_runtimes(self):
        claude_project = self.root / "claude-project"
        codex_project = self.root / "codex-project"
        for runtime, project in (("claude", claude_project), ("codex", codex_project)):
            result = self.run_installer(runtime, "--project", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

        self.assertEqual(
            (claude_project / ".claude/agents/builder.txt").read_text(), "claude agent\n"
        )
        self.assertTrue(claude_project.joinpath(".claude/skills/news-card/SKILL.md").is_file())
        self.assertEqual(
            (codex_project / ".codex/agents/builder.txt").read_text(), "codex agent\n"
        )
        self.assertTrue(codex_project.joinpath(".agents/skills/news-card/SKILL.md").is_file())
        self.assertTrue(codex_project.joinpath(".agents/skills/agent-evaluation-loop/SKILL.md").is_file())
        self.assertTrue(claude_project.joinpath(".claude/skills/agent-evaluation-loop/SKILL.md").is_file())
        self.assertFalse(codex_project.joinpath(".codex/agents/red-team.txt").exists())

    def test_red_team_installs_independently_for_both_runtimes(self):
        for runtime, skill_root in (("claude", ".claude"), ("codex", ".agents")):
            project = self.root / runtime
            result = self.run_installer(runtime, "--project", str(project), "--package", "red-team")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / ("." + runtime) / "agents/red-team.txt").is_file())
            self.assertTrue((project / skill_root / "skills/adversarial-review/SKILL.md").is_file())
            self.assertFalse((project / ("." + runtime) / "agents/builder.txt").exists())
            self.assertFalse((project / skill_root / "skills/agent-evaluation-loop").exists())

    def test_all_packages_reinstall_and_collision_are_preflighted(self):
        project = self.root / "all-project"
        arguments = ("codex", "--project", str(project), "--package", "all")
        for _ in range(2):
            result = self.run_installer(*arguments)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / ".codex/agents/builder.txt").is_file())
        self.assertTrue((project / ".codex/agents/red-team.txt").is_file())
        self.assertTrue((project / ".agents/skills/agent-evaluation-loop/SKILL.md").is_file())
        collision_project = self.root / "conflict-project"
        collision = collision_project / ".agents/skills/adversarial-review/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("keep existing", encoding="utf-8")
        result = self.run_installer("codex", "--project", str(collision_project), "--package", "all")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(collision.read_text(), "keep existing")
        self.assertFalse((collision_project / ".codex").exists())

    def test_red_team_only_rejects_operations_hook_without_writes(self):
        project = self.root / "invalid-project"
        result = self.run_installer("claude", "--project", str(project), "--package", "red-team", "--with-context-hook")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires the operations package", result.stderr)
        self.assertFalse(project.exists())

    def test_collision_preflight_prevents_partial_install(self):
        project = self.root / "project"
        collision = project / ".claude/skills/news-card/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("keep me\n", encoding="utf-8")

        result = self.run_installer("claude", "--project", str(project))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("collision", result.stderr)
        self.assertEqual(collision.read_text(), "keep me\n")
        self.assertFalse((project / ".claude/agents/builder.txt").exists())

    def test_context_hook_merge_preserves_settings_and_is_idempotent(self):
        project = self.root / "project"
        settings_path = project / ".claude/settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text(
            json.dumps({"theme": "dark", "hooks": {"PreToolUse": [{"keep": True}]}}),
            encoding="utf-8",
        )
        arguments = ("claude", "--project", str(project), "--with-context-hook")

        first = self.run_installer(*arguments)
        first_contents = settings_path.read_text()
        second = self.run_installer(*arguments)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(settings_path.read_text(), first_contents)
        settings = json.loads(first_contents)
        self.assertEqual(settings["theme"], "dark")
        self.assertEqual(settings["hooks"]["PreToolUse"], [{"keep": True}])
        self.assertEqual(len(settings["hooks"]["SessionStart"]), 1)

    def test_dry_run_changes_nothing(self):
        project = self.root / "project"
        result = self.run_installer(
            "claude", "--project", str(project), "--with-context-hook", "--dry-run"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would install", result.stdout)
        self.assertFalse(project.exists())

    def test_corrupt_settings_abort_before_copy(self):
        project = self.root / "project"
        settings_path = project / ".claude/settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text("{broken", encoding="utf-8")

        result = self.run_installer(
            "claude", "--project", str(project), "--with-context-hook"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot read Claude settings JSON", result.stderr)
        self.assertEqual(settings_path.read_text(), "{broken")
        self.assertFalse((project / ".claude/agents/builder.txt").exists())

    def test_symlinked_hook_is_rejected_before_copy(self):
        project = self.root / "project"
        hook_path = self.package / "claude/hooks/compact-reminder.json"
        real_hook = self.root / "outside-hook.json"
        hook_path.replace(real_hook)
        hook_path.symlink_to(real_hook)

        result = self.run_installer(
            "claude", "--project", str(project), "--with-context-hook"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink path component", result.stderr)
        self.assertFalse(project.exists())

    def test_user_codex_paths_use_isolated_environment(self):
        result = self.run_installer("codex", "--user")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "codex-home/agents/builder.txt").is_file())
        self.assertTrue((self.home / ".agents/skills/news-card/SKILL.md").is_file())

    def test_empty_codex_home_uses_default(self):
        result = self.run_installer(
            "codex", "--user", environment_overrides={"CODEX_HOME": ""}
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".codex/agents/builder.txt").is_file())

    def test_claude_config_dir_controls_user_install_and_hook(self):
        custom_root = self.root / "custom-claude"
        result = self.run_installer(
            "claude",
            "--user",
            "--with-context-hook",
            environment_overrides={"CLAUDE_CONFIG_DIR": str(custom_root)},
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((custom_root / "agents/builder.txt").is_file())
        self.assertTrue((custom_root / "skills/news-card/SKILL.md").is_file())
        self.assertTrue((custom_root / "settings.json").is_file())
        self.assertFalse((self.home / ".claude").exists())

    def test_empty_claude_config_dir_uses_default(self):
        result = self.run_installer(
            "claude", "--user", environment_overrides={"CLAUDE_CONFIG_DIR": ""}
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".claude/agents/builder.txt").is_file())


if __name__ == "__main__":
    unittest.main()
