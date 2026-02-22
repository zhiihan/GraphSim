from invoke import task


@task
def clean(c):
    patterns = ["build", "**/*.pyc", "dist"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}")


@task
def build(c):
    c.run("uv build")


@task
def install(c):
    c.run("uv pip install dist/*.whl")


@task(clean)
def buildwheel(c):
    c.run("cibuildwheel --platform linux --output-dir dist")
