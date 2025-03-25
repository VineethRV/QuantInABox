package main

import (
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"
)


func main() {
	fmt.Printf("Starting Quant In a Box\n");
	router := mux.NewRouter()
	initialize_trade(router)

	srv := &http.Server{
		Handler: router,
		Addr: "127.0.0.1:8000",

		WriteTimeout: 15 * time.Second,
		ReadTimeout: 15 * time.Second,
	}

	srv.ListenAndServe()
	
}
