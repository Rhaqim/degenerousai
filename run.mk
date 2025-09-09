.PHONY restart-ai-server restart-nginx

restart-ai-server:
	@echo "Restarting FastAPI AI server with Supervisor..."
	supervisorctl reread
	supervisorctl update
	supervisorctl restart fastapi
	@echo "FastAPI AI server restarted."

restart-nginx:
	@echo "Restarting Nginx server..."
# 	sudo systemctl restart nginx
	service nginx restart # Use this line if running on runpod
	@echo "Nginx server restarted."
