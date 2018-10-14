// Taken from https://gist.github.com/paulsmith/775764#file-echo-go

package main

import (
	"fmt"
	"net"
	"strconv"
    "runtime"
)

const PORT = 3000

func main() {
    fmt.Println("cpus:", runtime.NumCPU())
    fmt.Println("goroot:", runtime.GOROOT())
    fmt.Println("archive:", runtime.GOOS)

    fmt.Println("set max process:", 1)
    runtime.GOMAXPROCS(1)

	server, err := net.Listen("tcp", ":"+strconv.Itoa(PORT))
	if server == nil {
		panic("couldn't start listening: " + err.Error())
	}
	i := 0
	for {
		client, err := server.Accept()
		if client == nil {
			fmt.Printf("couldn't accept: " + err.Error())
			continue
		}
		i++
		fmt.Printf("%d: %v <-> %v\n", i, client.LocalAddr(), client.RemoteAddr())
		go handleConn(client)
	}
}

func handleConn(client net.Conn) {
    defer client.Close()
	buf := make([]byte, 102400)
	for {
		reqLen, err := client.Read(buf)
		if err != nil {
			break
		}
		if reqLen > 0 {
			client.Write(buf[:reqLen])
		}
	}
}
