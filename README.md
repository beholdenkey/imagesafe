# Dagger Proving Grounds

A Project to test [Dagger](https://dagger.io/) and see how it can be used to solve real-world DevOps and GitOps problems.

Does it make sense to take the time to learn Dagger and replace it with more linear build tools such as Make and Taskfile, or does it complement them and provide a way to build more complex workflows that are immutable and reproducible, regardless of the environment?

## Example: Container Image Lifecycle

- Build a container image
- sign the container image using sigstore
- Test the container image
- Tag the container image
- Push the container image to a registry
