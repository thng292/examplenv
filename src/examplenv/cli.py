"""Generate example.env.* files from .env.* files recursively.

Extracts variable names and infers their value types.
"""

import os
import re
import sys
from typing import Iterable, Annotated
from pathlib import Path

import typer


app = typer.Typer()

def should_ignore(key: str, val: str):
    return key.endswith("API_KEY") or val.startswith(("sk",))


def parse_env_file(file_path: Path) -> Iterable[tuple[str, str] | str]:
    """Parse a .env file and extract variable names and their inferred types.

    Args:
        file_path: Path to the .env file

    Returns:
        Dictionary mapping variable names to their inferred types
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    yield line
                    continue

                if "=" not in line:
                    yield line
                    continue

                key, value = line.split("=", 1)
                key = key.strip()

                # Skip if key is empty
                if not key:
                    yield line
                    continue
                # Remove quotes from value if present
                value = value.strip().strip("\"'")
                yield (key, value)

    except OSError as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)


def generate_example_env_file(original_file: Path) -> str:
    """Generate content for an example.env file.

    Args:
        original_file: Path to the original .env file

    Returns:
        String content for the example.env file>
    """
    env_vars = parse_env_file(original_file)
    lines = [f"# Example environment variables for {original_file.name}"]

    for line in env_vars:
        if isinstance(line, tuple):
            value = line[1]
            if should_ignore(line[0], line[1]):
                value = f"<YOUR_{line[0]}>"
            lines.append(f"{line[0]}={value}")
        else:
            lines.append(line)

    lines.append("")
    return "\n".join(lines)


def find_env_files(
    root_dir: Path,
    pattern: re.Pattern[str] = re.compile(r"^\.env(\..+)?$"),
) -> list[Path]:
    env_pattern = pattern
    found_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        skip_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".next",
        }
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            if env_pattern.match(filename):
                file_path = Path(dirpath) / filename
                found_files.append(file_path)

    if not found_files:
        print("No .env files found.")
        return []

    print(f"Found {len(found_files)} .env file(s):\n")
    return found_files


def find_and_gen_example_env_files(root_dir: Path) -> None:
    """Recursively find .env.* files and generate corresponding example files.

    Args:
        root_dir: Root directory to start the search
    """
    for env_file in find_env_files(root_dir):
        print(f"Processing: {env_file}")

        # Parse the env file
        # Generate example file
        example_content = generate_example_env_file(env_file)

        # Determine output filename
        if env_file.name == ".env":
            example_file = env_file.parent / "example.env"
        else:
            # .env.something -> example.env.something
            example_file = env_file.parent / f"example{env_file.name}"

        # Write example file
        try:
            with open(example_file, "w", encoding="utf-8") as f:
                f.write(example_content)
            print(f"  ✓ Generated: {example_file.relative_to(root_dir)}\n")
        except OSError as e:
            print(f"  ✗ Error writing {example_file}: {e}\n", file=sys.stderr)


def to_dict(iterable: Iterable[str | tuple[str, str]]):
    res: dict[str, str | None] = {}
    for it in iterable:
        if isinstance(it, tuple):
            res[it[0]] = it[1]
        else:
            res[it] = None

    return res


def find_and_migrate_env_files(root_dir: Path):
    for example_env_file in find_env_files(
        root_dir, re.compile(r"^example\.env(\..+)?$")
    ):
        print(f"Processing: {example_env_file}")
        env_file = example_env_file.parent / example_env_file.name.removeprefix(
            "example"
        )
        if env_file.exists() and env_file.is_file():
            example_env_vars = to_dict(parse_env_file(example_env_file))
            env_vars = to_dict(parse_env_file(env_file))
            lines: list[str] = []

            for key, val in example_env_vars.items():
                if val:
                    if should_ignore(key, val):
                        lines.append(f"{key}={val}")
                else:
                    lines.append(key)

            example_content = "\n".join(lines)
        else:
            with open(example_env_file) as f:
                example_content = f.read()

        # Write example file
        try:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(example_content)
            print(f"  ✓ Generated: {env_file.relative_to(root_dir)}\n")
        except OSError as e:
            print(f"  ✗ Error writing {env_file}: {e}\n", file=sys.stderr)

def checkPath(path: Path):
    if not path.exists():
        print(f"Error: Directory {path} does not exist.", file=sys.stderr)
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: {path} is not a directory.", file=sys.stderr)
        sys.exit(1)

@app.command()
def gen_example_env(
    dir_to_find: Annotated[
        Path | None,
        typer.Argument(help="Path to search for env file"),
    ] = None,
):
    """Find and generate all examples for all .env files."""
    root_dir = dir_to_find if dir_to_find else Path.cwd()
    checkPath(root_dir)

    print(f"Searching for .env files in: {root_dir}\n")
    find_and_gen_example_env_files(root_dir)
    print("Done!")


@app.command()
def migrate(
    dir_to_find: Annotated[
        Path | None, typer.Argument(help="Path to search for env file")
    ],
):
    """Migrate the env file for you."""
    root_dir = dir_to_find if dir_to_find else Path.cwd()
    checkPath(root_dir)

    print(f"Searching for .env files in: {root_dir}\n")
    find_and_migrate_env_files(root_dir)
    print("Done!")

def main():
    app()

if __name__ == "__main__":
    main()
