# SocraCode Isolated Execution Sandbox
FROM python:3.11-slim

# Create unprivileged runner user
RUN useradd -m -s /bin/bash sandbox_user

# Create workspace directory with limited permissions
WORKDIR /sandbox
RUN mkdir -p /sandbox/tmp && chown -R sandbox_user:sandbox_user /sandbox

USER sandbox_user

# Default execution entrypoint for Python snippets
ENTRYPOINT ["python", "-u", "-I"]
