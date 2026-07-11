package internal

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

// Runtime representa o container runtime disponível.
type Runtime string

const (
	RuntimePodman Runtime = "podman"
	RuntimeDocker Runtime = "docker"
)

// DetectRuntime verifica qual container runtime está disponível.
// Prefere podman; usa docker como fallback.
func DetectRuntime() Runtime {
	if _, err := exec.LookPath("podman"); err == nil {
		return RuntimePodman
	}
	return RuntimeDocker
}

// ComposeUp sobe os serviços do docker-compose no diretório do projeto.
func ComposeUp(projectDir string) error {
	runtime := DetectRuntime()

	var cmd *exec.Cmd
	switch runtime {
	case RuntimePodman:
		fmt.Println("🦭 Usando podman-compose...")
		cmd = exec.Command("podman-compose", "up", "--build", "-d")
	default:
		fmt.Println("🐳 Usando docker compose...")
		cmd = exec.Command("docker", "compose", "up", "--build", "-d")
	}

	cmd.Dir = projectDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	return cmd.Run()
}

// ComposeDown para os serviços do docker-compose no diretório do projeto.
func ComposeDown(projectDir string) error {
	runtime := DetectRuntime()

	var cmd *exec.Cmd
	switch runtime {
	case RuntimePodman:
		cmd = exec.Command("podman-compose", "down")
	default:
		cmd = exec.Command("docker", "compose", "down")
	}

	cmd.Dir = projectDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	return cmd.Run()
}

// ComposeLogs exibe os logs dos serviços.
func ComposeLogs(projectDir string, follow bool, service string) error {
	runtime := DetectRuntime()

	var args []string
	switch runtime {
	case RuntimePodman:
		args = []string{"podman-compose", "logs"}
	default:
		args = []string{"docker", "compose", "logs"}
	}

	if follow {
		args = append(args, "-f")
	}
	if service != "" {
		args = append(args, service)
	}

	// #nosec G204 — args são controlados internamente
	cmd := exec.Command(args[0], args[1:]...)
	cmd.Dir = projectDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	return cmd.Run()
}

// WaitHealthy aguarda o backend responder no healthcheck com retry.
func WaitHealthy(backendPort int) error {
	url := fmt.Sprintf("http://localhost:%d/health", backendPort)
	maxRetries := 30

	for i := range maxRetries {
		cmd := exec.Command("curl", "-sf", url)
		if err := cmd.Run(); err == nil {
			return nil
		}
		if i < maxRetries-1 {
			fmt.Printf("⏳ Aguardando backend... (%d/%d)\n", i+1, maxRetries)
			// sleep 2s entre tentativas
			sleepCmd := exec.Command("sleep", "2")
			_ = sleepCmd.Run()
		}
	}

	return fmt.Errorf("backend não respondeu após %d tentativas em %s", maxRetries, url)
}

// ComposeExec executa um comando em um container do compose.
func ComposeExec(projectDir, service string, args ...string) error {
	runtime := DetectRuntime()

	var cmdArgs []string
	switch runtime {
	case RuntimePodman:
		cmdArgs = append([]string{"podman-compose", "exec", service}, args...)
	default:
		cmdArgs = append([]string{"docker", "compose", "exec", service}, args...)
	}

	// #nosec G204 — args são controlados internamente
	cmd := exec.Command(cmdArgs[0], cmdArgs[1:]...)
	cmd.Dir = projectDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	return cmd.Run()
}

// ComposeFile retorna o path do docker-compose.yml de um projeto.
func ComposeFile(projectDir string) string {
	return filepath.Join(projectDir, "docker-compose.yml")
}
