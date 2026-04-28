# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.0.0] - 2023-01-02

### Changed
- Rewritten README

### Added
- Support for bash
  - Install script: install.sh
  - Entry point: gosh/gosh.sh

### Removed
- Old PowerShell things
- Old scripts

## [3.0.0] - 2022-02-22

### Changed
- For this release and forwards only pwsh is being supported as installation method
- Moved the changelog format to Keep a Changelog standard

### Removed
- install.sh

## [2.0.0] - 2021-11-19

### Added
- ark_bump_the_version integration for version management
- Installation script for Windows

### Changed
- Reformatted version message
- Removed __dundler__ info and moved to constants
- Improved path normalization to handle both / and \ separators

## [1.1.0]

### Added
- --help documentation

### Changed
- Show the name of the repository being pulled
