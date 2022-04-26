import os
import yaml
import subprocess

dct = yaml.load(os.environ["CHARTS"])
for key in dct:
    helm_name = key
    helm_options = dct[key]
    # helm upgrade -i sealed-secrets-controller --namespace kube-system --version 2.1.5 sealed-secrets/sealed-secrets --set image.registry=docker.io
    subprocess.run(
        [
            "helm", 
            "repo",
            "add",
            helm_options["repo_name"],
            helm_options["repo"]
        ]
    )    
    subprocess.run(
        [
            "helm", 
            "upgrade",
            "-i",
            helm_name,
            "--wait",
            "--namespace={}".format(helm_options["namespace"]) if ("namespace" in helm_options) else "",
            "--create-namespace",
            "--version",
            helm_options["version"],
            helm_options["repo_name"]+"/"+helm_options["chart"]
        ] 
        + 
        [
            "--set={key}={value}".format(key = x["key"], value = x["value"]) for x in helm_options["values"]
        ] if ("values" in helm_options) else []
    )