package routes

import (
	"github.com/sirupsen/logrus"
	"github.com/yottapanda/syncify/internal/auth"
	"github.com/yottapanda/syncify/internal/sync"
	"github.com/yottapanda/syncify/internal/views"
	"net/http"
)

func Sync(w http.ResponseWriter, r *http.Request) {
	s, err := auth.GetClient(r)
	if err != nil {
		logrus.Debugln(err)
		http.Redirect(w, r, "/login", http.StatusTemporaryRedirect)
		return
	}

	syncResponse := sync.Sync(r.Context(), s)

	err = views.Outcome(&syncResponse).Render(w)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}
