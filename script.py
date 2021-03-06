import base64
import os
import yaml
import subprocess
from git import Repo
import sys

catch_errors = (True if (os.environ["CATCH"] == "true") else False)
dct = yaml.load(os.environ["CHARTS"],yaml.Loader)
for key in dct:
    helm_name = key
    helm_options = dct[key]
    if helm_options["type"] == "helm":
        subprocess.run(
            [
                "helm", 
                "repo",
                "add",
                helm_options["repo_name"],
                helm_options["repo"]
            ]
        ,check=catch_errors,stdout=sys.stdout, stderr=subprocess.STDOUT)
        subprocess.run(
            [
                "helm", 
                "upgrade",
                "-i",
                helm_name,
                "--wait",
                "--create-namespace",
                "--dependency-update",
                "--debug"
            ] 
            + 
            ([
                "--namespace={}".format(helm_options["namespace"])
            ] if ("namespace" in helm_options) else [])
            +
            ([
                "--timeout={}".format(helm_options["timeout"])
            ] if ("timeout" in helm_options) else [])
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
        ,check=catch_errors,stdout=sys.stdout, stderr=subprocess.STDOUT)
    elif helm_options["type"] == "git":
        credentials = base64.b64encode(f"{helm_options['token']}:".encode("latin-1")).decode("latin-1")
        Repo.clone_from(
            url=helm_options["repo"],
            to_path=helm_name,
            branch=helm_options["branch"],
            single_branch=True,
            depth=1,
            c=f"http.{helm_options['repo']}/.extraheader=AUTHORIZATION: basic {credentials}"
        )
        os.chdir(helm_name)
        subprocess.run(
            [
                "helm", 
                "dependency",
                "update",
                "--debug"
            ], cwd="./"+helm_options["path"],check=True,stdout=sys.stdout, stderr=subprocess.STDOUT)
        subprocess.run(
            [
                "helm", 
                "upgrade",
                "-i",
                helm_name,
                "--wait",
                "--create-namespace",
                "--debug"
            ] 
            + 
            ([
                "--namespace={}".format(helm_options["namespace"])
            ] if ("namespace" in helm_options) else [])
            + 
            ([
                "--timeout={}".format(helm_options["timeout"])
            ] if ("timeout" in helm_options) else [])
            + 
            ([
                "--set={key}={value}".format(key = x["key"], value = x["value"]) for x in helm_options["values"]
            ] if ("values" in helm_options) else [])
            +
            [
                "./"+helm_options["path"]
            ]
        ,check=catch_errors,stdout=sys.stdout, stderr=subprocess.STDOUT)
        os.chdir(os.path.dirname(os.getcwd()))