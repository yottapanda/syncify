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
			Script(Src("https://unpkg.com/htmx.org@1.9.12")),
			Script(Src("https://cdn.tailwindcss.com")),
			Link(Rel("stylesheet"), Href("/stylesheet.css")),
		},
		Body: contents,
	})
}
