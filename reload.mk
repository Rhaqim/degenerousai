.PHONY: restart-ai-server restart-nginx

restart-ai-server:
	@echo "Restarting FastAPI server with Supervisor..."
	supervisorctl reload
	supervisorctl update
	supervisorctl restart degenerousai

restart-nginx:
	@echo "Restarting Nginx server..."
	service nginx restart