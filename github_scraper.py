import requests
import re
from bs4 import BeautifulSoup
import time


def scrape_user_info(username):
    url = f"https://github.com/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Parse the HTML content using BeautifulSoup and extract user info
        avatar_img = soup.select_one(".avatar-user")
        name = soup.select_one(".p-name").get_text().strip()
        company = (
            soup.select_one(".p-org").get_text().replace("@", "").capitalize()
            if soup.select_one(".p-org")
            else None
        )
        blog_element = soup.select_one("a.Link--primary[href^='https://github.blog']")
        twitter_element = soup.select_one(
            "a.Link--primary[href^='https://twitter.com/']"
        )

        if blog_element:
            blog = blog_element.get("href")
        else:
            blog = None

        if twitter_element:
            twitter_username = twitter_element.get_text().strip("@")
        else:
            twitter_username = None

        location = (
            soup.select_one(".p-label").get_text()
            if soup.select_one(".p-label")
            else None
        )
        bio = (
            soup.select_one(".p-note.user-profile-bio")
            .get_text()
            .strip()
            .replace("\n", " ")
            if soup.select_one(".p-note.user-profile-bio")
            else None
        )
        public_repos = (
            int(soup.select_one(".Counter").get("title"))
            if soup.select_one(".Counter")
            else None
        )

        followers_element = soup.select_one(
            "a.Link--secondary[href$='?tab=followers'] span.text-bold.color-fg-default"
        )

        if followers_element:
            followers_text = followers_element.get_text().strip()
            if followers_text[-1] == "k":
                followers_count = int(
                    float(re.sub(r"[^\d.]", "", followers_text)) * 1000
                )
            else:
                followers_count = int(re.sub(r"\D", "", followers_text))
        else:
            followers_count = None

        following_element = soup.select_one(
            "a.Link--secondary[href$='?tab=following'] span.text-bold.color-fg-default"
        )

        if following_element:
            following_text = following_element.get_text().strip()
            if following_text[-1] == "k":
                following_count = following_text
            else:
                following_count = int(re.sub(r"\D", "", following_text))
        else:
            following_count = None

        img_tag = soup.find("img", class_="avatar-user")
        src = img_tag["src"]
        user_id = src.split("/")[-1].split("?")[0]

        user_info = {
            "login": username,
            "id": user_id,
            "avatar_url": avatar_img.get("src") if avatar_img else None,
            "url": url,
            "html_url": f"https://github.com/{username}",
            "type": "User",
            "name": name,
            "company": company,
            "blog": blog,
            "location": location,
            "bio": bio,
            "twitter_username": twitter_username,
            "public_repos": public_repos,
            "followers": followers_count,
            "following": following_count,
        }
        return user_info


def get_with_backoff(url, max_retries=5):
    retries = 0
    while retries < max_retries:
        response = requests.get(url)
        if response.status_code == 429:
            wait_time = retries**2
            print(f"Rate limited. Retrying after {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        else:
            return response
    return None


def scrape_user_repos(username):
    url = f"https://github.com/{username}?tab=repositories"
    response = get_with_backoff(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        repos_list = []

        repos = soup.select("#user-repositories-list ul li")

        for repo in repos:
            repo_link = repo.find("h3", class_="wb-break-all").find("a")["href"]
            second_url = f"https://github.com{repo_link}"

            owner_elem = soup.find("span", class_="p-nickname vcard-username d-block")
            owner_data = owner_elem.get_text() if owner_elem else "Owner data not found"

            img_tag = soup.find("img", class_="avatar-user")
            src = img_tag["src"]
            user_id = src.split("/")[-1].split("?")[0]

            response_second = requests.get(second_url)
            soup_second = BeautifulSoup(response_second.text, "html.parser")

            repo_last_updated = repo.select_one("relative-time")["datetime"]

            archived_message = soup.find(
                "span", string="This repository has been archived."
            )
            if archived_message:
                is_archived = True
            else:
                is_archived = False

            issues_tab = soup_second.find("a", {"id": "issues-tab"})
            has_issues = bool(issues_tab)

            projects_tab = soup_second.find("a", {"href": f"{repo_link}/projects"})
            if projects_tab:
                has_projects = True
            else:
                has_projects = False

            discussions_tab = soup_second.find(
                "a", {"data-selected-links": "repo_discussions"}
            )
            if discussions_tab:
                has_discussions = True
            else:
                has_discussions = False

            default_branch_element = soup_second.find(
                "span", class_="css-truncate-target"
            )
            default_branch = default_branch_element.text.strip()

            inner_link = soup_second.find("a", class_="Link no-underline")["href"]
            repo_id = inner_link.split("repo=")[-1]

            repo_name = repo.select_one("h3 a").text.strip()
            repo_description_element = repo.select_one("p[itemprop='description']")
            repo_description = (
                repo_description_element.text.strip()
                if repo_description_element
                else None
            )

            summary_element = soup.select_one(".user-repo-search-results-summary")

            if summary_element:
                language_elements = summary_element.select("strong")
                if len(language_elements) >= 2:
                    repo_language = language_elements[1].text.strip()
                else:
                    repo_language = None
            else:
                repo_language = None

            repo_stars_element = repo.select_one("a[href$='/stargazers']")
            repo_stars = (
                int(repo_stars_element.text.strip().replace(",", ""))
                if repo_stars_element
                else 0
            )

            repo_forks_element = repo.select_one("a[href$='/forks']")

            repo_forks = (
                int(repo_forks_element.text.strip().replace(",", ""))
                if repo_forks_element
                else 0
            )
            visibility_element = repo.select_one(".Label--secondary")
            visibility_text = visibility_element.text.strip()
            if visibility_text == "Public":
                visibility = False
            else:
                visibility = True

            allow_fork_element = repo.select_one("a[href*='/forks']")
            if allow_fork_element:
                allow_fork = True
            else:
                allow_fork = False

            watchers_count_element = repo.select_one("a[href*='/watchers'] strong")
            if watchers_count_element:
                watchers_count_text = watchers_count_element.get_text(strip=True)
                watchers_count = int(watchers_count_text.replace(",", ""))
            else:
                watchers_count = None  # or you can handle it as per your requirement

            issues_count_element = repo.select_one("span#issues-repo-tab-count")

            if issues_count_element:
                issues_count = issues_count_element.text
            else:
                issues_count = None  # or handle it as per your requirement

            issue_count_element = soup.find("span", {"id": "issues-repo-tab-count"})
            if issue_count_element:
                issue_count_text = issue_count_element.text
            else:
                issue_count_text = None

            repo_info = {
                "id": repo_id,
                "name": repo_name,
                "full_name": f"{username}/{repo_name}",
                "owner": {
                    "login": owner_data,
                    "id": user_id,
                },
                "private": visibility,
                "html_url": f"https://github.com/{username}/{repo_name}",
                "description": repo_description,
                "fork": allow_fork,
                "url": f"https://api.github.com/repos/{username}/{repo_name}",
                "homepage": "https://github.com",  # This can be modified based on your logic
                "language": repo_language,
                "forks_count": repo_forks,
                "stargazers_count": repo_stars,
                "watchers_count": watchers_count,  # Assuming watchers count is the same as stargazers count
                "default_branch": default_branch,  # This can be modified based on your logic
                "pushed_at": repo_last_updated,
                "open_issue_count": issues_count,
                "has_issues": has_issues,
                "has_projects": has_projects,
                "has_discussions": has_discussions,
                "archived": is_archived,
            }

            repos_list.append(repo_info)

        return repos_list
    else:
        return []


repos_data = scrape_user_repos("github_username")
print(repos_data)
