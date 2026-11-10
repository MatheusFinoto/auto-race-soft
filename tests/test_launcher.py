import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4


LAUNCHER = Path(__file__).resolve().parents[1] / "packaging" / "Iniciar.cmd"
WHERE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "where.exe"


@unittest.skipUnless(os.name == "nt" and WHERE.is_file(), "Launcher requer Windows")
class LauncherTest(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(prefix="Auto Race ação & [teste] ' ! ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.app = self.root / "app"
        self.app.mkdir()
        self.launcher = self.root / "Iniciar.cmd"
        shutil.copy2(LAUNCHER, self.launcher)

    def add_executable(self, name="AutoRusso.exe"):
        shutil.copy2(WHERE, self.app / name)

    def run_launcher(self, *arguments):
        command = os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe")
        argument_line = subprocess.list2cmdline(arguments)
        return subprocess.run(
            f'"{command}" /d /s /c ""{self.launcher}" {argument_line}"',
            cwd=self.root,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=30,
        )

    def executable_name(self):
        files = list(self.app.glob("*.exe"))
        self.assertEqual(len(files), 1)
        self.assertRegex(files[0].name, r"^[0-9a-f]{32}\.exe$")
        return files[0].name

    def test_each_open_renames_single_executable_and_preserves_success(self):
        self.add_executable()

        first = self.run_launcher("where.exe")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        first_name = self.executable_name()

        second = self.run_launcher("where.exe")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertNotEqual(first_name, self.executable_name())

    def test_program_failure_exit_code_is_preserved(self):
        self.add_executable()

        result = self.run_launcher(f"missing_{uuid4().hex}.exe")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.executable_name()

    def test_quoted_arguments_with_spaces_and_unicode_are_forwarded(self):
        self.add_executable()
        (self.root / "arquivo com espaços.txt").write_text("fixture", encoding="utf-8")

        result = self.run_launcher("/r", str(self.root), "arquivo com espaços.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.executable_name()

    def test_empty_app_fails_without_creating_an_executable(self):
        result = self.run_launcher("where.exe")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(list(self.app.iterdir()), [])

    def test_locked_executable_fails_without_launching_the_old_name(self):
        self.add_executable()
        with (self.app / "AutoRusso.exe").open("rb"):
            result = self.run_launcher("where.exe")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual([path.name for path in self.app.iterdir()], ["AutoRusso.exe"])
        self.assertIn("Feche a instancia atual", result.stderr)

    def test_multiple_executables_fail_without_renaming_or_launching(self):
        self.add_executable("one.exe")
        self.add_executable("two.exe")

        result = self.run_launcher("where.exe")

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(sorted(path.name for path in self.app.iterdir()), ["one.exe", "two.exe"])
        self.assertIn("exatamente um executavel", result.stderr)


if __name__ == "__main__":
    unittest.main()
