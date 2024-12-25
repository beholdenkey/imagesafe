// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey

package main

import (
	"context"
	"dagger/imagesafe/internal/dagger"
)

func (m *Imagesafe) Scan(ctx context.Context, ref string) (string, error) {

	return dag.Container().
		From("ghcr.io/beholdenkey/imagesafe/malcontent:1.7.1").
		WithExec([]string{
			"mal",
			"scan",
			"-i",
			ref,
		}).Stdout(ctx)
}

func (m *Imagesafe) Analyze(ctx context.Context, src *dagger.Directory) (string, error) {
	return dag.Container().
		From("ghcr.io/beholdenkey/imagesafe/malcontent:1.7.1").
		WithMountedDirectory("/mnt", src).
		WithWorkdir("/mnt").
		WithExec([]string{"mal", "analyze"}).
		Stdout(ctx)
}
