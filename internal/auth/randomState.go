package auth

import (
	"crypto/rand"
	"encoding/base64"
)

func RandomState() (string, error) {
	var bytes = make([]byte, 32)
	_, err := rand.Read(bytes)
	if err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(bytes), nil
}
