all: plura-dl README.md README.txt plura-dl.1 plura-dl.bash-completion plura-dl.zsh plura-dl.fish

clean:
	rm -rf plura-dl.1.temp.md plura-dl.1 plura-dl.bash-completion README.txt MANIFEST build/ dist/ .coverage cover/ plura-dl.tar.gz plura-dl.zsh plura-dl.fish plura_dl/extractor/lazy_extractors.py *.dump *.part* *.ytdl *.info.json *.mp4 *.m4a *.flv *.mp3 *.avi *.mkv *.webm *.3gp *.wav *.ape *.swf *.jpg *.png plura-dl plura-dl.exe
	find . -name "*.pyc" -delete
	find . -name "*.class" -delete

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/man
SHAREDIR ?= $(PREFIX)/share
PYTHON ?= /usr/bin/env python

# set SYSCONFDIR to /etc if PREFIX=/usr or PREFIX=/usr/local
SYSCONFDIR = $(shell if [ $(PREFIX) = /usr -o $(PREFIX) = /usr/local ]; then echo /etc; else echo $(PREFIX)/etc; fi)

# set markdown input format to "markdown-smart" for pandoc version 2 and to "markdown" for pandoc prior to version 2
MARKDOWN = $(shell if [ `pandoc -v | head -n1 | cut -d" " -f2 | head -c1` = "2" ]; then echo markdown-smart; else echo markdown; fi)

install: plura-dl plura-dl.1 plura-dl.bash-completion plura-dl.zsh plura-dl.fish
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 plura-dl $(DESTDIR)$(BINDIR)
	install -d $(DESTDIR)$(MANDIR)/man1
	install -m 644 plura-dl.1 $(DESTDIR)$(MANDIR)/man1
	install -d $(DESTDIR)$(SYSCONFDIR)/bash_completion.d
	install -m 644 plura-dl.bash-completion $(DESTDIR)$(SYSCONFDIR)/bash_completion.d/plura-dl
	install -d $(DESTDIR)$(SHAREDIR)/zsh/site-functions
	install -m 644 plura-dl.zsh $(DESTDIR)$(SHAREDIR)/zsh/site-functions/_plura-dl
	install -d $(DESTDIR)$(SYSCONFDIR)/fish/completions
	install -m 644 plura-dl.fish $(DESTDIR)$(SYSCONFDIR)/fish/completions/plura-dl.fish

codetest:
	flake8 .

test:
	#nosetests --with-coverage --cover-package=plura_dl --cover-html --verbose --processes 4 test
	nosetests --verbose test
	$(MAKE) codetest

ot: offlinetest

# Keep this list in sync with devscripts/run_tests.sh
offlinetest: codetest
	$(PYTHON) -m nose --verbose test \
		--exclude test_age_restriction.py \
		--exclude test_download.py \
		--exclude test_iqiyi_sdk_interpreter.py \
		--exclude test_socks.py \
		--exclude test_subtitles.py \
		--exclude test_write_annotations.py \
		--exclude test_youtube_lists.py \
		--exclude test_youtube_signature.py

tar: plura-dl.tar.gz

.PHONY: all clean install test tar bash-completion pypi-files zsh-completion fish-completion ot offlinetest codetest

pypi-files: plura-dl.bash-completion README.txt plura-dl.1 plura-dl.fish

plura-dl: plura_dl/*.py plura_dl/*/*.py
	mkdir -p zip
	for d in plura_dl plura_dl/downloader plura_dl/extractor plura_dl/postprocessor ; do \
	  mkdir -p zip/$$d ;\
	  cp -pPR $$d/*.py zip/$$d/ ;\
	done
	touch -t 200001010101 zip/plura_dl/*.py zip/plura_dl/*/*.py
	mv zip/plura_dl/__main__.py zip/
	cd zip ; zip -q ../plura-dl plura_dl/*.py plura_dl/*/*.py __main__.py
	rm -rf zip
	echo '#!$(PYTHON)' > plura-dl
	cat plura-dl.zip >> plura-dl
	rm plura-dl.zip
	chmod a+x plura-dl

README.txt: README.md
	pandoc -f $(MARKDOWN) -t plain README.md -o README.txt

plura-dl.1: README.md
	$(PYTHON) devscripts/prepare_manpage.py plura-dl.1.temp.md
	pandoc -s -f $(MARKDOWN) -t man plura-dl.1.temp.md -o plura-dl.1
	rm -f plura-dl.1.temp.md

plura-dl.bash-completion: plura_dl/*.py plura_dl/*/*.py devscripts/bash-completion.in
	$(PYTHON) devscripts/bash-completion.py

bash-completion: plura-dl.bash-completion

plura-dl.zsh: plura_dl/*.py plura_dl/*/*.py devscripts/zsh-completion.in
	$(PYTHON) devscripts/zsh-completion.py

zsh-completion: plura-dl.zsh

plura-dl.fish: plura_dl/*.py plura_dl/*/*.py devscripts/fish-completion.in
	$(PYTHON) devscripts/fish-completion.py

fish-completion: plura-dl.fish

lazy-extractors: plura_dl/extractor/lazy_extractors.py

_EXTRACTOR_FILES = $(shell find plura_dl/extractor -iname '*.py' -and -not -iname 'lazy_extractors.py')
plura_dl/extractor/lazy_extractors.py: devscripts/make_lazy_extractors.py devscripts/lazy_load_template.py $(_EXTRACTOR_FILES)
	$(PYTHON) devscripts/make_lazy_extractors.py $@

plura-dl.tar.gz: plura-dl README.md README.txt plura-dl.1 plura-dl.bash-completion plura-dl.zsh plura-dl.fish ChangeLog AUTHORS
	@tar -czf plura-dl.tar.gz --transform "s|^|plura-dl/|" --owner 0 --group 0 \
		--exclude '*.DS_Store' \
		--exclude '*.kate-swp' \
		--exclude '*.pyc' \
		--exclude '*.pyo' \
		--exclude '*~' \
		--exclude '__pycache__' \
		--exclude '.git' \
		--exclude 'docs/_build' \
		-- \
		bin devscripts test plura_dl docs \
		ChangeLog AUTHORS LICENSE README.md README.txt \
		Makefile MANIFEST.in plura-dl.1 plura-dl.bash-completion \
		plura-dl.zsh plura-dl.fish setup.py setup.cfg \
		plura-dl
