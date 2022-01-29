

# Light Controller


## Building

Make sure the install step is done outside of `poetry shell`:

	poetry build
	sudo pip3 install dist/lightcontroller-0.1.0-py3-none-any.whl

# Manage via systemd

	sudo systemctl status lightcontroller-daemon.service
	sudo systemctl start lightcontroller-daemon.service
	sudo systemctl stop lightcontroller-daemon.service
