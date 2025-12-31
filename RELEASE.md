# Release Guide

This project uses automated GitHub Actions for releases.

## How to Release
1. Ensure all tests pass on `main`.
2. Create a new tag: `git tag v1.0.0`
3. Push the tag: `git push origin v1.0.0`
4. The **Release** workflow will automatically:
   - Build binaries for Windows, macOS, and Linux.
   - Publish the package to PyPI.
   - Create a GitHub Release with assets.
