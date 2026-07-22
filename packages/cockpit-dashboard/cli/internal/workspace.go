package internal

import (
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
)

const projectName = "cockpit-dashboard"

// WorkspaceRoot retorna o path raiz do workspace do cockpit.
func WorkspaceRoot() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("não foi possível obter o home dir: %w", err)
	}
	return filepath.Join(home, ".cockpit", "workspace"), nil
}

// ProjectDir retorna o path do dashboard no workspace.
func ProjectDir() (string, error) {
	ws, err := WorkspaceRoot()
	if err != nil {
		return "", err
	}
	return filepath.Join(ws, projectName), nil
}

// ProjectExists verifica se o dashboard já existe no workspace.
func ProjectExists() (bool, error) {
	dir, err := ProjectDir()
	if err != nil {
		return false, err
	}
	_, err = os.Stat(dir)
	if os.IsNotExist(err) {
		return false, nil
	}
	return err == nil, err
}

// EnsureDashboardRoot garante que a pasta do dashboard existe.
func EnsureDashboardRoot() error {
	dir, err := ProjectDir()
	if err != nil {
		return err
	}
	return os.MkdirAll(dir, 0o755)
}

// PackageDir retorna o path do pacote instalado no cockpit.
func PackageDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".cockpit", "packages", projectName), nil
}

// CopyDashboard copia os arquivos do pacote para o workspace.
func CopyDashboard(destDir string) error {
	srcDir, err := PackageDir()
	if err != nil {
		return err
	}
	if _, err := os.Stat(srcDir); err != nil {
		return fmt.Errorf("pacote não encontrado em %s: verifique se cockpit-dashboard está instalado", srcDir)
	}

	return filepath.WalkDir(srcDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		rel, err := filepath.Rel(srcDir, path)
		if err != nil {
			return err
		}

		// Não copia o próprio binário nem a pasta bin
		if rel == "bin" || rel == "bin/dashboard" || filepath.HasPrefix(rel, "bin/") {
			return nil
		}

		dest := filepath.Join(destDir, rel)

		if d.IsDir() {
			return os.MkdirAll(dest, 0o755)
		}

		return copyFile(path, dest)
	})
}

func copyFile(src, dest string) error {
	if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
		return err
	}

	in, err := os.Open(src) // #nosec G304
	if err != nil {
		return err
	}
	defer in.Close()

	out, err := os.Create(dest)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, in)
	return err
}

// CreateEnvFile cria o arquivo .env a partir do .env.example.
func CreateEnvFile(projectDir string) error {
	example := filepath.Join(projectDir, ".env.example")
	envFile := filepath.Join(projectDir, ".env")

	content, err := os.ReadFile(example) // #nosec G304
	if err != nil {
		return fmt.Errorf("não foi possível ler .env.example: %w", err)
	}

	return os.WriteFile(envFile, content, 0o600) // #nosec G306
}
