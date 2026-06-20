package modules

import (
	"bytes"
	"testing"

	"github.com/spf13/cobra"
)

func TestNewHelloCommand(t *testing.T) {
	cmd := NewHelloCommand()

	if cmd.Use != "hello" {
		t.Errorf("Expected command use 'hello', got '%s'", cmd.Use)
	}

	if cmd.Short == "" {
		t.Error("Expected command short description")
	}

	if cmd.Long == "" {
		t.Error("Expected command long description")
	}
}

func TestHelloCommandExecution(t *testing.T) {
	cmd := NewHelloCommand()

	// Capture output
	output := new(bytes.Buffer)
	cmd.SetOut(output)

	// Execute command
	err := cmd.Execute()
	if err != nil {
		t.Fatalf("Command execution failed: %v", err)
	}

	// Check output
	expected := "hello world\n"
	actual := output.String()

	if actual != expected {
		t.Errorf("Expected output '%s', got '%s'", expected, actual)
	}
}

func TestHelloCommandWithArgs(t *testing.T) {
	cmd := NewHelloCommand()

	// Capture output
	output := new(bytes.Buffer)
	cmd.SetOut(output)

	// Set args (should be ignored)
	cmd.SetArgs([]string{"arg1", "arg2"})

	// Execute command
	err := cmd.Execute()
	if err != nil {
		t.Fatalf("Command execution failed: %v", err)
	}

	// Check output (should still be "hello world")
	expected := "hello world\n"
	actual := output.String()

	if actual != expected {
		t.Errorf("Expected output '%s', got '%s'", expected, actual)
	}
}
