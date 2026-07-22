package cmd

import (
	"fmt"
	"os/exec"
	"runtime"
)

func openURL(url string) {
	var cmd *exec.Cmd

	switch runtime.GOOS {
	case "linux":
		cmd = exec.Command("xdg-open", url)
	case "darwin":
		cmd = exec.Command("open", url)
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	default:
		fmt.Printf("Abra manualmente: %s\n", url)
		return
	}

	if err := cmd.Start(); err != nil {
		fmt.Printf("Não foi possível abrir o browser. Acesse: %s\n", url)
	}
}
