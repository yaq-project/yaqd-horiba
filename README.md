# yaqd-horiba

[![PyPI version](https://badge.fury.io/py/yaqd-horiba.svg)](https://badge.fury.io/py/yaqd-horiba)
[![Conda](https://img.shields.io/conda/vn/conda-forge/yaqd-horiba)](https://anaconda.org/conda-forge/yaqd-horiba)
[![yaq](https://img.shields.io/badge/framework-yaq-orange)](https://yaq.fyi/)
[![black](https://img.shields.io/badge/code--style-black-black)](https://black.readthedocs.io/)
[![ver](https://img.shields.io/badge/calver-YYYY.0M.MICRO-blue)](https://calver.org/)
[![log](https://img.shields.io/badge/change-log-informational)](https://github.com/yaq-project/yaqd-horiba/blob/main/CHANGELOG.md)

yaq daemons for Horiba Jobin-Yvon hardware

This package contains the following daemon(s):
- [yaqd-horiba-micro-hr](https://yaq.fyi/daemons/horiba-micro-hr/)
- [yaqd-horiba-ihr320](https://yaq.fyi/daemons/horiba-ihr320/)

Example configuration files are included in the example-yaq-configs folder.

## drivers

This program does not use the manufacturer provided drivers for the device. Instead it uses libusb. I use https://zadig.akeo.ie/ to override the driver to WinUSB. (This has the advantage of being able to be rolled back to the manufacturer drivers if needed)

## maintainers

[Kent Meyer](https://github.com/kameyer226)

