BACKEND_VERSION=$(grep '^version =' pyproject.toml | sed -E 's/version = ["'\''](.*)["'\'']/\1/')
BACKEND_VERSION=$(echo $BACKEND_VERSION | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+)-alpha\.([0-9]+)/\1a\2/')
echo "backend_version: $BACKEND_VERSION"