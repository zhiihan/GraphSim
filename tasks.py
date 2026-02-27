from invoke import task


@task
def clean(c):
    patterns = ["build", "**/*.pyc", "dist", "docs/build/"]
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


@task(clean)
def docs(c, serve=False):
    c.run("sphinx-apidoc -o docs/api/ --module-first --no-toc --force src/graphsim")
    if serve:
        c.run("sphinx-autobuild --open-browser docs/ docs/build/")
    else:
        c.run("sphinx-build docs/ docs/build/")
