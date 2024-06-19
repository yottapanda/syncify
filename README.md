# Syncify

A tool that copies your "Liked Songs" to a regular playlist that you can make public and/or share with your friends.

For some reason doing this has always been impossible; it has bugged me for years. I finally decided to fix it myself.

## Usage

(Until Spotify approves the app, you won't be able to use the tool unless I add you to the tester's list)

1. Go to [syncify.thechubbypanda.dev](https://syncify.thechubbypanda.dev)
2. Press "Login with Spotify"
3. When prompted, allow access
4. Press the "Sync" button
5. Wait (it takes about 20 seconds to synchronize my ~1250 Liked Songs)
6. Follow the link to your new playlist or simply check your library

The tool will update the same playlist every time you press "Sync" so if you want to keep an iteration, just rename it and the tool will create a new playlist the next time around.

## Tech Stack

Syncify is primarily written in Golang using: 
- [zmb3](https://github.com/zmb3)'s Spotify API [library](https://github.com/zmb3/spotify)
- [Gomponents](https://www.gomponents.com/)
- [Chi Router](https://go-chi.io/#/)
- [Tailwind CSS](https://tailwindcss.com/)

This was my first time using Tailwind CSS and I must say, alongside Gomponents, it has made me reconsider my dislike of frontend development!
