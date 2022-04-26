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
            "update",
            "-i",
            helm_name,
            "--namespace {}".format(helm_options["namespace"]) if ("namespace" in helm_options) else "",
            "--version",
            helm_options["version"],
            helm_options["name"]
        ] + 
        [
            "--set {key}={value}".format(key = x["key"], value = x["value"]) for x in helm_options["values"]
        ]
    )