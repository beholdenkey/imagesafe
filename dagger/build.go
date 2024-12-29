// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey

package main

import (
	"context"
)

// Builds a Container Image from an Apko file
func (m *Imagesafe) buildImage(ctx context.Context, file string, version string) (string, error) {
	return dag.Container().
		From("cgr.dev/chainguard/apko:latest").
		WithExec([]string{"apko", "build", "/mnt/apko.yaml", version}).
		Stdout(ctx)
}
