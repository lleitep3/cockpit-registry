package modules

import (
	"fmt"

	"github.com/spf13/cobra"
)

// NewHelloCommand creates the hello command.
func NewHelloCommand() *cobra.Command {
	return &cobra.Command{
		Use:   "hello",
		Short: "Display hello world message",
		Long:  "A simple hello-world command that displays a greeting message",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Println("hello world")
			return nil
		},
	}
}
