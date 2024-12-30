package views

import (
	"github.com/thechubbypanda/syncify/internal/model"
	g "maragu.dev/gomponents"
	c "maragu.dev/gomponents/components"
	. "maragu.dev/gomponents/html"
)

func Page(model model.Model, contents ...g.Node) g.Node {
	head := []g.Node{
		Meta(Name("description"), Content("Sync your Spotify 'Liked Songs' playlist to a sharable one.")),
		Meta(Name("keywords"), Content("spotify, sync, likes, liked, songs, public, playlist")),
		Meta(Name("author"), Content("Keval \"thechubbypanda\" Kapdee")),
		Link(Rel("icon"), Href("/icon.png"), Type("image/svg+xml")),
		Script(Src("https://unpkg.com/htmx.org@1.9.12"), Async(), Integrity("sha384-ujb1lZYygJmzgSwoxRggbCHcjc0rB2XoQrxeTUQyRjrOnlCoYta87iKBWq3EsdM2"), CrossOrigin("anonymous")),
		Link(Rel("stylesheet"), Href("/stylesheet.css"), Type("text/css")),
	}
	if model.Plausible.ScriptUrl != "" {
		head = append(head, Script(
			Src(model.Plausible.ScriptUrl),
			Defer(),
			Data("domain", model.Plausible.DataDomain),
			Data("api", model.Plausible.DataApi),
		))
	}
	return c.HTML5(c.HTML5Props{
		Title:    "Syncify",
		Language: "en",
		Head:     head,
		Body:     contents,
	})
}
