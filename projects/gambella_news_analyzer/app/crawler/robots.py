from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import requests

class RobotsChecker:
    def __init__(self, start_url, user_agent, timeout=20):
        self.start_url = start_url
        self.user_agent = user_agent
        self.timeout = timeout
        self.rp = RobotFileParser()
        robots_url = urljoin(start_url, '/robots.txt')
        try:
            resp = requests.get(robots_url, headers={'User-Agent': user_agent}, timeout=timeout)
            if resp.ok:
                self.rp.parse(resp.text.splitlines())
            else:
                self.rp.parse([])
        except requests.RequestException:
            self.rp.parse([])

    def allowed(self, url):
        return self.rp.can_fetch(self.user_agent, url)
