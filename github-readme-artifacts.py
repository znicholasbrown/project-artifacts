import base64
import pprint

import prefect
from github import Github as GithubClient
from prefect import Flow, Parameter, Task, artifacts
from prefect.client import Secret
from prefect.environments.storage import GitHub


class GetReadMe(Task):
    def run(self, ref):
        access_token = Secret("GITHUB_AUTH_TOKEN").get()
        github_client = GithubClient(access_token)

        repo = github_client.get_repo(ref)
        readme = repo.get_contents("README.md")

        b = base64.b64decode(readme.content)

        return b.decode("utf-8")


class GenerateArtifact(Task):
    def run(self, readme, ref):
        artifact_id = artifacts.create_markdown(readme)
        return artifact_id


with Flow("GitHub README Artifacts") as flow:
    repos = Parameter("repo", ["PrefectHQ/prefect", "PrefectHQ/ui", "PrefectHQ/server"])

    readme = GetReadMe(task_run_name=lambda **kwargs: f"Fetch {kwargs['ref']}").map(
        ref=repos
    )

    GenerateArtifact(task_run_name=lambda **kwargs: f"Render {kwargs['ref']}").map(
        readme=readme, ref=repos
    )


flow.storage = GitHub(
    repo="znicholasbrown/project-artifacts",
    path="github-readme-artifacts.py",
    ref="master",
    access_token_secret="GITHUB_AUTH_TOKEN",
)


flow.register(project_name="Artifacts")
