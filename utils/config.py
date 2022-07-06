from os import environ

INSTAGRAM_POST_PATTERN = "^(https?:\/\/(?:www\.)?instagram\.com(?:\/(?!.*\.\.)(?!.*\.$)[^\W][\w.]{2,29})?\/(?:p|tv|reel)\/([^\/?#&]+)).*$"
INSTAGRAM_STORY_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/stories\\/([^/?#&]+)).*$"
INSTAGRAM_PROFILE_PATTERN = "^(https?:\\/\\/(?:www\\.)?instagram\\.com(?:\\/(?!.*\\.\\.)(?!.*\\.$)[^\\W][\\w.]{2,29})?\\/([^/?#&]+)).*$"
TWITTER_PATTERN = "^(https?:\/\/(?:www\.)?(?:mobile\.)?twitter\.com(?:\/(?!.*\.\.)(?!.*\\.$)[^\W][\w.]{1,30})?\/status(es)?\/([\d+]{16,19}))"
INSTA_SESSION = environ["INSTA_TOKEN"]