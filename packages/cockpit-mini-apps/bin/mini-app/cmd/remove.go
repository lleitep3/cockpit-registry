package cmd

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-mini-apps/internal"
)

var forceRemove bool

var removeCmd = &cobra.Command{
	Use:   "remove <nome>",
	Short: "Remove um mini-app do workspace do cockpit",
	Long: `Remove um mini-app do workspace do cockpit.

ATENÇÃO: esta operação remove todos os arquivos do mini-app, incluindo os dados do banco.
Use --force para pular a confirmação.`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		exists, err := internal.ProjectExists(name)
		if err != nil {
			return err
		}
		if !exists {
			return fmt.Errorf("mini-app '%s' não encontrado", name)
		}

		projectDir, err := internal.ProjectDir(name)
		if err != nil {
			return err
		}

		// Confirmação interativa
		if !forceRemove {
			fmt.Printf("⚠️  Remover o mini-app '%s'?\n", name)
			fmt.Printf("   Caminho: %s\n", projectDir)
			fmt.Println("   ATENÇÃO: dados do banco de dados serão perdidos!")
			fmt.Print("\n   Digite o nome do projeto para confirmar: ")

			reader := bufio.NewReader(os.Stdin)
			input, err := reader.ReadString('\n')
			if err != nil {
				return fmt.Errorf("erro ao ler input: %w", err)
			}
			input = strings.TrimSpace(input)

			if input != name {
				fmt.Println("❌ Nome não confere. Operação cancelada.")
				return nil
			}
		}

		// Parar containers primeiro
		fmt.Printf("🛑 Parando containers de '%s'...\n", name)
		if err := internal.ComposeDown(projectDir); err != nil {
			fmt.Printf("⚠️  Aviso ao parar containers: %s\n", err)
		}

		// Remover pasta
		fmt.Printf("🗑️  Removendo %s...\n", projectDir)
		if err := os.RemoveAll(projectDir); err != nil {
			return fmt.Errorf("erro ao remover: %w", err)
		}

		fmt.Printf("✅ Mini-app '%s' removido.\n", name)
		return nil
	},
}

func init() {
	removeCmd.Flags().BoolVar(&forceRemove, "force", false, "Pular confirmação interativa")
}
