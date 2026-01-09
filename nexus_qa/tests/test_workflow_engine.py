import tempfile
import unittest
from pathlib import Path

from nexus_qa.models import WorkflowStep
from nexus_qa.workflows.engine import WorkflowEngine


class WorkflowEngineExecuteStepTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = WorkflowEngine()

    def test_shell_false_does_not_execute_extra_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pwned_path = Path(tmpdir) / "pwned"
            step = WorkflowStep(name="safe", command="echo ${INPUT}")
            variables = {"INPUT": f"a; touch {pwned_path}"}

            result = self.engine.execute_step(step, variables)

            self.assertTrue(result["success"])
            self.assertFalse(pwned_path.exists())

    def test_shell_true_allows_shell_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.txt"
            step = WorkflowStep(
                name="shell",
                command=f"printf %s ${{VALUE}} > {output_path}",
                shell=True,
            )
            variables = {"VALUE": "hello world"}

            result = self.engine.execute_step(step, variables)

            self.assertTrue(result["success"])
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding="utf-8"), "hello world")


if __name__ == "__main__":
    unittest.main()
