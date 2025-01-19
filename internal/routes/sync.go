package routes

import (
	"context"
	"github.com/sirupsen/logrus"
	"github.com/yottapanda/syncify/internal/auth"
	"github.com/yottapanda/syncify/internal/sync"
	"github.com/yottapanda/syncify/internal/views"
	"net/http"
	"time"
)

func TimeoutMiddleware(timeout time.Duration) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ctx, cancel := context.WithTimeout(r.Context(), timeout)
			defer cancel()

			next.ServeHTTP(w, r.WithContext(ctx))

			deadline, ok := ctx.Deadline()
			if !ok || time.Now().Before(deadline) {
				logrus.Errorln("Request timed out")
			}
		})
	}
}

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
