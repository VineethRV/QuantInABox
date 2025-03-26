package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"sort"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	kiteconnect "github.com/zerodha/gokiteconnect/v4"
)

var (
	apiKey string
	apiSecret string
	
)

var g_kc kiteconnect.Client



/*
JSON Request form required

{
	"exchange" : string -> NSE/BSE/NFO,
	"trading_symbol" : string -> Reliance/BANKNIFTY etc
	"transaction_type" : string -> buy/sell
	"quantity" : int 
	"product" : string -> MIS/NRML/CNC
	"order_type" : string -> MARKET/LIMIT/SL/SL-M
	"validity" : string -> DAY/IOC
	"variety" : string
*/
func place_order(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Placing an order\n")
	
	fmt.Println("JSON Request")
	body, err := io.ReadAll(r.Body)

	if err != nil {
		fmt.Printf("POST /order Error: %v\n", err)
		return
	}

	defer r.Body.Close()
	
	var result map[string]any
	err = json.Unmarshal([]byte(body), &result)

	if err != nil {
		fmt.Println("Failed to marshall json string")
		return
	}
	
	fmt.Println(result)
	exchange, ok := result["exchange"].(string)
	trading_symbol, ok := result["trading_symbol"].(string)
	transaction_type, ok := result["transaction_type"].(string)
	quantity, ok := result["quantity"].(int)
	product, ok := result["product"].(string)
	order_type, ok := result["order_type"].(string)
	validity, ok := result["validity"].(string)
	variety, ok := result["variety"].(string)

	if ok {
	}
	
	orderParams := kiteconnect.OrderParams {
		Exchange: exchange,
		Tradingsymbol: trading_symbol,
		TransactionType: strings.ToUpper(transaction_type),
		Quantity: quantity,
		Product: product,
		OrderType: order_type,
		Validity: validity,
	}

	_, err = g_kc.PlaceOrder(
		variety,
		orderParams,
	)

	if err != nil {
		fmt.Println("Failed to place order")
		return
	}

	fmt.Println("Successfuly placed order")
}

func get_orders(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Retrieving list of orders\n")

	orders, err := g_kc.GetOrders()

	if err != nil {
		fmt.Printf("GET /order error: %v\n", err)
		r.Response.StatusCode = 300
		return
	}
	
	fmt.Println("Orders")
	for _, order := range orders {
		fmt.Println("----------------")
		fmt.Printf("Order ID: %s\nOrder Type: %s\nVariety: %s\nProduct: %s\nStatus: %s\n", order.OrderID, order.OrderType, order.Variety, order.Product, order.Status)
	}

	fmt.Println("---------------")

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(orders)
}

func get_order(w http.ResponseWriter, r *http.Request) {

}

func close_order(w http.ResponseWriter, r* http.Request) {
	vars := mux.Vars(r)
	variety := vars["variety"]
	order_id := vars["order_id"]
	parent_order_id := ""
	resp, err := g_kc.CancelOrder(variety, order_id, &parent_order_id)

	if err != nil {
		fmt.Printf("DELETE /order/%s/%s Error: %v\n", variety, order_id, err)
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w, "Failed to close order")
		return
	}

	fmt.Printf("Closed Order ID: %s\n", resp.OrderID)
	w.WriteHeader(http.StatusAccepted)
	fmt.Fprintf(w, "Closed Order ID: %s", resp.OrderID) 
}

type InstrumentDetail struct {
	Name string 
	InstrumentToken int
	ExchangeToken int
	TradingSymbol string
	LastPrice float64
	Exchange string
	StrikePrice float64
}

func get_market_details(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	market := vars["market"]
	fmt.Printf("Retrieving market details of %s\n", market)
}
// Returns a json containing a list of InstrumentDetails similar in structure to InstrumentDetail
func get_markets_details(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Retreving list of available markets\n")

	instruments, err := g_kc.GetInstruments()
	if err != nil {
		fmt.Println("Failed to get Instruments details")
		return
	}

	var instruments_details []InstrumentDetail

	for _, instrument := range instruments {
		//fmt.Printf("Instrument token: %d | ExchangeToken: %d | Name: %s | LastPrice: %f\n", 
		//	instrument.InstrumentToken, instrument.ExchangeToken, instrument.Name, instrument.LastPrice)

		instruments_details = append(instruments_details, InstrumentDetail{
			instrument.Name,
			instrument.InstrumentToken,
			instrument.ExchangeToken,
			instrument.Tradingsymbol,
			instrument.LastPrice,
			instrument.Exchange,
			instrument.StrikePrice,
		})
	}

	// sort the array
	sort.Slice(instruments_details, func(i, j int) bool { return instruments_details[i].StrikePrice > instruments_details[j].StrikePrice })
	//fmt.Println(instruments_details)
	
	j, err := json.Marshal(instruments_details)
	if err != nil {
		fmt.Println("failed to marshall map into json")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(j)
}

func connect_to_zerodha() {
	kc := kiteconnect.New(apiKey)
	g_kc = *kc
	login_url := kc.GetLoginURL()

	// check if access token is valid for today 
	fileInfo, err := os.Stat("token.txt")
	if err != nil {
		fmt.Printf("Failed to get info\n")
		fmt.Println("Please login")
		exec.Command("xdg-open", login_url).Start()
		return
	}
	modTime := fileInfo.ModTime()
	now := time.Now()
	today := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())

	if modTime.After(today) {
		fmt.Println("Access token already exists for today")
		data, _ := os.ReadFile("token.txt")
		fmt.Printf("Access token for today is: %s\n", string(data))
		g_kc.SetAccessToken(string(data))
		return

	}
	fmt.Println("Requesting new access token")
	exec.Command("xdg-open", login_url).Start()
	fmt.Println("Please login before continuing to interact")
}

func set_client_access_token(request_token string) {

	fmt.Printf("Retrieved request token: %s\n", request_token)
	data, err := g_kc.GenerateSession(request_token, apiSecret)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("New access token: %s\n", data.AccessToken)
	g_kc.SetAccessToken(data.AccessToken)

	// write access token locally
	os.WriteFile("token.txt", []byte(data.AccessToken), 0644)
}
func request_token_callback(w http.ResponseWriter, r* http.Request) {
	request_token := r.URL.Query().Get("request_token")

	set_client_access_token(request_token)		
}

func setup_env() {
	err := godotenv.Load(".env")
	if err != nil {
		fmt.Println("Failed to load environemt variables")
		return
	}
	apiKey = os.Getenv("API_KEY")
	apiSecret = os.Getenv("API_SECRET")
	fmt.Printf("API KEY: %s\nAPI_SECRET: %s\n", apiKey, apiSecret)
}

func initialize_trade(router* mux.Router) {

	setup_env()
	
	router.HandleFunc("/order/{order_id}", get_order).Methods("GET")
	router.HandleFunc("/order", get_orders).Methods("GET")
	router.HandleFunc("/order", place_order).Methods("POST")
	router.HandleFunc("/order/{variety}/{order_id}", close_order).Methods("DELETE")
	router.HandleFunc("/market", get_markets_details).Methods("GET")
	router.HandleFunc("/market/{market}", get_market_details).Methods("GET")
	router.HandleFunc("/qiab", request_token_callback)

	connect_to_zerodha()
}



