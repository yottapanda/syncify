# Syncify

A tool that copies your "Liked Songs" to a regular playlist that you can make public and/or share with your friends.

For some reason doing this has always been impossible; it has bugged me for years. I finally decided to fix it myself.

## Usage

1. Go to [https://syncify.yottapanda.com](https://syncify.yottapanda.com)
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

## Self-Hosting

See the [examples directory](examples) for a docker-compose file that you can use to self-host Syncify.

Use the [example .env file](example.env) as a template for your own `.env` file.

## Development

Populate a `/.env` file with your own Spotify app's Client ID and Client Secret, see the [example .env file](example.env). It should look something like this:

```env
LOG_LEVEL=trace
CLIENT_ID=thisisdefinitelyasecret
CLIENT_SECRET=thisisdefinitelyasecret
URL=http://localhost:8000
```

Then you just need to run the following command:

```shell
docker compose up --build --watch
```

If you're using GoLand, you'll need to `Crtl+S` to get IntelliJ to write out the files that you've changed or just swap to your browser and wait a second or two for compose to do it's magic.
