import os
import yaml
import subprocess

dct = yaml.load(os.environ["CHARTS"],yaml.Loader)
for key in dct:
    helm_name = key
    helm_options = dct[key]
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
            "--create-namespace",
        ] 
        + 
        ([
            "--namespace={}".format(helm_options["namespace"])
        ] if ("namespace" in helm_options) else [])
        + 
        ([
            "--version={}".format(helm_options["version"])
        ] if ("version" in helm_options) else [])        
        + 
        ([
            "--set={key}={value}".format(key = x["key"], value = x["value"]) for x in helm_options["values"]
        ] if ("values" in helm_options) else [])
        +
        [
            helm_options["repo_name"]+"/"+helm_options["chart"]
        ]
    )