fmt:
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive api
	isort api
	black api -l 70 -t py310

	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive scripts
	isort scripts
	black scripts -l 70 -t py310

	
