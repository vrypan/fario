# Changelog

## [0.7.5] - 2023-11-21
- Requires farcaster-py==0.0.8 (SSL support)
- Updated commands that connect to hubs with a `--ssl` option
- `ssl=True` can also be defined in `.env` or `~/.fario`

## [0.7.4] - 2023-11-12
- Requires farcaster-py==0.0.7 (Supports FIP-10 changes)

## [0.7.3] - 2023-11-10
- Fixed a bug with `fario-out --links`
- New option `fario-grep --not-signer` 

## [0.7.2] - 2023-11-03
- New sub-command `fario-account fromsecret`
- New command `fario-grep`
- New command `fario-hubinfo`

## [0.7.1] - 2023-10-28
- Fixed a bug with fario-signers

## [0.7.0] - 2023-10-28
- all commands use config.get_config() to read configuration
- configuration can be environment, .env and (new) ~/.fario
- new command fario-config. Prints current config or outputs
sample config.
- some command parameters have changed names to get unified 
options naming between commands.
- merged json2fario
- numerous bug fixes, probably new bugs introduced :-)

## [0.6.1] - 2023-10-28
- Bug fix in fario_account.py

## [0.6.0] - 2023-10-26
- new option `fario-signers hash --keep-hash`
- breaking change: all options with underscores have been converted to dashes:
ex.: `--with_fnames` --> `--with-fnames`
- New command: `fario-account`. Still ugly, but works.
- six is no longer a requirement


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
