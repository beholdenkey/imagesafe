package main

import "dagger/imagesafe/internal/dagger"

type Github struct{}

func (module *Github) DaggerOrganization() *Organization {
	url := "https://github.com/dagger"
	return &Organization{
		URL:          url,
		Repositories: []*dagger.GitRepository{dag.Git(url + "/dagger")},
		Members: []*Account{
			{"jane", "jane@example.com"},
			{"john", "john@example.com"},
		},
	}
}

type Organization struct {
	URL          string
	Repositories []*dagger.GitRepository
	Members      []*Account
}

type Account struct {
	Username string
	Email    string
}

func (account *Account) URL() string {
	return "https://github.com/" + account.Username
}

// note
// When the Dagger Engine extends the Dagger API schema with these types, it prefixes their names with the name of the main object:

// Github
// GithubAccount
// GithubOrganization
// This is to prevent possible naming conflicts when loading multiple modules, which is reflected in code generation (for example, when using this module in another one as a dependency).

// Here's an example of calling a Dagger Function from this module to get all member URLs:

// dagger call dagger-organization members url

// The result will be:

// https://github.com/jane
// https://github.com/john
