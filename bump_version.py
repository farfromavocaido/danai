import toml
import subprocess

# Load the current version from pyproject.toml
with open('pyproject.toml', 'r') as f:
    data = toml.load(f)

# Get the current version
version = data['project']['version']
manual_version_set = version

# Split version into major, minor, patch
major, minor, patch = map(int, version.split('.'))

# Get the latest commit message to check for manual version change
# Get the last commit's message
commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()

# Check if there's a manual version bump
if f"version={manual_version_set}" in commit_message:
    print(f"Manual version set: {manual_version_set}")
    # Outputs for the GitHub action
    print("::set-output name=should_publish::true")
else:
    # Increment the patch version
    patch += 1
    new_version = f"{major}.{minor}.{patch}"

    # Update the pyproject.toml with the new version
    data['project']['version'] = new_version
    with open('pyproject.toml', 'w') as f:
        toml.dump(data, f)

    # Commit the version bump
    subprocess.run(['git', 'config', '--global', 'user.name', 'github-actions[bot]'])
    subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions[bot]@users.noreply.github.com'])
    subprocess.run(['git', 'add', 'pyproject.toml'])
    subprocess.run(['git', 'commit', '-m', f"Bump version to {new_version}"])
    subprocess.run(['git', 'tag', f"v{new_version}"])
    subprocess.run(['git', 'push', '--follow-tags'])

    # Outputs for the GitHub action
    print(f"Version bumped to {new_version}")
    print("::set-output name=should_publish::true")