import prefect
from prefect import Flow, Task, artifacts, Parameter
from prefect.client import Secret
from prefect.environments.storage import GitHub
from github import Github as GithubClient
import base64
import pprint


class GetReadMe(Task):
    def run(self, ref):
        access_token = Secret("GITHUB_AUTH_TOKEN").get()
        github_client = GithubClient(access_token)

        repo = github_client.get_repo(ref)
        readme = repo.get_contents("README.md")

        b = base64.b64decode(readme.content)

        return b.decode("utf-8")


class GenerateArtifact(Task):
    def run(self, readme):
        artifact_id = artifacts.create_markdown(readme)
        return artifact_id


with Flow("GitHub README Artifacts") as flow:
    repo = Parameter("repo", "PrefectHQ/prefect")

    readme = GetReadMe()(ref=repo)
    GenerateArtifact()(readme=readme)


flow.storage = GitHub(
    repo="znicholasbrown/project-artifacts",
    path="github-readme-artifacts.py",
    ref="master",
    secrets=["GITHUB_AUTH_TOKEN"],
)

flow.register(project_name="Artifacts")
