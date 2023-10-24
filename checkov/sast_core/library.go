package main

import (
	"C"
	"encoding/json"
	"log"

	sitter "github.com/smacker/go-tree-sitter"
	"github.com/smacker/go-tree-sitter/python"
)

type CheckovDocument struct {
	SourceCodeFile string `json:"source_code_file"`
	SourceCodeDir  string `json:"source_code_dir"`
	PolicyDir      string `json:"policy_dir"`
	PoliciyFile    string `json:"policiy_file"`
	Language       string `json:"language"`
}

var langs = map[string]*sitter.Language{
	"python": python.GetLanguage(),
}

//export analyzeCode
func analyzeCode(documentPtr *C.char) *C.char {
	documentString := C.GoString(documentPtr)
	jsonDocument := CheckovDocument{}
	err := json.Unmarshal([]byte(documentString), &jsonDocument)
	if err != nil {
		log.Fatal(err)
	}
	log.Println(jsonDocument)
	parser := sitter.NewParser()
	parser.SetLanguage(langs[jsonDocument.Language])

	mapD := map[string]int{"matches": 0, "profiler": 0}
	toReturn, _ := json.Marshal(mapD)
	return C.CString(string(toReturn))
}

func main() {
}
