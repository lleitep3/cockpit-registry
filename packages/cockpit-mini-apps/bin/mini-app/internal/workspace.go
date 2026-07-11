package internal

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

const (
	// MiniAppsDir é o subdiretório dentro do workspace do cockpit.
	MiniAppsDir = "mini-apps"
)

// WorkspaceRoot retorna o path raiz do workspace do cockpit.
func WorkspaceRoot() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("não foi possível obter o home dir: %w", err)
	}
	return filepath.Join(home, ".cockpit", "workspace"), nil
}

// MiniAppsRoot retorna o path da pasta de mini-apps.
func MiniAppsRoot() (string, error) {
	ws, err := WorkspaceRoot()
	if err != nil {
		return "", err
	}
	return filepath.Join(ws, MiniAppsDir), nil
}

// ProjectDir retorna o path de um mini-app específico.
func ProjectDir(name string) (string, error) {
	root, err := MiniAppsRoot()
	if err != nil {
		return "", err
	}
	return filepath.Join(root, name), nil
}

// ProjectExists verifica se um mini-app já existe no workspace.
func ProjectExists(name string) (bool, error) {
	dir, err := ProjectDir(name)
	if err != nil {
		return false, err
	}
	_, err = os.Stat(dir)
	if os.IsNotExist(err) {
		return false, nil
	}
	return err == nil, err
}

// ListProjects retorna os nomes de todos os mini-apps no workspace.
func ListProjects() ([]string, error) {
	root, err := MiniAppsRoot()
	if err != nil {
		return nil, err
	}

	entries, err := os.ReadDir(root)
	if os.IsNotExist(err) {
		return []string{}, nil
	}
	if err != nil {
		return nil, fmt.Errorf("erro ao listar workspace: %w", err)
	}

	var projects []string
	for _, e := range entries {
		if e.IsDir() && !strings.HasPrefix(e.Name(), ".") {
			projects = append(projects, e.Name())
		}
	}
	return projects, nil
}

// EnsureMiniAppsRoot garante que a pasta mini-apps existe no workspace.
func EnsureMiniAppsRoot() error {
	root, err := MiniAppsRoot()
	if err != nil {
		return err
	}
	return os.MkdirAll(root, 0o755)
}

// ValidateName valida que o nome do projeto é kebab-case válido.
func ValidateName(name string) error {
	if name == "" {
		return fmt.Errorf("nome do projeto não pode ser vazio")
	}
	for _, c := range name {
		if !((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '-') {
			return fmt.Errorf("nome '%s' inválido: use apenas letras minúsculas, números e hífens (kebab-case)", name)
		}
	}
	if strings.HasPrefix(name, "-") || strings.HasSuffix(name, "-") {
		return fmt.Errorf("nome '%s' inválido: não pode começar ou terminar com hífen", name)
	}
	return nil
}
