fmt:
	isort api
	black api -l 70 -t py310

	isort scripts
	black scripts -l 70 -t py310