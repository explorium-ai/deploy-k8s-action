# Deploy Helm Charts on Local or Remote K8s Cluster

This action takes care of all things needed in order to deploy Helm Charts and Other kubernetes resources on a Local K3D Cluster or a Remote K8s Cluster.
## Inputs

| Input | Type | Description | Default | Required
| ------ | ------ | ------ | ------ | ------
| install_local_cluster | Boolean | Install a local K3d Cluster | true | Yes
| local_cluster_name | String | Name of local Cluster if Chosen | mycluster | No |
| local_cluster_args | String | Args passed to the K3d Cluster | -p "8080:80@loadbalancer" -p "9443:443@loadbalancer" --api-port 6443 --servers 1 --agents 1 --verbose --k3s-node-label "node=ondemand@server:0;agent:0" --k3s-arg "--disable=traefik@server:0" | No |
| pre_commands | Multiline String | Shell Commands to run before installing Helm Charts | '' | No |
| post_commands | Multiline String | Shell Commands to run after installing Helm Charts | '' | No |
| kubeconfig | String | kubeconfig file to connect to a remote cluster. Do not set if using Local Cluster  | /home/runner/.kube/config | No |
| charts | Multiline String | The Helm Charts to deploy to the cluster | None | No |
| k3d-version | String | (Optional) Override Default k3d version | v5.4.1 | No |
| catch_chart_errors | Boolean | If to exit on unsucessfull helm instal | false | No |

## Full Example usage

```yaml
- name: Deploy K8s
  uses: explorium-ai/deploy-k8s-action@main
  with:
    install_local_cluster: true
    catch_chart_errors: true
    local_cluster_name: platform-cluster
    pre_commands: | # Note the pipe. This is a Multiline String
      kubectl create namespace test
    local_cluster_args: >- # Note the arrow. This is a One-Line String
      --api-port 6443
      --servers 1
      --agents 1
      --verbose 
    charts: >-
      sealed-secrets:
        type: helm
        repo: https://bitnami-labs.github.io/sealed-secrets
        repo_name: sealed-secrets
        chart: sealed-secrets
        version: 2.1.5 # Latest if ommited
        namespace: kube-system # Default if ommited. Created during install.
        values:
          - key: image.registry
            value: docker.io
      keda:
        type: helm
        repo: https://kedacore.github.io/charts
        repo_name: kedacore
        chart: keda
      platform:
        type: git
        repo: https://github.com/myorg/helmrepo.git
        token: ${{ secrets.GITHUB_TOKEN }} # To connect to the repository
        branch: main
        path: environments/dev/platform
        namespace: localhost      
        timeout: 10m
        values:
          - key: image.tag
            value: github
    post_commands: |
      kubectl get pods -n localhost
```
## Advanced - Workflow With Docker Build, Caching and Registry Injection

```yaml
name: Test Build and Deploy to Local Cluster

on:
  push:
    branches:
      - main

jobs:
  build_and_deploy_to_k3s:
    runs-on: ubuntu-latest
    services:
      registry:
        image: registry:2
        ports:
          - 5000:5000
        options: --name registry --hostname registry
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
        with:
          driver-opts: network=host

      - name: Build and Tag
        id: docker_build
        uses: docker/build-push-action@v2
        with:
          push: true
          file: Dockerfile
          tags: localhost:5000/${{ github.event.repository.name }}:github
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Save Local Registry Configuration to File
        run: |
          cat <<EOT >> registries.yaml
          mirrors:
            "registry:5000":
              endpoint:
                - http://registry:5000
          EOT
            
      - name: Deploy K8s
        uses: explorium-ai/deploy-k8s-action@main
        with:
          install_local_cluster: true
          local_cluster_name: platform-cluster
          pre_commands: |
            docker network connect k3d-platform-cluster registry
          local_cluster_args: >-
            --servers 1
            --agents 1
            --registry-config "registries.yaml"
          charts: >-
            platform:
              type: git
              repo: https://github.com/myorg/helmrepo.git
              token: ${{ secrets.GITHUB_TOKEN }} # To connect to the repository
              branch: main
              path: environments/dev/platform
              namespace: localhost      
              timeout: 10m
              values:
                - key: image.repository
                  value: registry:5000/${{ github.event.repository.name }}
                - key: image.tag
                  value: github
          post_commands: |
            kubectl get pods -n localhost
```            

## Remote AWS EKS Cluster

```yaml
- uses: unfor19/install-aws-cli-action@v1.0.3
  with:
    arch: amd64

- name: Login to Remote EKS
  run: |
    aws eks update-kubeconfig --region eu-west-1 --name my-cluster
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    
- name: Deploy K8s
  uses: explorium-ai/deploy-k8s-action@main
  with:
    install_local_cluster: false
    kubeconfig: /home/runner/.kube/config
```