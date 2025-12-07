#!/bin/bash

uvx --from=fonttools --with=brotli pyftsubset \
	"./IBMPlexSans-VariableFont.ttf" \
	--unicodes-file=./unicode-ranges.txt \
	--layout-features="*" \
	--flavor="woff2" \
	--output-file="../src/fonts/ibm-plex-sans-variable.woff2"
