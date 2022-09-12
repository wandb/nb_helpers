import os, wandb, docker
from pathlib import Path

DOCKER_IMAGE = "lambda-meta:latest"

WANDB_API_KEY=wandb.api.api_key
GITHUB_TOKEN=os.environ["GITHUB_TOKEN"]

ENVS = {"WANDB_API_KEY":WANDB_API_KEY, 
        "GITHUB_TOKEN":GITHUB_TOKEN}

client = docker.from_env()
device_requests=[docker.types.DeviceRequest(device_ids=["0"], 
                                            capabilities=[['gpu']])]

examples_path = Path("/home/tcapelle/wandb/examples")
examples_path_in_docker = Path("/examples")
working_dir = Path('/home/examples')
volumes = {str(examples_path): {'bind': str(working_dir), 'mode': 'rw'}}

def in_docker_path(nb, examples_dir):
    return examples_dir / nb.relative_to(examples_path)

def run_one (nb, docker_image, envs, gpu=True, github_issue=True, from_local=True, pip_install=True):
    nb = in_docker_path(nb, working_dir if from_local else examples_path_in_docker)
    pip_install = "--pip-install" if pip_install else ""
    github_issue = "--github_issue --repo examples_ci --owner wandb" if github_issue else ""
    cmd = f"nb_helpers.run_nbs {nb}"+f" {pip_install}"+f" {github_issue}"
    res = client.containers.run(
        image=docker_image, 
        command=cmd, 
        environment=envs, 
        remove=True,
        volumes=volumes,
        device_requests=device_requests if gpu else None,
        )
    return res