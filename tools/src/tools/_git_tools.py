import re
import subprocess

def get_upstream_url():
    try:
        # This gets the URL of the 'origin' remote
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            check=True,
            capture_output=True,
            text=True
        )
        url = result.stdout.strip()

        # Convert a ssh link to a http link
        if url.startswith('git@'):
            url = 'https://' + re.sub(':', '/', url.partition('@')[-1])
        
        return url if url else None
    except subprocess.CalledProcessError:
        return None

# url = get_upstream_url()
# print(url)

def get_git_username():
    try:
        name = subprocess.run(["git", "config", "user.name"],
                              text=True, capture_output=True, check=True).stdout.strip()
        if name:
            return name
    except Exception:
        pass
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_gecos or pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        return os.getenv("USER") or "unknown"

def get_github_username():
    # Helper to run commands safely
    def run(cmd):
        try:
            return subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=1,     # prevents hangs
                check=False    # don't raise exceptions
            )
        except Exception:
            return None

    # 1. Use GitHub CLI *only if logged in*
    status = run(["gh", "auth", "status"])
    if status and status.returncode == 0:
        result = run(["gh", "api", "user", "--jq", ".login"])
        if result:
            user = result.stdout.strip()
            if user:
                return user

    # 2. Try git remote URL
    remote = run(["git", "remote", "get-url", "origin"])
    if remote:
        url = remote.stdout.strip()
        if "github.com" in url:
            m = re.search(r"github\.com[:/](?P<user>[^/]+)/", url)
            if m:
                return m.group("user")

    # 3. Try git config github.user
    config = run(["git", "config", "github.user"])
    if config:
        user = config.stdout.strip()
        if user:
            return user

    return None

    # 4. Try environment variables
    for var in ("GITHUB_USER", "GH_USERNAME"):
        if os.getenv(var):
            return os.getenv(var)

    # 5. Fallback to author name (last resort)
    try:
        user = subprocess.run(
            ["git", "config", "user.name"],
            text=True, capture_output=True, check=True
        ).stdout.strip()
        if user:
            return user
    except Exception:
        pass

    return None


def detect_license_type(lic_text: str) -> str:
    text = lic_text.lower()
    if 'mit license' in text:
        return 'MIT'
    if 'gnu general public license' in text or 'gpl' in text:
        return 'GPL-3.0'
    if 'apache license' in text:
        return 'Apache-2.0'
    if 'bsd' in text:
        return 'BSD-3-Clause'
    return 'Custom'
