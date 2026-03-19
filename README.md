# ZoiteChat Addons

Community addons, scripts, plugins, and extensions for **ZoiteChat**.

This repository collects user-contributed ZoiteChat addons in one place, organized by language so people do not have to go treasure hunting through forum posts, pastebins, and forgotten web directories.

## Repository layout

Addons in this repository are sorted by language:

```text
python/
perl/
lua/
c/
tcl/
````

Each addon should live in the folder that matches the language it is written in.

Example:

```text
python/my-addon/
perl/nick-helper/
lua/channel-tools/
c/example-plugin/
tcl/legacy-script/
```

## What belongs here

This repo is for ZoiteChat-related extensions, including:

* Python scripts
* Perl scripts
* Lua scripts
* C plugins or addon source
* Tcl scripts
* Supporting documentation for submitted addons

## How to submit an addon

Addons are submitted through a **Pull Request**.

### Submission steps

1. Fork this repository
2. Create a branch for your addon or update
3. Add your addon under the correct language folder
4. Include a `README.md` inside your addon folder
5. Open a Pull Request with a clear description

## Required submission structure

Each addon should have its own folder inside the correct language directory.

Example:

```text
python/my-addon/
├── README.md
├── LICENSE
├── my-addon.py
└── optional-extra-files
```

## What to include with your submission

Each addon submission should include:

* The addon files
* A `README.md` for that addon
* License information
* Install instructions
* Basic usage information
* Version information, if applicable
* Your name or handle, if you want to include it

## Addon README expectations

Your addon README should explain:

* What the addon does
* Which language it uses
* How to install it
* How to configure it
* How to use it
* Any dependencies or requirements
* Any known limitations
* Which ZoiteChat versions it is intended for, if relevant

## Pull Request guidelines

Please keep PRs clean and focused.

### Do

* Submit your addon in the correct language folder
* Keep one addon or one logical update per PR
* Use clear folder and file names
* Document what the addon does
* Include a license
* Confirm the addon works in ZoiteChat

### Do not

* Put addons in the wrong language directory
* Bundle unrelated changes in the same PR
* Include compiled junk, temp files, or editor backups
* Submit broken, incomplete, or malicious code
* Copy someone else’s work without proper rights or licensing

## Review process

Pull Requests may be reviewed for:

* Relevance to ZoiteChat
* Correct folder placement
* Basic functionality
* Code cleanliness
* Documentation quality
* Licensing clarity
* Safety and usefulness

Submission does **not** guarantee acceptance.

## Licensing

You must have the right to submit the code you are contributing.

By opening a Pull Request, you confirm that:

* You wrote the code, or
* You have permission to redistribute it, and
* The license is clearly stated

If no license is included, the submission may be declined.

## Updating an existing addon

To update an addon already in the repo:

1. Fork the repository
2. Make your changes in the existing addon folder
3. Update the addon documentation if needed
4. Open a Pull Request explaining what changed

## Reporting problems

If an addon has issues, open an issue in this repository with:

* Addon name
* Language
* ZoiteChat version
* Operating system
* Error details
* Steps to reproduce

## Notes for contributors

Try to keep submissions easy to understand, install, and maintain.

Good submissions are:

* Useful
* Documented
* Safe
* Easy to test
* Placed in the correct language folder

## Thanks

Thanks to everyone contributing addons and helping improve ZoiteChat.
