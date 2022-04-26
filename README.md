# Deploy Helm Charts on Local or Remote K8s Cluster

This action takes care of all things needed in order to deploy Helm Charts and Other kubernetes resources on a Local K3D Cluster or a Remote K8s Cluster.
## Inputs

| Input | Type | Description | Default | Required
| ------ | ------ | ------ | ------ | ------
| install_local_cluster | Boolean (String) | Install a local K3d Cluster | true | Yes
| local_cluster_name | String | Name of local Cluster if Chosen | mycluster | No |
| local_cluster_args | String | Args passed to the K3d Cluster | -p "8080:80@loadbalancer" -p "9443:443@loadbalancer" --api-port 6443 --servers 1 --agents 1 --verbose --k3s-node-label "node=ondemand@server:0;agent:0" --k3s-arg "--disable=traefik@server:0"    | No |
| pre_commands | Multiline String | Shell Commands to run before installing Helm Charts | '' | No |
| post_commands | Multiline String | Shell Commands to run after installing Helm Charts | '' | No |
| kubeconfig | String | kubeconfig file to connect to a remote cluster. Do not set if using Local Cluster  | /home/runner/.kube/config | No |
| charts | Multiline String | The Helm Charts to deploy to the cluster | None | No |

## Full Example usage

```yaml
- name: Deploy K8s
  uses: explorium-ai/deploy-k8s-action@main
  with:
    install_local_cluster: true
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
