# x0 Share

A small ZoiteChat / HexChat Python addon that uploads a file to an x0.at-compatible upload host and pastes the returned URL into the chat tab where you started the upload. Humanity did invent at least one useful shortcut.

## Features

* Upload files to the default x0.at service
* Support any 0x0-style compatible upload host
* Send the returned URL directly into the active channel or private message tab
* Configure a custom upload host
* Reset back to the default host
* GTK file chooser support, with Tkinter fallback
* Background uploads so the client stays responsive

## Requirements

* ZoiteChat or HexChat
* Python plugin support enabled
* PyGObject / GTK recommended, or Tkinter as fallback

## Install

Copy the script into your ZoiteChat / HexChat Python addons folder, or load it manually through the client.

## Where the menu appears

This addon adds a **0x0 Share** submenu in both of these places:

* Tab right-click menu
* Channel right-click menu

## Menu options

### Share File...

Opens a file chooser, uploads the selected file to the configured upload host, and sends the returned URL into the current chat tab.

### Preferences...

Opens a small preferences dialog where you can set the upload host URL.

Example:

```text
https://x0.at
```

### Reset Host to Default

Clears the saved custom host and resets the addon back to the default upload host:

```text
https://x0.at
```

## Commands

```text
/0X0SHARE [full-path]
```

Upload a file and send the returned URL to the current tab.

```text
/0X0SHAREHOST [url]
```

Show or set the upload host.

```text
/0X0SHARECONF
```

Open the preferences dialog.

```text
/0X0SHARERESET
```

Reset the upload host to the default.

## Notes

The default upload host is:

```text
https://x0.at
```

The upload host must accept the same simple multipart file upload flow as 0x0-style services and return the uploaded file URL as plain text.

Existing custom hosts are still supported. Resetting the host will return the addon to `https://x0.at`.

Uploads run in the background so the client stays responsive.
::: 
