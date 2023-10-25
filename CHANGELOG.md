# Changelog

## [0.5.3] - 2023-10-25
- Removed protobuf_to_dict/.
- fario2json uses google.protobuf.json_format now.
- fario2json --version option
- Bug fix. Message hash was not updated when re-signing with `fario-signers sign`
- Introduced json2fario. Needs work.

## [0.5.2] - 2023-10-24
- Bug fixes
- Dynamic dependancies
- Depends on farcaster-py==0.0.6

## [0.5] - 2023-10-24

- `fario-signers` replaced `fario-new-signer`, `fario-remove-signer` and `fario-sign`
- Updated README to reflect the changes caused by `fario-signers`.
- Dynamic package version based on \_\_about\_\_.py
- `fario-cast` has options for embeds and custom timestamp
- Various typos
- Removed unused code
- Added HOWTO/How_to_get_access_to_a_hub.md
- Updated the README cheatsheet with new examples (and fixed some typos)


# Metachangelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
