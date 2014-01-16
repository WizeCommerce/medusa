ICONURL= /usr/share/doc/asciidoc/doc/images/icons
all: html slides
EDITOR=vim

html:
	asciidoc -a icons -a iconsdir=$(ICONURL) -a data-uri -a toc README.asciidoc
	mv README.html index.html

edit:
	echo "You're a lazy bum.  This is not what makefiles were designed for"
	$(EDITOR) README.asciidoc


slides: 
	asciidoc -b deckjs README.asciidoc
	mv README.html slides.html



