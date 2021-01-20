import base64
import pprint

import prefect
from github import Github as GithubClient
from prefect import Flow, Parameter, Task, artifacts
from prefect.tasks.prefect import StartFlowRun
from prefect.client import Secret
from prefect.environments.storage import GitHub


class GenerateArtifact(Task):
    def run(self, data):
        artifact_id = artifacts.create_link(data)
        return artifact_id


with Flow("Relative Link Artifacts") as flow:
    a = StartFlowRun(
        project_name="PROJECT: Schematics",
        parameters={"input": "¡Hola, mundo!"},
        wait=True,
    )(flow_name="Orchestration Dependency A", run_name="ODEP-A")

    GenerateArtifact(task_run_name=lambda **kwargs: f"Artifact {kwargs['data']}").map(
        data=a
    )


flow.storage = GitHub(
    repo="znicholasbrown/project-artifacts",
    path="relative-link-artifacts.py",
    ref="master",
    secrets=["GITHUB_AUTH_TOKEN"],
)


flow.register(project_name="Artifacts")
