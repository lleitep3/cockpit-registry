package githubtools_test

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"

	"github.com/lleitep3/aicockpit/internal/packages"
)

func TestManifestValidates(t *testing.T) {
	t.Helper()

	repoRoot, err := filepath.Abs(filepath.Join("..", ".."))
	if err != nil {
		t.Fatalf("failed to resolve repo root: %v", err)
	}

	pkgPath := filepath.Join(repoRoot, "packages", "github-tools")
	pkg, err := packages.LoadPackage(pkgPath)
	if err != nil {
		t.Fatalf("failed to load package manifest: %v", err)
	}

	if pkg.Name != "github-tools" {
		t.Errorf("expected package name github-tools, got %s", pkg.Name)
	}

	if err := pkg.Validate(pkgPath); err != nil {
		t.Fatalf("package manifest validation failed: %v", err)
	}
}

func TestScriptIsExecutableAndSyntaxValid(t *testing.T) {
	t.Helper()

	scriptPath := filepath.Join(".", "bin", "github-tools")
	info, err := os.Stat(scriptPath)
	if err != nil {
		t.Fatalf("failed to stat script: %v", err)
	}

	if info.Mode().Perm()&0o111 == 0 {
		t.Errorf("script %s is not executable", scriptPath)
	}

	cmd := exec.Command("bash", "-n", scriptPath)
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("script has syntax errors: %v\n%s", err, string(out))
	}
}

func TestScriptHelpAndUnknownCommand(t *testing.T) {
	t.Helper()

	scriptPath := filepath.Join(".", "bin", "github-tools")

	helpCmd := exec.Command(scriptPath, "--help")
	helpOut, err := helpCmd.CombinedOutput()
	if err != nil {
		t.Fatalf("help command failed: %v\n%s", err, string(helpOut))
	}
	if !strings.Contains(string(helpOut), "cockpit github") {
		t.Errorf("help output should mention 'cockpit github', got:\n%s", string(helpOut))
	}

	badCmd := exec.Command(scriptPath, "unknown")
	badOut, err := badCmd.CombinedOutput()
	if err == nil {
		t.Fatalf("expected unknown command to fail, got:\n%s", string(badOut))
	}
	if !strings.Contains(string(badOut), "unknown command") {
		t.Errorf("expected 'unknown command' in error output, got:\n%s", string(badOut))
	}
}
