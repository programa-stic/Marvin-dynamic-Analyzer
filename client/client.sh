adb start-server;
while true; do
	sleep 10;
	python VMClient.py;
done

