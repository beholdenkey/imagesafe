// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey
package main

import (
	"context"
	"dagger/imagesafe/internal/dagger"
)

// Lint Dagger
func (m *Imagesafe) Lint(ctx context.Context, directoryArg *dagger.Directory) (string, error) {
	return dag.Container().
		From("golang:latest").
		WithMountedDirectory("/mnt", directoryArg).
		WithWorkdir("/mnt").
		WithExec([]string{"golangci-lint", "run"}).
		Stdout(ctx)
}
