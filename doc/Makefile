BROWSER=google-chrome

run:  doc
	$(BROWSER) README.html
doc: clean doxygen ascii
	echo "generating doc"
	
clean:
	rm -fr README.html
	rm -fr html

doxygen:
	doxygen Doxyfile
ascii:
	asciidoc -a icons -a data-uri -a toc README.asciidoc
runascii: ascii
	$(BROWSER) README.html
