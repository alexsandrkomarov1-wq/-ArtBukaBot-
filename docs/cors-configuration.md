# Browser access and CORS

Set CORE_CORS_ORIGINS to a comma-separated list of exact HTTPS origins that are allowed to call the API from a browser.

Example:
CORE_CORS_ORIGINS=https://family.example,https://preview.example

Do not use a wildcard origin with credentials. Add the final public website origin only after its deployment URL is known. The API defaults to no cross-origin browser access when this variable is empty.
