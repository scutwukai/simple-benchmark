package main

import "fmt"
import "runtime"
import "net/http"


func main() {
    fmt.Println("cpus:", runtime.NumCPU())
    fmt.Println("goroot:", runtime.GOROOT())
    fmt.Println("archive:", runtime.GOOS)

    fmt.Println("set max process:", 1)
    runtime.GOMAXPROCS(1)

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        var header http.Header = w.Header()
        header.Add("Content-Type", "text/html; charset=utf-8")
	    fmt.Fprintf(w, "<html><h1>rps test</h1></html>")
    })

    http.ListenAndServe("127.0.0.1:3000", nil)
}
