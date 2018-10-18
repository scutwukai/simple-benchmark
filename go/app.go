package main

import "io"
import "fmt"
import "path"
import "strings"
import "strconv"
import "runtime"
import "net/http"


func main() {
    fmt.Println("cpus:", runtime.NumCPU())
    fmt.Println("goroot:", runtime.GOROOT())
    fmt.Println("archive:", runtime.GOOS)

    fmt.Println("set max process:", 1)
    runtime.GOMAXPROCS(1)

    responses := make(map[int64]strings.Builder)
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        _, file := path.Split(r.URL.Path)
        msize, _ := strconv.ParseInt(file, 10, 0)

        m, ok := responses [ msize ]
        if (!ok) {
            for i := int64(0); i < msize; i++ {
                fmt.Fprintf(&m, "X")
            }

            responses [ msize ] = m
        }

        header := w.Header()
        header.Add("Content-Type", "text/plain; charset=utf-8")
	    fmt.Fprintf(w, m.String())
    })

    http.HandleFunc("/form", func(w http.ResponseWriter, r *http.Request) {
        r.ParseMultipartForm(1024 * 1024)

        var length int64
        for _, v := range r.MultipartForm.File {
            file, _ := v[0].Open()

            content := new(strings.Builder)
            length, _ = io.Copy(content, file)
        }

        header := w.Header()
        header.Add("Content-Type", "text/plain; charset=utf-8")
	    fmt.Fprintf(w, "%d", length)
    })

    http.ListenAndServe("127.0.0.1:3000", nil)
}
