package main

import (
	"fmt"

	kiteconnect "github.com/zerodha/gokiteconnect/v4"
	kitemodels "github.com/zerodha/gokiteconnect/v4/models"
	kiteticker "github.com/zerodha/gokiteconnect/v4/ticker"
)

var (
	ticker *kiteticker.Ticker
)

var (
	instrument_tokens = []uint32{281854981}
)

func onError(err error) {
	fmt.Println("Error: ", err)
}

func onClose(code int, reason string) {
	fmt.Println("Close: ", code, reason)
}

func onConnect() {
	fmt.Println("Connected")
	err := ticker.Subscribe(instrument_tokens)
	if err != nil {
		fmt.Println("err: ", err)
	}

	err = ticker.SetMode(kiteticker.ModeFull, instrument_tokens)
	if err != nil {
		fmt.Println("err: ", err)
	}
}

func onTick(tick kitemodels.Tick) {
	fmt.Println("Tick: ", tick)
}

func onOrderUpdate(order kiteconnect.Order) {
	fmt.Println("Order Update: ", order.OrderID)
}

func start_ticker() {
	fmt.Println("Starting ticker...")
	apiKey := get_api_key()
	accessToken := get_access_token()
	fmt.Printf("API KEY: %s\nAccess Token: %s\n", apiKey, accessToken)
	ticker = kiteticker.New(apiKey, accessToken)

	ticker.OnError(onError)
	ticker.OnClose(onClose)
	ticker.OnConnect(onConnect)
	ticker.OnTick(onTick)
	ticker.OnOrderUpdate(onOrderUpdate)

	fmt.Println("Started ticker")
	go ticker.Serve()
}

func initialize_ticker() {
	start_ticker()
}
