- [GitHub Gists Viewer](#github-gists-viewer)
  - [Key Features](#key-features)
  - [Prerequisites](#prerequisites)
  - [Optional Extras](#optional-extras)
    - [Pre-Commit Framework - Useful Git hook scripts for identifying simple issues before submission to code review](#pre-commit-framework---useful-git-hook-scripts-for-identifying-simple-issues-before-submission-to-code-review)
    - [How to avoid Github rate limiting](#how-to-avoid-github-rate-limiting)
  - [Python Dependencies](#python-dependencies)
  - [Using Docker to Run the Application](#using-docker-to-run-the-application)
    - [Multi-Stage Dockerfile](#multi-stage-dockerfile)
    - [Clone the Repository](#clone-the-repository)
    - [Explanation of the Multi-Stage Dockerfile](#explanation-of-the-multi-stage-dockerfile)
      - [Stage 1: Build and Test Stage (builder)](#stage-1-build-and-test-stage-builder)
      - [Stage 2: Production Stage](#stage-2-production-stage)
    - [Building and Running the Docker Container](#building-and-running-the-docker-container)
      - [Step 1: Build the Docker Image](#step-1-build-the-docker-image)
      - [Step 2: Run the Docker Container](#step-2-run-the-docker-container)
    - [Test Coverage using Pytest in Docker](#test-coverage-using-pytest-in-docker)
      - [Build the test stage Docker Image](#build-the-test-stage-docker-image)
      - [Benefits of Using this Multi-Stage Dockerfile](#benefits-of-using-this-multi-stage-dockerfile)
    - [Useful commands](#useful-commands)
  - [Acknowledgements](#acknowledgements)
  - [License](#license)
  - [Contact](#contact)

# GitHub Gists Viewer

This is a simple Flask web application that retrieves and displays public GitHub gists for any specified user. The application defaults to showing gists for the user `octocat`.

This project showcases basic REST API integration, pagination handling, and responsive design considerations, making it suitable for introductory-level web application development.

## Key Features

- **User-Specific Gist Display**: Shows public gists for any GitHub user, with the root URL defaulting to `octocat`.
- **Pagination**: Supports pagination to view gists page-by-page.
- **HTML Interface**: Provides a user-friendly HTML interface, displaying gist descriptions and links.
- **GitHub API Caching**: Implements in-memory caching to reduce the number of requests to the GitHub API, improving efficiency and reducing load times.

## Prerequisites

Ensure the following are installed:

- [Docker](https://www.docker.com/get-docker) - Containerisation platform

## Optional Extras

### Pre-Commit Framework - Useful Git hook scripts for identifying simple issues before submission to code review

Refer to the `.pre-commit-config.yaml` file for configuration details.

- [Pre-Commit Framework](https://pre-commit.com/) - Git hook manager
  - [ggshield](https://github.com/ggshield/ggshield) - Git secret scanner for sensitive data
  - [ruff](https://beta.ruff.rs/docs/) - Python linting and formatting tool
  - [Hadolint](https://github.com/hadolint/hadolint) - Docker linting tool
  - [trailing-whitespace-fixer](https://github.com/pre-commit/mirrors-trailing-whitespace) - Trailing whitespace fixer
  - [fix end of files](https://github.com/pre-commit/mirrors-fix-end-of-files) - End of files fixer
  - [check-merge-conflict](https://github.com/pre-commit/mirrors-check-merge-conflict) - Merge conflict checker
- Basic Pre-Commit Framework Usage

```shell
# Installs Pre-commit Framework
pre-commit install

# Uninstalls Pre-commit Framework
pre-commit uninstall

# Runs all Pre-commit checks
pre-commit run --all-files

# Updates all Pre-commit hooks to the latest versions
pre-commit autoupdate
```

### How to avoid Github rate limiting

- [Rate Limiting](https://developer.github.com/v3/#rate-limiting)

Create a `.env` file with the following contents in the root of the repository:

```shell
GITHUB_API_KEY=YOUR_GITHUB_API_KEY
```

## Python Dependencies

- [Flask](https://flask.palletsprojects.com/en/2.3.x/) - Web framework
- [Pytest](https://docs.pytest.org/en/latest/) - Testing framework
- [Requests](https://requests.readthedocs.io/en/latest/) - HTTP library
- [Werkzeug](https://werkzeug.palletsprojects.com/en/2.3.x/) - WSGI utility library
- [Flask-Caching](https://flask-caching.readthedocs.io/en/latest/) - Caching extension

## Using Docker to Run the Application

You can use Docker to containerise and run the application. This is especially helpful for deployment or if you want to ensure consistent environments.

### Multi-Stage Dockerfile

The Dockerfile provided uses a multi-stage build to ensure that testing is performed during the build process. This helps ensure that only successfully tested builds make it to the production stage, and unnecessary build dependencies are excluded from the final production image.

### Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/EqualExperts-Assignments/equal-experts-tranquil-calm-profuse-ocean-bfdd4af27d4d
cd equal-experts-tranquil-calm-profuse-ocean-bfdd4af27d4d
```

Here is the Dockerfile used:

```dockerfile
# Stage 1: Build and Test Stage
FROM python:3.9-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application source code to build stage
COPY . .

# Set the default command for testing (useful if running the builder stage manually)
CMD ["sh", "-c", "pytest -s test_app.py"]

# Run the tests during the build process to ensure all code is functioning correctly
RUN /bin/sh -c "pytest -s test_app.py"

# Stage 2: Production Stage
FROM python:3.9-slim

WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=builder /app /app

# Copy the installed dependencies from the builder stage to the production stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set environment variables
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Default command to run the application
CMD ["python", "app.py"]
```

### Explanation of the Multi-Stage Dockerfile

#### Stage 1: Build and Test Stage (builder)

- **Base Image:** Uses python:3.9-slim to create a lightweight container for building and testing.
- **Working Directory:** Sets the working directory to /app.
- **Install Dependencies:**
  - `COPY requirements.txt .` – Copies the requirements.txt file to the container.
  - `RUN pip install --no-cache-dir -r requirements.txt` – Installs all the dependencies needed for the application.
- **Copy Source Code:**
  - `COPY . .` – Copies all the application source code into the `/app` directory of the container.
- **Testing:**
  - `CMD ["sh", "-c", "pytest -s test_app.py"]` – Sets a default command for testing, which can be run manually for development debugging   purposes.
  - `RUN /bin/sh -c "pytest -s test_app.py"` – Executes the tests during the build process. If any tests fail, the build proces stops, ensuring that the resulting image is stable and tested.

#### Stage 2: Production Stage

- **Base Image:** Uses `python:3.9-slim` for the production stage to keep the container small and optimised.
- **Working Directory:** Sets `/app` as the working directory.
- **Copy Artifacts:**
  - `COPY --from=builder /app /app` – Copies the application files and dependencies from the builder stage to the production image.
- **Copy Dependencies:**
  - `COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages` – Copies the installed Python packages from the builder stage to the production stage.
  - `COPY --from=builder /usr/local/bin /usr/local/bin` – Copies any executables installed by pip (such as flask, gunicorn, etc.) into the production container.
- **Environment Variables:**
  - `ENV FLASK_ENV=production` – Sets the environment to production.
- **Expose Port:**
  - `EXPOSE 8080` – Opens port 8080 for external access to the Flask application.
- **Run the Application:**
  - `CMD ["python", "app.py"]` – Defines the default command to run the application.

### Building and Running the Docker Container

To build and run this Docker container, follow these steps:

#### Step 1: Build the Docker Image

Run the following command from the project directory:

```shell
docker build -t octogist .
```

During the build process, the tests will be executed. If all tests pass, the final production image will be created.

#### Step 2: Run the Docker Container

Run the container using a Github API Key to avoid rate limiting:

```shell
docker run -e GITHUB_API_KEY=<your_github_api_key> -p 8080:8080 octogist
```

Run the container without specifying a Github API Key:

```shell
docker run -p 8080:8080 octogist
```

The application will now be accessible at [http://localhost:8080](http://localhost:8080)

### Test Coverage using Pytest in Docker

The application has basic test coverage implemented using `pytest`. Run the tests using `Docker` by running only the first stage of the multi-stage Dockerfile:

#### Build the test stage Docker Image

Every code change will require a rebuild of the test stage Docker image.

```shell
docker build --target builder -t builder-stage .
```

#### Benefits of Using this Multi-Stage Dockerfile

**Automated Testing:** By running the tests during the build stage, the Docker image ensures that only tested code makes it to production.  This greatly reduces the risk of deploying a broken version of the application.

**Separation of Build and Production:** The build and testing process is separated from the production environment, which keeps the production image smaller and more secure by excluding unnecessary build dependencies.

**Environment-Specific Logic:** The use of environment variables `(FLASK_ENV)` allows you to adjust the behavior of the container depending on whether it's being run in development or production. For example, by modifying the CMD in the production stage, you could conditionally run tests only in development.

### Useful commands

- Stops the Docker container, deletes the Docker container and deletes the Docker image.

```shell
docker stop $(docker ps -q --filter "ancestor=octogist") && docker rm $(docker ps -aq --filter "ancestor=octogist") && docker rmi octogist
```

- Builds the Docker container, tags the Docker container and runs the Docker container on port 8080.

```shell
docker build . --file Dockerfile --tag octogist && docker run -e GITHUB_API_KEY=<your_github_api_key> -p 8080:8080 octogist
```

## Acknowledgements

- [GitHub API Documentation](https://docs.github.com/en/rest/gists)
- [GitHub Gist Viewer](https://github.com/yourusername/github-gists-viewer)
- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [pytest](https://docs.pytest.org/en/latest/)
- [Docker](https://www.docker.com/)

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

## Contact

For any questions or feedback, please contact [Equal Experts](https://www.equalexperts.com/contact-us/south-africa/).
