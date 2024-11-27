package session

import (
	"github.com/alexedwards/scs/v2"
	"github.com/alexedwards/scs/v2/memstore"
	"github.com/thechubbypanda/syncify/internal/config"
	"net/http"
	"strings"
)

var Manager = scs.New()

func InitManager(cfg *config.Config) {
	Manager.Store = memstore.New()

	Manager.Cookie.Secure = strings.HasPrefix(cfg.Url, "https")
	Manager.Cookie.HttpOnly = true
	Manager.Cookie.Persist = false
	Manager.Cookie.Name = "syncify_session"
	Manager.Cookie.SameSite = http.SameSiteLaxMode
}
