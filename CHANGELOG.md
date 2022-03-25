# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [2022.3.0]

### Fixed
- Raise when invalid turret requested
- Wait before setting slits and mirrors on startup/home so that they are set properly
- Add a stillness check to computation of busy
    - things like intermittant firmware busy going low due to e.g. backlashing
- Always loop update state instead of waiting for busy to go true. This ensures the slits are properly read
    - previously had be actually setting correctly but not updating reported position
- Avoid trying to set slits to NaN, which would raise an exception and prevent additional slits from being set

## [2021.10.0]

### Changed
- Convert IHR320 slit and mirror fields into properties, with added getters

## [2021.3.1]

### Fixed
- Minor fixes to the IHR320 found while testing

## [2021.3.0]

### Changed
- micro-hr renamed to horiba-micro-hr for consistency in the ecosystem
- updated configuration for gratings to have a string rather than integer

### Fixed
- added forgotten config options to is-daemon: enable, log_level, and log_to_file

### Added
- horiba-ihr320 daemon

## [2021.1.0]

### Fixed
- Set default turret to 0 instead of null
- prefer libusb0 backend, avoiding hard crash condition on some systems

### Added
- conda-forge as installation source

## [2020.11.1]

### Fixed
- set limits at startup

## [2020.11.0]

### Added
- added get-turret

### Changed
- regenerated avpr based on recent traits update
- use new trait system in core

## [2020.07.0]

### Changed
- Use flit for publishing to pypi
- Use Apache Avro as defined in [YEP-107](https://yeps.yaq.fyi/107/)

## [2020.05.0]

### Added
- added changelog
- add gitlab-ci
- add traits support
- added daemon-level version, see [YEP-105](https://yeps.yaq.fyi/105/)

### Changed
- Remove set_action decorator, use from syntax
- Remove pytest-runner
- Use daemon level loggers
- refactored gitlab-ci
- updated readme

## [0.1.0]

### Added
- initial release

[Unreleased]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2022.3.0...main
[2022.3.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2021.10.1...v2022.3.0
[2021.10.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2021.3.1...v2021.10.0
[2021.3.1]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2021.3.0...v2021.3.1
[2021.3.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2021.1.0...v2021.3.0
[2021.1.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2020.11.1...v2021.1.0
[2020.11.1]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2020.11.0...v2020.11.1
[2020.11.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2020.07.0...v2020.11.0
[2020.07.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v2020.05.0...v2020.07.0
[2020.05.0]: https://gitlab.com/yaq/yaqd-horiba/-/compare/v0.1.0...v2020.05.0
[0.1.0]: https://gitlab.com/yaq/yaqd-horiba/-/tags/v0.1.0
