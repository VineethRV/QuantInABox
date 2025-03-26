package main

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

func get_access_token() string {
	data, err := os.ReadFile("token.txt")
	if err != nil {
		fmt.Println("Failed to read file")
		return ""
	}

	return string(data)
}

func get_api_secret() string {
	return os.Getenv("API_SECRET")
}

func get_api_key() string {
	return os.Getenv("API_KEY")	
}

func initialize_utils() {
	err := godotenv.Load(".env")
	if err != nil {
		fmt.Printf("Failed to initialize utility functions\nError: %v\n", err)
		return;
	}
}
