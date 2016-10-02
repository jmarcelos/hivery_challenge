create: createenv

createenv:
	test -d env_hivery || virtualenv env_hivery
	env_hivery/bin/pip install -Ur requirements.txt
	touch ./env_hivery/bin/activate

creategit:
	echo "# Virtualenv\n.Python\n*.log\n*.ini\n*.pyc\nenv_hivery/\n[Bb]in\n[Ii]nclude\n[Ll]ib\n[Ll]ocal\n# MacOSX\n.DS_Store" >> .gitignore
	git init

scrapy:
	env_hivery/bin/python scrapper/scrapy_runner.py

test:
	env_hivery/bin/python scrapper/coles/spiders/test/tests.py

mac-chrome-drive:
	wget http://chromedriver.storage.googleapis.com/2.24/chromedriver_mac64.zip
	unzip chromedriver_mac64.zip -d scrapper
