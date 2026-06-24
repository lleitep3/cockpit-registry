package main

import (
	"bytes"
	"fmt"
	"html/template"
	"io"
	"os"
	"path/filepath"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/renderer/html"
	"gopkg.in/yaml.v3"
)

type ArticleDef struct {
	ID          string `yaml:"id"`
	Title       string   `yaml:"title"`
	Description string   `yaml:"description"`
	File        string   `yaml:"file"`
	ReadingTime string   `yaml:"reading_time"`
	Tags        []string `yaml:"tags"`
}

type Config struct {
	CourseTitle      string       `yaml:"course_title"`
	OutputDir        string       `yaml:"output_dir"`
	IntroductionFile string       `yaml:"introduction_file"`
	Articles         []ArticleDef `yaml:"articles"`
}

type RenderArticle struct {
	ID          string
	Title       string
	Description string
	ReadingTime string
	Tags        []string
	ContentHTML template.HTML
	PrevID      string
	PrevTitle   string
	NextID      string
	NextTitle   string
	Index       int
	Total       int
}

type IndexData struct {
	CourseTitle      string
	IntroductionHTML template.HTML
	Articles         []RenderArticle
}

type ArticleData struct {
	CourseTitle string
	Article     RenderArticle
	AllArticles []RenderArticle
}

func main() {
	if len(os.Args) < 3 || os.Args[1] != "build" {
		fmt.Println("Usage: article build <content-file.yml>")
		os.Exit(1)
	}

	configFile := os.Args[2]

	data, err := os.ReadFile(configFile)
	if err != nil {
		fmt.Printf("Error reading config file: %v\n", err)
		os.Exit(1)
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		fmt.Printf("Error parsing YAML: %v\n", err)
		os.Exit(1)
	}

	mdParser := goldmark.New(
		goldmark.WithExtensions(extension.GFM, extension.Typographer),
		goldmark.WithParserOptions(parser.WithAutoHeadingID()),
		goldmark.WithRendererOptions(html.WithHardWraps(), html.WithXHTML()),
	)

	execPath, err := os.Executable()
	if err != nil {
		fmt.Printf("Error getting executable path: %v\n", err)
		os.Exit(1)
	}

	baseDir := filepath.Dir(filepath.Dir(execPath))
	indexPath := filepath.Join(baseDir, "assets", "course_index.html")
	articlePath := filepath.Join(baseDir, "assets", "article_page.html")

	tmplIndex, err := template.New(filepath.Base(indexPath)).Funcs(template.FuncMap{
		"inc": func(i int) int { return i + 1 },
	}).ParseFiles(indexPath)
	if err != nil {
		fmt.Printf("Error parsing template %s: %v\n", indexPath, err)
		os.Exit(1)
	}

	tmplArticle, err := template.New(filepath.Base(articlePath)).Funcs(template.FuncMap{
		"inc": func(i int) int { return i + 1 },
	}).ParseFiles(articlePath)
	if err != nil {
		fmt.Printf("Error parsing template %s: %v\n", articlePath, err)
		os.Exit(1)
	}

	configDir := filepath.Dir(configFile)

	var renderArticles []RenderArticle
	for i, artDef := range cfg.Articles {
		mdPath := artDef.File
		if !filepath.IsAbs(mdPath) {
			mdPath = filepath.Join(configDir, mdPath)
		}

		mdData, err := os.ReadFile(mdPath)
		if err != nil {
			fmt.Printf("Error reading markdown file %s: %v\n", mdPath, err)
			continue
		}

		var buf bytes.Buffer
		if err := mdParser.Convert(mdData, &buf); err != nil {
			fmt.Printf("Error converting markdown %s: %v\n", mdPath, err)
			continue
		}

		htmlContent := buf.String()

		art := RenderArticle{
			ID:          artDef.ID,
			Title:       artDef.Title,
			Description: artDef.Description,
			ReadingTime: artDef.ReadingTime,
			Tags:        artDef.Tags,
			ContentHTML: template.HTML(htmlContent),
			Index:       i + 1,
			Total:       len(cfg.Articles),
		}

		if i > 0 {
			art.PrevID = cfg.Articles[i-1].ID
			art.PrevTitle = cfg.Articles[i-1].Title
		}
		if i < len(cfg.Articles)-1 {
			art.NextID = cfg.Articles[i+1].ID
			art.NextTitle = cfg.Articles[i+1].Title
		}

		renderArticles = append(renderArticles, art)
	}

	outDir := cfg.OutputDir
	if !filepath.IsAbs(outDir) {
		outDir = filepath.Join(configDir, outDir)
	}

	if err := os.MkdirAll(outDir, 0755); err != nil {
		fmt.Printf("Error creating output dir: %v\n", err)
		os.Exit(1)
	}

	copyDir(filepath.Join(baseDir, "assets", "styles"), filepath.Join(outDir, "styles"))
	copyDir(filepath.Join(baseDir, "assets", "scripts"), filepath.Join(outDir, "scripts"))

	// Read and parse Introduction
	var introHTML template.HTML
	if cfg.IntroductionFile != "" {
		introPath := filepath.Join(configDir, cfg.IntroductionFile)
		introContent, err := os.ReadFile(introPath)
		if err == nil {
			var introBuf bytes.Buffer
			if err := mdParser.Convert(introContent, &introBuf); err == nil {
				introHTML = template.HTML(introBuf.String())
			}
		}
	}

	// Generate Index
	indexData := IndexData{
		CourseTitle:      cfg.CourseTitle,
		IntroductionHTML: introHTML,
		Articles:         renderArticles,
	}

	outHTMLPath := filepath.Join(outDir, "index.html")
	outf, err := os.Create(outHTMLPath)
	if err != nil {
		fmt.Printf("Error creating output file: %v\n", err)
		os.Exit(1)
	}
	defer outf.Close()

	if err := tmplIndex.Execute(outf, indexData); err != nil {
		fmt.Printf("Error executing template: %v\n", err)
		os.Exit(1)
	}

	// Generate Article Pages
	for _, art := range renderArticles {
		artData := ArticleData{
			CourseTitle: cfg.CourseTitle,
			Article:     art,
			AllArticles: renderArticles,
		}

		artPath := filepath.Join(outDir, art.ID+".html")
		af, err := os.Create(artPath)
		if err != nil {
			fmt.Printf("Error creating article file: %v\n", err)
			continue
		}

		if err := tmplArticle.Execute(af, artData); err != nil {
			fmt.Printf("Error executing template: %v\n", err)
		}
		af.Close()
	}

	fmt.Printf("Successfully generated multi-page course at %s\n", outDir)
}

func copyDir(src, dst string) error {
	return filepath.Walk(src, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		relPath, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		dstPath := filepath.Join(dst, relPath)
		if info.IsDir() {
			return os.MkdirAll(dstPath, info.Mode())
		}
		
		srcf, err := os.Open(path)
		if err != nil {
			return err
		}
		defer srcf.Close()
		
		dstf, err := os.OpenFile(dstPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, info.Mode())
		if err != nil {
			return err
		}
		defer dstf.Close()
		
		_, err = io.Copy(dstf, srcf)
		return err
	})
}
