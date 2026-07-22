package internal

import (
	"fmt"
	"os"
	"os/exec"
)

type Runtime string

const (
	RuntimePodman Runtime = "podman"
	RuntimeDocker Runtime = "docker"
)

// DetectRuntime verifica qual container runtime está disponível.
func DetectRuntime() Runtime {
	if _, err := exec.LookPath("podman"); err == nil {
		return RuntimePodman
	}
	return RuntimeDocker
}

// ComposeUp sobe os serviços do docker-compose.
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

// ComposeDown para os serviços do docker-compose.
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

	cmd := exec.Command(args[0], args[1:]...) // #nosec G204
	cmd.Dir = projectDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	return cmd.Run()
}

// WaitHealthy aguarda o backend responder no healthcheck.
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
			sleepCmd := exec.Command("sleep", "2")
			_ = sleepCmd.Run()
		}
	}

	return fmt.Errorf("backend não respondeu após %d tentativas em %s", maxRetries, url)
}
