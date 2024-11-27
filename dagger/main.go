// A generated module for DaggerProvingGrounds functions
//
// This module has been generated via dagger init and serves as a reference to
// basic module structure as you get started with Dagger.
//
// Two functions have been pre-created. You can modify, delete, or add to them,
// as needed. They demonstrate usage of arguments and return types using simple
// echo and grep commands. The functions can be called from the dagger CLI or
// from one of the SDKs.
//
// The first line in this comment block is a short description line and the
// rest is a long description with more detail on the module's purpose or usage,
// if appropriate. All modules should have a short description.

package main

import (
	"context"
	"dagger/dagger-proving-grounds/internal/dagger"
	"fmt"
)

type DaggerProvingGrounds struct{}

// Returns a container that echoes whatever string argument is provided
func (m *DaggerProvingGrounds) ContainerEcho(stringArg string) *dagger.Container {
	return dag.Container().From("alpine:latest").WithExec([]string{"echo", stringArg})
}

// Returns lines that match a pattern in the files of the provided Directory
func (m *DaggerProvingGrounds) GrepDir(ctx context.Context, directoryArg *dagger.Directory, pattern string) (string, error) {
	return dag.Container().
		From("alpine:latest").
		WithMountedDirectory("/mnt", directoryArg).
		WithWorkdir("/mnt").
		WithExec([]string{"grep", "-R", pattern, "."}).
		Stdout(ctx)
}

func (m *DaggerProvingGrounds) Build(ctx context.Context) error {
	result := dag.Apko().Build(dag.CurrentModule().Source().File("wolfi-base.yaml"), "latest")
	_, err := dag.Container().Import(result.File()).WithExec([]string{"cat", "/etc/apk/repositories"}).Sync(ctx)

	return err
}

func (m *DaggerProvingGrounds) Wolfi(ctx context.Context) error {
	const expected = "https://packages.wolfi.dev/os\n"

	actual, err := dag.Apko().Wolfi().Container().WithExec([]string{"cat", "/etc/apk/repositories"}).Stdout(ctx)
	if err != nil {
		return err
	}

	if actual != expected {
		return fmt.Errorf("expected %q, got %q", expected, actual)
	}

	return nil
}

func (m *DaggerProvingGrounds) Alpine(ctx context.Context) error {
	const expected = "https://dl-cdn.alpinelinux.org/alpine/edge/main\n"

	actual, err := dag.Apko().Alpine().Container().WithExec([]string{"cat", "/etc/apk/repositories"}).Stdout(ctx)
	if err != nil {
		return err
	}

	if actual != expected {
		return fmt.Errorf("expected %q, got %q", expected, actual)
	}

	return nil
}
