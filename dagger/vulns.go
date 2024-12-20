// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey

package main

// dagger call scan --help

// The result will be:

// USAGE
//   dagger call scan [arguments]

// ARGUMENTS
//       --ref string                                  [required]
//       --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL   [required]

// Here's an example of calling the Dagger Function with an invalid enum argument:

// dagger call scan --ref=ghcr.io/beholdenkey/imagesafe/hurl:6.0.0 --severity=LOW

import (
	"context"
)

// Vulnerability severity levels
type Severity string

const (
	// Undetermined risk; analyze further.
	Unknown Severity = "UNKNOWN"

	// Minimal risk; routine fix.
	Low Severity = "LOW"

	// Moderate risk; timely fix.
	Medium Severity = "MEDIUM"

	// Serious risk; quick fix needed.
	High Severity = "HIGH"

	// Severe risk; immediate action.
	Critical Severity = "CRITICAL"
)

func (m *Imagesafe) Scan(ctx context.Context, ref string, severity Severity) (string, error) {
	ctr := dag.Container().From(ref)

	return dag.Container().
		From("aquasec/trivy:0.58.0").
		WithMountedFile("/mnt/ctr.tar", ctr.AsTarball()).
		WithMountedCache("/root/.cache", dag.CacheVolume("trivy-cache")).
		WithExec([]string{
			"trivy",
			"image",
			"--format=json",
			"--no-progress",
			"--exit-code=1",
			"--vuln-type=os,library",
			"--severity=" + string(severity),
			"--show-suppressed",
			"--input=/mnt/ctr.tar",
		}).Stdout(ctx)
}
