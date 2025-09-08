#!/usr/bin/env python3
"""
GitHub Repository Downloader MCP Tool using FastMCP
"""

import asyncio
import os
import re
from typing import Dict, List, Optional
from pathlib import Path

from mcp.server import FastMCP

# Create FastMCP instance
mcp = FastMCP("github-downloader")


class GitHubURLExtractor:
    """Tool class for extracting GitHub URLs"""

    @staticmethod
    def extract_github_urls(text: str) -> List[str]:
        """Extract GitHub URLs from text"""
        patterns = [
            # Standard HTTPS URL
            r"https?://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?",
            # SSH URL
            r"git@github\.com:[\w\-\.]+/[\w\-\.]+(?:\.git)?",
            # Short format owner/repo - stricter matching
            r"(?<!\S)(?<!/)(?<!\.)([\w\-\.]+/[\w\-\.]+)(?!/)(?!\S)",
        ]

        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Handle short format
                if isinstance(match, tuple):
                    match = match[0]

                # Clean URL
                if match.startswith("git@"):
                    url = match.replace("git@github.com:", "https://github.com/")
                elif match.startswith("http"):
                    url = match
                else:
                    # Handle short format (owner/repo) - add more validation
                    if "/" in match and not any(
                        x in match for x in ["./", "../", "deepcode_lab", "tools"]
                    ):
                        parts = match.split("/")
                        if (
                            len(parts) == 2
                            and all(
                                part.replace("-", "").replace("_", "").isalnum()
                                for part in parts
                            )
                            and not any(part.startswith(".") for part in parts)
                        ):
                            url = f"https://github.com/{match}"
                        else:
                            continue
                    else:
                        continue

                # Normalize URL
                url = url.rstrip(".git")
                url = url.rstrip("/")

                # Fix duplicate github.com
                if "github.com/github.com/" in url:
                    url = url.replace("github.com/github.com/", "github.com/")

                urls.append(url)

        return list(set(urls))  # Remove duplicates

    @staticmethod
    def extract_target_path(text: str) -> Optional[str]:
        """Extract target path from text"""
        # Path indicator patterns
        patterns = [
            r'(?:to|into|in|at)\s+(?:folder|directory|path)?\s*["\']?([^\s"\']+)["\']?',
            r'(?:save|download|clone)\s+(?:to|into|at)\s+["\']?([^\s"\']+)["\']?',
            # Chinese support (converted to English patterns)
            r'(?:to|at|save to|download to|clone to)\s*["\']?([^\s"\']+)["\']?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                path = match.group(1).strip("。，,.")
                # Filter out common words
                if path and path.lower() not in [
                    "here",
                    "there",
                    "current",
                    "local",
                    "this",
                    "that",
                ]:
                    return path

        return None

    @staticmethod
    def infer_repo_name(url: str) -> str:
        """Infer repository name from URL"""
        url = url.rstrip(".git")
        if "github.com" in url:
            parts = url.split("/")
            if len(parts) >= 2:
                return parts[-1]
        return "repository"


async def check_git_installed() -> bool:
    """Check if Git is installed"""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        return proc.returncode == 0
    except Exception:
        return False


async def clone_repository(repo_url: str, target_path: str) -> Dict[str, any]:
    """Execute git clone command"""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            repo_url,
            target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        return {
            "success": proc.returncode == 0,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "returncode": proc.returncode,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def download_github_repo(instruction: str) -> str:
    """
    Download GitHub repositories from natural language instructions.

    Args:
        instruction: Natural language text containing GitHub URLs and optional target paths

    Returns:
        Status message about the download operation

    Examples:
        - "Download https://github.com/openai/gpt-3"
        - "Clone microsoft/vscode to my-projects folder"
        - "Get https://github.com/facebook/react"
    """
    # Check if Git is installed
    if not await check_git_installed():
        return "❌ Error: Git is not installed or not in system PATH"

    extractor = GitHubURLExtractor()

    # Extract GitHub URLs
    urls = extractor.extract_github_urls(instruction)
    if not urls:
        return "❌ No GitHub URLs found in the instruction"

    # Extract target path
    target_path = extractor.extract_target_path(instruction)

    # Download repositories
    results = []
    for url in urls:
        try:
            # Prepare target path
            if target_path:
                # Check if absolute path
                if os.path.isabs(target_path):
                    # If absolute path, use directly
                    final_path = target_path
                    # If target path is directory, add repository name
                    if os.path.basename(target_path) == "" or target_path.endswith("/"):
                        final_path = os.path.join(
                            target_path, extractor.infer_repo_name(url)
                        )
                else:
                    # If relative path, keep as relative
                    final_path = target_path
                    # If target path is directory, add repository name
                    if os.path.basename(target_path) == "" or target_path.endswith("/"):
                        final_path = os.path.join(
                            target_path, extractor.infer_repo_name(url)
                        )
            else:
                final_path = extractor.infer_repo_name(url)

            # If relative path, ensure proper relative path format
            if not os.path.isabs(final_path):
                final_path = os.path.normpath(final_path)
                if final_path.startswith("/"):
                    final_path = final_path.lstrip("/")

            # Ensure parent directory exists
            parent_dir = os.path.dirname(final_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            # Check if target path already exists
            if os.path.exists(final_path):
                results.append(
                    f"❌ Failed to download {url}: Target path already exists: {final_path}"
                )
                continue

            # Execute clone
            result = await clone_repository(url, final_path)

            if result["success"]:
                msg = f"✅ Successfully downloaded: {url}\n"
                msg += f"   Location: {final_path}"
                if result.get("stdout"):
                    msg += f"\n   {result['stdout'].strip()}"
            else:
                msg = f"❌ Failed to download: {url}\n"
                msg += f"   Error: {result.get('error', result.get('stderr', 'Unknown error'))}"

        except Exception as e:
            msg = f"❌ Failed to download: {url}\n"
            msg += f"   Error: {str(e)}"

        results.append(msg)

    return "\n\n".join(results)


@mcp.tool()
async def parse_github_urls(text: str) -> str:
    """
    Extract GitHub URLs and target paths from text.

    Args:
        text: Text containing GitHub URLs

    Returns:
        Parsed GitHub URLs and target path information
    """
    extractor = GitHubURLExtractor()

    urls = extractor.extract_github_urls(text)
    target_path = extractor.extract_target_path(text)

    content = "📝 Parsed information:\n\n"

    if urls:
        content += "GitHub URLs found:\n"
        for url in urls:
            content += f"  • {url}\n"
    else:
        content += "No GitHub URLs found\n"

    if target_path:
        content += f"\nTarget path: {target_path}"
    else:
        content += "\nTarget path: Not specified (will use repository name)"

    return content


@mcp.tool()
async def git_clone(
    repo_url: str, target_path: Optional[str] = None, branch: Optional[str] = None
) -> str:
    """
    Clone a specific GitHub repository.

    Args:
        repo_url: GitHub repository URL
        target_path: Optional target directory path
        branch: Optional branch name to clone

    Returns:
        Status message about the clone operation
    """
    # Check if Git is installed
    if not await check_git_installed():
        return "❌ Error: Git is not installed or not in system PATH"

    # Prepare target path
    if not target_path:
        extractor = GitHubURLExtractor()
        target_path = extractor.infer_repo_name(repo_url)

    # Convert to absolute path
    if not os.path.isabs(target_path):
        target_path = str(Path.cwd() / target_path)

    # Check target path
    if os.path.exists(target_path):
        return f"❌ Error: Target path already exists: {target_path}"

    # Build command
    cmd = ["git", "clone"]
    if branch:
        cmd.extend(["-b", branch])
    cmd.extend([repo_url, target_path])

    # Execute clone
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            result = "✅ Successfully cloned repository\n"
            result += f"Repository: {repo_url}\n"
            result += f"Location: {target_path}"
            if branch:
                result += f"\nBranch: {branch}"
            return result
        else:
            return f"❌ Clone failed\nError: {stderr.decode('utf-8', errors='replace')}"

    except Exception as e:
        return f"❌ Clone failed\nError: {str(e)}"


# Main program entry
if __name__ == "__main__":
    print("🚀 GitHub Repository Downloader MCP Tool")
    print("📝 Starting server with FastMCP...")
    print("\nAvailable tools:")
    print("  • download_github_repo - Download repos from natural language")
    print("  • parse_github_urls - Extract GitHub URLs from text")
    print("  • git_clone - Clone a specific repository")
    print("")

    # Run server
    mcp.run()