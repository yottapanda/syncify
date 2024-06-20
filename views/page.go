package views

import (
	g "github.com/maragudk/gomponents"
	c "github.com/maragudk/gomponents/components"
	. "github.com/maragudk/gomponents/html"
	"github.com/thechubbypanda/syncify/config"
)

func Page(plausible config.Plausible, contents ...g.Node) g.Node {
	head := []g.Node{
		Meta(Name("description"), Content("Sync your Spotify 'Liked Songs' playlist to a sharable one.")),
		Meta(Name("keywords"), Content("spotify, sync, likes, liked, songs, public, playlist")),
		Meta(Name("author"), Content("Keval \"thechubbypanda\" Kapdee")),
		Script(Src("https://unpkg.com/htmx.org@1.9.12"), Integrity("sha384-ujb1lZYygJmzgSwoxRggbCHcjc0rB2XoQrxeTUQyRjrOnlCoYta87iKBWq3EsdM2"), CrossOrigin("anonymous")),
		Link(Rel("stylesheet"), Href("/stylesheet.css")),
	}
	if plausible.ScriptUrl != "" {
		head = append(head, Script(
			Src(plausible.ScriptUrl),
			Defer(),
			Data("domain", plausible.DataDomain),
			Data("api", plausible.DataApi),
		))
	}
	return c.HTML5(c.HTML5Props{
		Title:    "Syncify",
		Language: "en",
		Head:     head,
		Body:     contents,
	})
}
