package routes

import (
	logger "github.com/chi-middleware/logrus-logger"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/sirupsen/logrus"
	"github.com/thechubbypanda/syncify/internal/config"
	"github.com/thechubbypanda/syncify/internal/session"
	"net/http"
	"strings"
)

func CreateRouter(cfg *config.Config) *chi.Mux {
	r := chi.NewRouter()

	cspParts := []string{"default-src 'self'", "style-src 'self' 'unsafe-inline'"}
	scriptSources := []string{"unpkg.com"}
	connectSources := []string{"'self'"}
	if cfg.Plausible.ScriptUrl != "" {
		scriptSources = append(scriptSources, cfg.Plausible.Origin)
		connectSources = append(connectSources, cfg.Plausible.Origin)
	}
	cspParts = append(cspParts, "script-src "+strings.Join(scriptSources, " "))
	cspParts = append(cspParts, "connect-src "+strings.Join(connectSources, " "))

	r.Use(
		middleware.RealIP,
		middleware.StripSlashes,
		logger.Logger("router", logrus.StandardLogger()),
		session.Manager.LoadAndSave,
		middleware.SetHeader("Content-Security-Policy", strings.Join(cspParts, "; ")),
		middleware.SetHeader("Strict-Transport-Security", "max-age=2592000"),
		middleware.SetHeader("X-Frame-Options", "DENY"),
		middleware.SetHeader("X-Content-Type-Options", "nosniff"),
		middleware.SetHeader("Referrer-Policy", "strict-origin"),
		middleware.SetHeader("Permissions-Policy", "accelerometer=(), autoplay=(), camera=(), cross-origin-isolated=(), display-capture=(), encrypted-media=(), fullscreen=(), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), xr-spatial-tracking=()"),
	)

	r.Route("/", func(r chi.Router) {
		r.Get("/", Root)
		r.Get("/sync", Sync)
		r.Get("/login", Login)
		r.Get("/logout", Logout)
		r.Get("/callback", Callback)
		r.Route("/", func(r chi.Router) {
			r.Get("/*", http.StripPrefix("/", http.FileServer(http.Dir("static/"))).ServeHTTP)
		})
	})

	return r
}
