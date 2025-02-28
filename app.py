from flask import (
    Flask,
    render_template_string,
    make_response,
    redirect,
    url_for,
    request,
)
import os
import logging
import requests
from flask_caching import Cache

import sentry_sdk
from flask import Flask

sentry_sdk.init(
    dsn="https://fbf7c460ae3a45d232f2e640b0aa8a1c@o4508896598753280.ingest.de.sentry.io/4508896998457424",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

app = Flask(__name__)

# Set up cache configuration (in-memory cache for simplicity)
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # Cache timeout in seconds (5 minutes)
cache = Cache(app)


# Set the base URL for GitHub API. Update this to point to a self-hosted GitHub instance if required,
# or extract it to an environment variable for flexibility in different environments.
github_base_url = "https://api.github.com"
# Import the necessary module to access environment variables
github_api_key = os.getenv("GITHUB_API_KEY")

# HTML template for displaying gists in a user-friendly way
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Gists</title>
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .gist { margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .gist-description { font-weight: bold; }
        .gist-url { color: #0366d6; text-decoration: none; }
    </style>
</head>
<body>
    <h1>{{ message }}</h1>
    <div>
        {% if gists %}
            {% for gist in gists %}
                <div class="gist">
                    <p class="gist-description">{{ gist.get('description') or "No description available" }}</p>
                    <p>View Gist: <a class="gist-url" href="{{ gist.get('html_url') }}" target="_blank">{{ gist.get('html_url') }}</a></p>
                </div>
            {% endfor %}
        {% else %}
            <p>No gists found for this user.</p>
        {% endif %}
    </div>
    <div>
        <a href="{{ url_for('get_user_gists', user=user, page=prev_page, per_page=per_page) }}">Previous</a> |
        <a href="{{ url_for('get_user_gists', user=user, page=next_page, per_page=per_page) }}">Next</a>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    """Redirect the root endpoint to '/octocat'."""
    return redirect(url_for("get_user_gists", user="octocat"))


@cache.cached(timeout=300, query_string=True)
@app.route("/<string:user>", methods=["GET"])
def get_user_gists(user):
    """Fetch the public gists of a GitHub user with pagination support, with caching."""
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)

    url = f"{github_base_url}/users/{user}/gists"
    params = {"page": page, "per_page": per_page}
    if github_api_key:
        headers = {"Authorization": f"token {github_api_key}"}
    else:
        headers = None

    try:
        response = requests.get(url, params=params, headers=headers)

        # Check for 404 status from GitHub, indicating a nonexistent user
        if response.status_code == 404:
            message = f"User '{user}' not found."
            return render_template_with_message(message, 404, user, page, per_page)

        response.raise_for_status()  # Raise an HTTPError for other non-200 responses
        gists = response.json()

        # Handle empty list case for potentially nonexistent users
        if response.status_code == 200 and not gists:
            message = f"User '{user}' not found."  # Treat empty gists as a 404 if no gists are found
            return render_template_with_message(message, 404, user, page, per_page)

        # For the verification of Pytest and Ruff only
        # message = f"Displaying gists for '{urrrssserrr}' - Page {page}"
        message = f"Displaying gists for '{user}' - Page {page}"
        return render_template_with_message(
            message,
            200,
            user,
            page,
            per_page,
            gists,
            page - 1 if page > 1 else 1,
            page + 1,
        )

    except requests.exceptions.RequestException as req_err:
        app.logger.error(f"Request error occurred: {req_err}")
        return render_template_with_message(
            "A network error occurred while fetching gists. Please try again later.",
            503,
            user,
            page,
            per_page,
        )

    except Exception as err:
        app.logger.error(f"An unexpected error occurred: {err}")
        return render_template_with_message(
            "An internal error occurred.", 500, user, page, per_page
        )


def render_template_with_message(
    message, status, user, page, per_page, gists=[], prev_page=1, next_page=2
):
    """Helper function to render the HTML template with a specified message and status."""
    html = render_template_string(
        HTML_TEMPLATE,
        message=message,
        gists=gists,
        user=user,
        page=page,
        per_page=per_page,
        prev_page=prev_page,
        next_page=next_page,
    )
    return make_response(html, status)


# Environment check function to verify if the GitHub API key is set
def environment_check():
    # Check if the GitHub API key is not found in the environment variables
    if not os.getenv("GITHUB_API_KEY"):
        # Log a warning if the API key is missing, indicating potential rate limiting issues
        logging.warning(
            "GitHub API key secret not found, maybe subject to rate limiting"
        )


if __name__ == "__main__":
    # Call the environment check
    environment_check()
    app.run(host="0.0.0.0", port=8080)
