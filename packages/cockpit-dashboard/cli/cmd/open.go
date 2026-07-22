package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-dashboard/internal"
)

var openCmd = &cobra.Command{
	Use:   "open",
	Short: "Abre o dashboard do cockpit no browser",
	RunE: func(cmd *cobra.Command, args []string) error {
		projectDir, err := internal.ProjectDir()
		if err != nil {
			return err
		}

		exists, err := internal.ProjectExists()
		if err != nil {
			return err
		}

		if !exists {
			fmt.Println("🚀 Primeira execução: copiando dashboard para o workspace...")
			if err := internal.EnsureDashboardRoot(); err != nil {
				return err
			}
			if err := internal.CopyDashboard(projectDir); err != nil {
				_ = os.RemoveAll(projectDir)
				return fmt.Errorf("erro ao copiar dashboard: %w", err)
			}
			fmt.Println("⚙️  Criando .env...")
			if err := internal.CreateEnvFile(projectDir); err != nil {
				return fmt.Errorf("erro ao criar .env: %w", err)
			}
		}

		fmt.Printf("\n🐳 Subindo containers em %s...\n", projectDir)
		if err := internal.ComposeUp(projectDir); err != nil {
			return fmt.Errorf("erro ao subir containers: %w", err)
		}

		fmt.Println("⏳ Aguardando backend inicializar...")
		if err := internal.WaitHealthy(8000); err != nil {
			fmt.Printf("⚠️  Aviso: %s\n", err)
			fmt.Println("   O backend pode ainda estar iniciando. Tente acessar em alguns segundos.")
		}

		fmt.Println("🌐 Abrindo browser...")
		openURL("http://localhost:3000")

		fmt.Printf(`
✅ Dashboard rodando!

   Frontend:  http://localhost:3000
   API:       http://localhost:8000
   Swagger:   http://localhost:8000/docs

   Workspace: %s

   Logs:      cd %s && podman-compose logs -f
`, projectDir, projectDir)

		return nil
	},
}
