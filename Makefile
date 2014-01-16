all: html slides

html:
	asciidoc -a icons -a data-uri -a toc README.asciidoc
	mv README.html index.html


slides: 
	asciidoc -b deckjs README.asciidoc
	mv README.html slides.html



