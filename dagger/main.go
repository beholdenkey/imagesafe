// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey

package main

import (
	"context"
	"dagger/imagesafe/internal/dagger"
)

type ImageSafe struct{}

// Returns a container that echoes whatever string argument is provided
func (m *ImageSafe) ContainerEcho(stringArg string) *dagger.Container {
	return dag.Container().From("alpine:latest").WithExec([]string{"echo", stringArg})
}

// Returns lines that match a pattern in the files of the provided Directory
func (m *ImageSafe) GrepDir(ctx context.Context, directoryArg *dagger.Directory, pattern string) (string, error) {
	return dag.Container().
		From("alpine:latest").
		WithMountedDirectory("/mnt", directoryArg).
		WithWorkdir("/mnt").
		WithExec([]string{"grep", "-R", pattern, "."}).
		Stdout(ctx)
}
