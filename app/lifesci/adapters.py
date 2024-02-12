# myapp/adapters.py

from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter

class MyGitHubOAuth2Adapter(GitHubOAuth2Adapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        # Bypass the intermediate page and allow auto signup
        return True