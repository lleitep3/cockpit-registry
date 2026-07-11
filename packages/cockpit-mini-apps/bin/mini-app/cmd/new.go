package cmd

import (
	"fmt"
	"os"
	"time"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-mini-apps/internal"
)

var noDB bool

var newCmd = &cobra.Command{
	Use:   "new <nome>",
	Short: "Cria um novo mini-app no workspace do cockpit",
	Long: `Cria um novo mini-app completo no workspace do cockpit.

Por padrão, cria com banco de dados PostgreSQL. Use --no-db para criar sem banco.

Exemplos:
  cockpit mini-app new todo-app
  cockpit mini-app new link-shortener --no-db`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		// Gerar nome automático se vazio (não deve acontecer com ExactArgs(1))
		if name == "" {
			name = fmt.Sprintf("mini-app-%s", time.Now().Format("20060102"))
		}

		// Validar nome
		if err := internal.ValidateName(name); err != nil {
			return err
		}

		// Verificar se já existe
		exists, err := internal.ProjectExists(name)
		if err != nil {
			return err
		}
		if exists {
			return fmt.Errorf("mini-app '%s' já existe no workspace", name)
		}

		// Selecionar tipo de boilerplate
		btype := internal.BoilerplateWithDB
		if noDB {
			btype = internal.BoilerplateWithoutDB
		}

		// Criar pasta do projeto
		projectDir, err := internal.ProjectDir(name)
		if err != nil {
			return err
		}
		if err := internal.EnsureMiniAppsRoot(); err != nil {
			return err
		}

		fmt.Printf("🚀 Criando mini-app '%s'", name)
		if noDB {
			fmt.Print(" (sem banco de dados)")
		}
		fmt.Println("...")

		// Copiar boilerplate
		fmt.Println("📦 Copiando boilerplate...")
		if err := internal.CopyBoilerplate(btype, projectDir, name); err != nil {
			// Limpar se falhou
			_ = os.RemoveAll(projectDir)
			return fmt.Errorf("erro ao copiar boilerplate: %w", err)
		}

		// Criar .env
		fmt.Println("⚙️  Criando .env...")
		if err := internal.CreateEnvFile(projectDir); err != nil {
			return fmt.Errorf("erro ao criar .env: %w", err)
		}

		// Subir containers
		fmt.Printf("\n🐳 Subindo containers em %s...\n", projectDir)
		if err := internal.ComposeUp(projectDir); err != nil {
			return fmt.Errorf("erro ao subir containers: %w", err)
		}

		// Aguardar backend ficar saudável
		fmt.Println("⏳ Aguardando backend inicializar...")
		if err := internal.WaitHealthy(8000); err != nil {
			fmt.Printf("⚠️  Aviso: %s\n", err)
			fmt.Println("   O backend pode ainda estar iniciando. Tente acessar em alguns segundos.")
		}

		// Abrir browser
		fmt.Println("🌐 Abrindo browser...")
		openURL("http://localhost:3000")

		// Resumo final
		fmt.Printf(`
✅ Mini-app '%s' criado com sucesso!

   Frontend:  http://localhost:3000
   API:       http://localhost:8000
   Swagger:   http://localhost:8000/docs

   Workspace: %s

   Logs:      cd %s && podman-compose logs -f
`, name, projectDir, projectDir)

		return nil
	},
}

func init() {
	newCmd.Flags().BoolVar(&noDB, "no-db", false, "Criar mini-app sem banco de dados PostgreSQL")
}
