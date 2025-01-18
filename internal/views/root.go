package views

import (
	"github.com/yottapanda/syncify/internal/model"
	g "maragu.dev/gomponents"
	hx "maragu.dev/gomponents-htmx"
	. "maragu.dev/gomponents/html"
	"strconv"
)

func Root(model model.Model) g.Node {
	return Page(
		model,
		Div(Class("flex flex-col items-center justify-center h-screen gap-6 p-8"),
			Div(Class("flex flex-col items-center gap-2"),
				H1(Class("text-3xl font-bold"), g.Text("Syncify")),
				P(Class("text-lg text-gray-600 text-center"), g.Text("Sync your Spotify 'Liked Songs' playlist to a sharable one.")),
				UserText(model),
			),
			Buttons(model),
			Div(ID("spinner"), Class("inline w-8 h-8"), g.Raw(`<svg aria-hidden="true" class="text-gray-200 animate-spin fill-green-500" viewBox="0 0 100 100" fill="none">
<path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
<path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
</svg>`)),
			Outcome(model.SyncOutcome),
			P(
				Class("absolute bottom-0 p-4 text-center"),
				A(Class("text-green-500"), Href("https://github.com/yottapanda/syncify"), g.Text("Syncify")),
				g.Text(" is made with love by "),
				A(Class("text-green-500"), Href("https://github.com/yottapanda"), g.Text("yottapanda")),
			),
		),
	)
}

func UserText(model model.Model) g.Node {
	if model.User == nil {
		return Div()
	}
	return Div(
		Class("text-gray-500 dark:text-gray-400"),
		Span(g.Text("Logged in as "), Span(Class("font-medium"), g.Text(model.User.DisplayName))),
	)
}

func Buttons(model model.Model) g.Node {
	if model.User == nil {
		return Div(
			Class("flex gap-2"),
			A(
				Class("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 bg-green-500 hover:bg-green-600 text-white"),
				Href("/login"),
				g.Text("Login with Spotify"),
			),
		)
	}

	return Div(
		Class("flex gap-2"),
		Button(
			Class("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 bg-green-500 hover:bg-green-600 hover:scale-105 text-white hover:cursor-pointer"),
			hx.Get("/sync"),
			hx.Target("#outcome"),
			hx.Swap("outerHTML"),
			hx.Indicator("#spinner"),
			g.Text("Sync"),
		),
		A(
			Class("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input hover:scale-105 h-10 px-4 py-2"),
			Href("/logout"),
			g.Text("Logout"),
		),
	)
}

func Outcome(syncOutcome *model.SyncResponse) g.Node {
	var o g.Node
	if syncOutcome == nil {
		o = Div()
	} else if syncOutcome.Err != nil {
		o = g.Text("Error: " + syncOutcome.Err.Error())
	} else {
		o = Span(g.Text("Successfully synchronized "+strconv.Itoa(syncOutcome.Count)+" tracks to your "), A(Class("text-green-500"), Href(syncOutcome.PlaylistUrl), g.Text("Syncify playlist")))
	}
	return Div(ID("outcome"), Class("text-gray-500 text-center"), o)
}
