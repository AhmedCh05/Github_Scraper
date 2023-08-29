import os
from flask import Flask, jsonify, abort
from github_scraper import scrape_user_info, scrape_user_repos

myFlaskApp = Flask(__name__)


# Gets the user information from GitHub.
@myFlaskApp.route("/users/<username>", methods=["GET"])
def get_user_info(username):
    user_info = scrape_user_info(username)
    if not user_info:
        abort(404, f"User '{username}' not found on GitHub.")
    # Process the data if needed
    return jsonify(user_info)


# Gets the user repository from GitHub.
@myFlaskApp.route("/users/<username>/repos", methods=["GET"])
def get_user_repos(username):
    user_repos = scrape_user_repos(username)
    # print(user_repos)
    if not user_repos:
        abort(404, f"No repositories found for user '{username}' on GitHub.")
    # Process the data if needed
    return jsonify(user_repos)


if __name__ == "__main__":
    port = int(os.environ.get("GITHUB_API_PORT", 5000))
    myFlaskApp.run(port=port)
