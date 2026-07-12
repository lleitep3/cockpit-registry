package internal

import (
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

// BoilerplateType define o tipo de boilerplate a ser copiado.
type BoilerplateType string

const (
	BoilerplateWithDB    BoilerplateType = "with-db"
	BoilerplateWithoutDB BoilerplateType = "without-db"
)

// BoilerplatePath retorna o path do boilerplate instalado pelo pacote cockpit.
// O cockpit instala o pacote em ~/.cockpit/packages/cockpit-mini-apps/
func BoilerplatePath(btype BoilerplateType) (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	p := filepath.Join(home, ".cockpit", "packages", "cockpit-mini-apps", "boilerplate", string(btype))
	if _, err := os.Stat(p); err != nil {
		return "", fmt.Errorf("boilerplate não encontrado em %s: verifique se o pacote cockpit-mini-apps está instalado", p)
	}
	return p, nil
}

// CopyBoilerplate copia o boilerplate para o diretório de destino,
// substituindo os placeholders pelo nome real do projeto.
func CopyBoilerplate(btype BoilerplateType, destDir, projectName string) error {
	srcDir, err := BoilerplatePath(btype)
	if err != nil {
		return err
	}

	return filepath.WalkDir(srcDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		// Path relativo ao boilerplate
		rel, err := filepath.Rel(srcDir, path)
		if err != nil {
			return err
		}

		// Substitui placeholders no nome do path
		rel = replacePlaceholders(rel, projectName)
		dest := filepath.Join(destDir, rel)

		if d.IsDir() {
			return os.MkdirAll(dest, 0o755)
		}

		return copyFileWithReplace(path, dest, projectName)
	})
}

// copyFileWithReplace copia um arquivo substituindo placeholders no conteúdo.
func copyFileWithReplace(src, dest, projectName string) error {
	// Garante que o diretório pai existe
	if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
		return err
	}

	in, err := os.Open(src) // #nosec G304
	if err != nil {
		return err
	}
	defer in.Close()

	content, err := io.ReadAll(in)
	if err != nil {
		return err
	}

	// Substitui placeholders no conteúdo do arquivo
	replaced := replacePlaceholders(string(content), projectName)

	return os.WriteFile(dest, []byte(replaced), 0o644) // #nosec G306
}

// replacePlaceholders substitui os placeholders de template pelo nome real do projeto.
func replacePlaceholders(s, projectName string) string {
	// {{PROJECT_NAME}} → todo-app
	s = strings.ReplaceAll(s, "{{PROJECT_NAME}}", projectName)
	// {{PROJECT_NAME_UPPER}} → TODO_APP (para variáveis de ambiente)
	upper := strings.ToUpper(strings.ReplaceAll(projectName, "-", "_"))
	s = strings.ReplaceAll(s, "{{PROJECT_NAME_UPPER}}", upper)
	// {{PROJECT_NAME_TITLE}} → Todo App (para títulos)
	title := toTitleCase(projectName)
	s = strings.ReplaceAll(s, "{{PROJECT_NAME_TITLE}}", title)
	return s
}

// toTitleCase converte "todo-app" em "Todo App".
func toTitleCase(s string) string {
	words := strings.Split(s, "-")
	for i, w := range words {
		if len(w) > 0 {
			words[i] = strings.ToUpper(w[:1]) + w[1:]
		}
	}
	return strings.Join(words, " ")
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
