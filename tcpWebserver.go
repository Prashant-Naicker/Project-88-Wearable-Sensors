package main

import (
    "fmt"
    "net"
    "encoding/binary"
)

func main() {
    l, err := net.Listen("tcp", ":8081")
    if err != nil { fmt.Printf("%v", err); return }
    fmt.Println("#############################################################")
    fmt.Println("Server is running...")
    for {
        conn, err := l.Accept()
        if err != nil { fmt.Printf("%v", err); continue }

        go handleConnection(conn)
    }
}

func handleConnection(conn net.Conn) {
    fmt.Println("Connected!")

    for {
        sizeBytes, err := awaitData(conn, 2)
        if (err != nil) { fmt.Println("Disconnected"); return }

        size := binary.LittleEndian.Uint16(sizeBytes)
        data, err := awaitData(conn, int(size))
        if (err != nil) { fmt.Println("Disconnected"); return }

        fmt.Printf("> %v\n", string(data))
    }
}

func awaitData(conn net.Conn, totalSize int) ([]byte, error) {
    buffer := make([]byte, totalSize)
    readSize := 0

    for (readSize < totalSize) {
        length, err := conn.Read(buffer[readSize:]) //Read method stores bytes being read into the buffer and returns the length of bytes read.
        if err != nil { return nil, err }

        readSize += length
    }

    return buffer, nil
}

func sendData(conn net.Conn, message []byte) error {
    var dataLength = len(message)
    var dataLengthRaw = []byte {0, 0}

    dataLengthRaw[0] = byte(dataLength << 8 >> 8)
    dataLengthRaw[1] = byte(dataLength >> 8)

    _, err := conn.Write(dataLengthRaw)
    _, err = conn.Write(message)

    return err
}
