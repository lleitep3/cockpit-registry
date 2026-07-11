package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-mini-apps/internal"
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "Lista todos os mini-apps no workspace do cockpit",
	RunE: func(cmd *cobra.Command, args []string) error {
		projects, err := internal.ListProjects()
		if err != nil {
			return err
		}

		if len(projects) == 0 {
			root, _ := internal.MiniAppsRoot()
			fmt.Printf("Nenhum mini-app encontrado em %s\n", root)
			fmt.Println("Crie um com: cockpit mini-app new <nome>")
			return nil
		}

		root, _ := internal.MiniAppsRoot()
		fmt.Printf("Mini-apps em %s:\n\n", root)
		for _, p := range projects {
			dir, _ := internal.ProjectDir(p)
			fmt.Printf("  📦 %s\n", p)
			fmt.Printf("     %s\n", dir)
		}
		return nil
	},
}
