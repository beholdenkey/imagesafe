// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey

package main

import (
	"context"
)

// Scan returns Malcontent scan results for a given image reference.
// Example usage: dagger call scan --ref=ghcr.io/beholdenkey/imagesafe/hurl:6.0.0
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
