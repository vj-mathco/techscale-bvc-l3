# TechScale: Multi-stage Docker build
# Stage 1 installs dependencies. Stage 2 is the lean runtime image.
# Only the installed packages and application code should reach the final image.


# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build

# TODO: Copy the requirements file and install all dependencies.
# Install into an isolated location so they can be copied cleanly to the runtime stage.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime
# TODO: Start from a clean python:3.11-slim base.
# Copy only the installed packages from the builder stage — not the build tools or cache.
# Copy the application source, set the working directory, expose port 8000, and define the startup command.
FROM python:3.11-slim AS runtime
RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates curl gnupg \
	&& mkdir -p /etc/apt/keyrings \
	&& curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
		| gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
	&& echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
		> /etc/apt/sources.list.d/mssql-release.list \
	&& apt-get update \
	&& ACCEPT_EULA=Y apt-get install -y --no-install-recommends libgssapi-krb5-2 msodbcsql18 \
	&& apt-get purge -y --auto-remove curl gnupg \
	&& rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
