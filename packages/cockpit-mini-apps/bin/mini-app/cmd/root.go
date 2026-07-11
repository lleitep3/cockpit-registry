package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "mini-app",
	Short: "Gerencia mini-apps no workspace do cockpit",
	Long: `cockpit mini-app — cria e gerencia mini-apps completos (SvelteKit + FastAPI + PostgreSQL)
no workspace do cockpit (~/.cockpit/workspace/mini-apps/).

Exemplos:
  cockpit mini-app new todo-app          # cria com banco de dados
  cockpit mini-app new todo-app --no-db  # cria sem banco de dados
  cockpit mini-app list                  # lista mini-apps criados
  cockpit mini-app open todo-app         # abre no browser
  cockpit mini-app remove todo-app       # remove o mini-app`,
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddCommand(newCmd)
	rootCmd.AddCommand(listCmd)
	rootCmd.AddCommand(openCmd)
	rootCmd.AddCommand(removeCmd)
}
