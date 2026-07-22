package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-dashboard/internal"
)

var stopCmd = &cobra.Command{
	Use:   "stop",
	Short: "Para os containers do dashboard",
	RunE: func(cmd *cobra.Command, args []string) error {
		projectDir, err := internal.ProjectDir()
		if err != nil {
			return err
		}

		fmt.Println("🛑 Parando containers...")
		if err := internal.ComposeDown(projectDir); err != nil {
			return fmt.Errorf("erro ao parar containers: %w", err)
		}

		fmt.Println("✅ Dashboard parado.")
		return nil
	},
}
