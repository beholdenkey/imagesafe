// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2024-Present Justin Bailey

package main

import (
	"context"
	"dagger/imagesafe/internal/dagger"
	"fmt"
)

type Imagesafe struct{}

// Returns a container that echoes whatever string argument is provided
func (m *Imagesafe) ContainerEcho(stringArg string) *dagger.Container {
	return dag.Container().From("alpine:latest").WithExec([]string{"echo", stringArg})
}

// Returns lines that match a pattern in the files of the provided Directory
func (m *Imagesafe) GrepDir(ctx context.Context, directoryArg *dagger.Directory, pattern string) (string, error) {
	return dag.Container().
		From("alpine:latest").
		WithMountedDirectory("/mnt", directoryArg).
		WithWorkdir("/mnt").
		WithExec([]string{"grep", "-R", pattern, "."}).
		Stdout(ctx)
}

func (m *Imagesafe) Build(ctx context.Context) error {
	result := dag.Apko().Build(dag.CurrentModule().Source().File("../images/wolfi-base/apko.yaml"), "latest")

	_, err := dag.Container().Import(result.File()).WithExec([]string{"cat", "/etc/apk/repositories"}).Sync(ctx)

	return err
}

func (m *Imagesafe) GetUser(ctx context.Context) (string, error) {
	return dag.Container().
		From("cgr.dev/chainguard/wolfi-base:latest").
		WithExec([]string{"apk", "add", "curl"}).
		WithExec([]string{"apk", "add", "jq"}).
		WithExec([]string{"sh", "-c", "curl https://randomuser.me/api/ | jq .results[0].name"}).
		Stdout(ctx)
}

// Start and return an HTTP service
func (m *Imagesafe) HttpService() *dagger.Service {
	return dag.Container().
		From("python").
		WithWorkdir("/srv").
		WithNewFile("index.html", "Hello, world!").
		WithExposedPort(8080).
		AsService(dagger.ContainerAsServiceOpts{Args: []string{"python", "-m", "http.server", "8080"}})
}

// Send a request to an HTTP service and return the response
// dagger call http-service up
func (m *Imagesafe) Get(ctx context.Context) (string, error) {
	return dag.Container().
		From("alpine").
		WithServiceBinding("www", m.HttpService()).
		WithExec([]string{"wget", "-O-", "http://www:8080"}).
		Stdout(ctx)
}

// dagger call services up --ports 8080:80
func (m *Imagesafe) Services(ctx context.Context) (*dagger.Service, error) {

	svcA := dag.Container().From("nginx").
		WithExposedPort(80).
		AsService(dagger.ContainerAsServiceOpts{Args: []string{"sh", "-c", `nginx & while true; do curl svcb:80 && sleep 1; done`}}).
		WithHostname("svca")

	_, err := svcA.Start(ctx)
	if err != nil {
		return nil, err
	}

	svcB := dag.Container().From("nginx").
		WithExposedPort(80).
		AsService(dagger.ContainerAsServiceOpts{Args: []string{"sh", "-c", `nginx & while true; do curl svca:80 && sleep 1; done`}}).
		WithHostname("svcb")

	svcB, err = svcB.Start(ctx)
	if err != nil {
		return nil, err
	}

	return svcB, nil
}

// Send a query to a MariaDB service and return the response
// docker run --rm --detach -p 3306:3306 --name my-mariadb --env MARIADB_ROOT_PASSWORD=secret  mariadb:10.11.2
func (m *Imagesafe) UserList(
	ctx context.Context,
	// Host service
	svc *dagger.Service,
) (string, error) {
	return dag.Container().
		From("mariadb:10.11.2").
		WithServiceBinding("db", svc).
		WithExec([]string{"/usr/bin/mysql", "--user=root", "--password=secret", "--host=db", "-e", "SELECT Host, User FROM mysql.user"}).
		Stdout(ctx)
}

// Error Handling Example
// dagger call divide --a=4 --b=2
func (*Imagesafe) Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, fmt.Errorf("cannot divide by zero")
	}
	return a / b, nil
}
