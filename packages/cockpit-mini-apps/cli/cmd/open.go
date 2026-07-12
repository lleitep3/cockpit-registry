package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-mini-apps/internal"
)

var openCmd = &cobra.Command{
	Use:   "open <nome>",
	Short: "Abre um mini-app no browser",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		exists, err := internal.ProjectExists(name)
		if err != nil {
			return err
		}
		if !exists {
			return fmt.Errorf("mini-app '%s' não encontrado. Use 'cockpit mini-app list' para ver os disponíveis", name)
		}

		url := "http://localhost:3000"
		fmt.Printf("🌐 Abrindo %s (%s)...\n", name, url)
		openURL(url)
		return nil
	},
}
