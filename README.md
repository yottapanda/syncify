# Syncify

A tool that copies your "Liked Songs" to a regular playlist that you can make public and/or share with your friends.

For some reason doing this has always been impossible; it has bugged me for years. I finally decided to fix it myself.

## Usage

1. Go to [https://syncify.yottapanda.com](https://syncify.yottapanda.com)
2. Press "Login with Spotify"
3. When prompted, allow access
4. Press the "Sync" button
5. Wait (it takes about 20 seconds to synchronize my ~1250 Liked Songs)
6. Check your library for your new playlist(s)

The tool will update the same playlists by name every time you press "Enqueue Sync" so if you want to keep an iteration, just rename it and the tool will create a new playlist the next time around.

## Self-Hosting

See the [examples directory](examples) for a docker-compose file that you can use to self-host Syncify.

The [example.env](example.env) file contains more variables you can use to configure Syncify.

## Development

Populate a `/.env` file with your own Spotify app's Client ID and Client Secret, see the [example .env file](example.env).

Then you should be able to run the whole project with the following commands:

```shell
cd frontend
pnpm install
pnpm build
cd ..
uv sync
uv run syncify
```

If you're using PyCharm, you can also use the `all` run configuration which will do all the above for you.
