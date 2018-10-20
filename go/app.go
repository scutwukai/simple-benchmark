package main

import "io"
import "fmt"
import "path"
import "strings"
import "strconv"
import "runtime"
import "net/http"
import "database/sql"

import "github.com/akrennmair/goconf"
import "github.com/go-redis/redis"
import _ "github.com/go-sql-driver/mysql"



func main() {
    fmt.Println("cpus:", runtime.NumCPU())
    fmt.Println("goroot:", runtime.GOROOT())
    fmt.Println("archive:", runtime.GOOS)

    fmt.Println("set max process:", 1)
    runtime.GOMAXPROCS(1)

    rs := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
        Password: "",
        DB: 0,
    })

    c, _ := conf.ReadConfigFile("my.cnf")
    host, _ := c.GetString("client", "host")
    port, _ := c.GetInt("client", "port")
    user, _ := c.GetString("client", "user")
    pwd, _ := c.GetString("client", "password")
    db, _ := c.GetString("client", "db")
    cs, _ := c.GetString("client", "charset")

    dsn := new(strings.Builder)
    fmt.Fprintf(dsn, "%s:%s@tcp(%s:%d)/%s?charset=%s", user, pwd, host, port, db, cs)
    my, _ := sql.Open("mysql", dsn.String())

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

    http.HandleFunc("/redis", func(w http.ResponseWriter, r *http.Request) {
        key := r.FormValue("key")

        rs.Set(key, "hello redis", 0)
        word, _ := rs.Get(key).Result()

        header := w.Header()
        header.Add("Content-Type", "text/plain; charset=utf-8")
	    fmt.Fprintf(w, word)
    })

    http.HandleFunc("/mysql", func(w http.ResponseWriter, r *http.Request) {
        sql := r.FormValue("sql")

        rows, _ := my.Query(sql)
        defer rows.Close()

        rows.Next()
        var value string
        rows.Scan(&value)

        header := w.Header()
        header.Add("Content-Type", "text/plain; charset=utf-8")
	    fmt.Fprintf(w, "%s", value)
    })

    http.ListenAndServe("127.0.0.1:3000", nil)
}
