package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/lleitep3/cockpit-dashboard/internal"
)

var followLogs bool
var logsCmd = &cobra.Command{
	Use:   "logs [serviço]",
	Short: "Mostra os logs do dashboard",
	Args:  cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		projectDir, err := internal.ProjectDir()
		if err != nil {
			return err
		}

		service := ""
		if len(args) > 0 {
			service = args[0]
		}

		fmt.Printf("📋 Logs do dashboard (%s)...\n", projectDir)
		return internal.ComposeLogs(projectDir, followLogs, service)
	},
}

func init() {
	logsCmd.Flags().BoolVarP(&followLogs, "follow", "f", false, "Seguir logs em tempo real")
}
