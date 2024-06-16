package views

import (
	g "github.com/maragudk/gomponents"
	c "github.com/maragudk/gomponents/components"
	. "github.com/maragudk/gomponents/html"
)

func Page(contents ...g.Node) g.Node {
	return c.HTML5(c.HTML5Props{
		Title:    "Syncify",
		Language: "en",
		Head: []g.Node{
			Meta(Name("description"), Content("Sync your Spotify 'Liked Songs' playlist to a sharable one.")),
			Meta(Name("keywords"), Content("spotify, sync, likes, liked, songs, public, playlist")),
			Meta(Name("author"), Content("Keval \"thechubbypanda\" Kapdee")),
			Script(Src("https://unpkg.com/htmx.org@1.9.12")),
			Script(Src("https://cdn.tailwindcss.com")),
			Link(Rel("stylesheet"), Href("/stylesheet.css")),
		},
		Body: contents,
	})
}
