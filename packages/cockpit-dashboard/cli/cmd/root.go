package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "dashboard",
	Short: "Dashboard visual do AICockpit",
	Long: `cockpit dashboard — abre um mini-app visual com o estado atual do AICockpit.

Exemplos:
  cockpit dashboard open   # abre o dashboard no browser
  cockpit dashboard stop   # para os containers
  cockpit dashboard logs   # mostra os logs`,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddCommand(openCmd)
	rootCmd.AddCommand(stopCmd)
	rootCmd.AddCommand(logsCmd)
}
