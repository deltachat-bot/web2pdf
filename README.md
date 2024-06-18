# Web to PDF

[![Latest Release](https://img.shields.io/pypi/v/deltabot-web2pdf.svg)](https://pypi.org/project/deltabot-web2pdf)
[![CI](https://github.com/deltachat-bot/web2pdf/actions/workflows/python-ci.yml/badge.svg)](https://github.com/deltachat-bot/web2pdf/actions/workflows/python-ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Delta Chat bot that allows to fetch websites as PDF. Just send any URL to the bot
in private or add it to get a PDF in any message containing an URL.

## Install

```sh
pip install deltabot-web2pdf
```

You also need to install wkhtmltopdf package. Debian/Ubuntu example:

```sh
sudo apt-get install wkhtmltopdf
```

**Warning!** Version in debian/ubuntu repos have reduced functionality (because it
is compiled without the wkhtmltopdf QT patches), such as adding outlines, headers,
footers, TOC etc. To use this options you should install static binary from
wkhtmltopdf site: https://wkhtmltopdf.org/

## Usage

Configure the bot's Delta Chat account:

```sh
web2pdf init bot@example.com PASSWORD
```

You can run `web2pdf init` several times to add multiple different accounts to the
bot so it can be reached in more than one email address.

The bot's display name, avatar and status/signature can also be tweaked:

```
web2pdf config selfavatar "/path/to/avatar.png"
web2pdf config displayname "My Bot"
web2pdf config selfstatus "Hi, I am a Delta Chat bot"
```

To run the bot so it starts processing messages:

```sh
web2pdf serve
```

To see all available options run `web2pdf --help`
