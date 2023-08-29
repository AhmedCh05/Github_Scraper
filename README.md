# GitHub Web Scraper

This is a Python script that uses BeautifulSoup and requests to scrape user information and repositories from GitHub. It provides two main functionalities:

1. `scrape_user_info(username)`: Scrapes basic user information for a given GitHub username.
2. `scrape_user_repos(username)`: Scrapes repositories information for a given GitHub username.

## Installation

1. Clone this repository using:
   ```
   git clone https://github.com/yourusername/github-web-scraper.git
   ```
   
2. Install the required packages using:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Import the necessary functions from `github_scraper` module:
   ```python
   from github_scraper import scrape_user_info, scrape_user_repos
   ```

2. To scrape user information:
   ```python
   user_info = scrape_user_info("github_username")
   print(user_info)
   ```

3. To scrape user repositories:
   ```python
   repos_data = scrape_user_repos("github_username")
   print(repos_data)
   ```

## API Endpoints

The provided Flask application offers two API endpoints:

1. `GET /users/<username>`: Get user information.
2. `GET /users/<username>/repos`: Get user repositories information.

You can run the Flask app using the following command:
```bash
python app.py
```

## Notes

- This script uses web scraping techniques and might be subject to changes on GitHub's website structure, leading to potential issues.
- Respect GitHub's [Terms of Service](https://docs.github.com/en/github/site-policy/github-terms-of-service) and [API Usage Policy](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#resources).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to contribute to this project by reporting issues or submitting pull requests. Happy coding!
```

Please replace `"yourusername"` in the installation section with your actual GitHub username and adjust the content according to your preferences. Make sure to also include a `requirements.txt` file containing the necessary packages for your project.
