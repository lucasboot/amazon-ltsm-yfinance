.PHONY: help install run test clean deploy

help:
	@echo "🚀 Amazon LSTM API - Comandos disponíveis:"
	@echo ""
	@echo "  make install    - Instala dependências"
	@echo "  make run        - Executa a API localmente"
	@echo "  make test       - Executa testes"
	@echo "  make test-local - Testa API local com script"
	@echo "  make clean      - Remove arquivos temporários"
	@echo "  make deploy     - Deploy na Vercel"
	@echo "  make check      - Verifica estrutura do projeto"
	@echo ""

install:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt
	@echo "✅ Dependências instaladas!"

run:
	@echo "🚀 Iniciando API..."
	uvicorn api.index:app --reload

test:
	@echo "🧪 Executando testes..."
	pytest tests/test_api.py -v

test-local:
	@echo "🧪 Testando API local..."
	python scripts/test_local.py

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Limpeza concluída!"

deploy:
	@echo "🚀 Deploy na Vercel..."
	vercel --prod

check:
	@echo "🔍 Verificando estrutura do projeto..."
	@echo ""
	@echo "📁 Pastas:"
	@ls -d api/ app/ artifacts/ tests/ scripts/ 2>/dev/null || echo "  ⚠️  Alguma pasta está faltando!"
	@echo ""
	@echo "📄 Arquivos importantes:"
	@ls requirements.txt vercel.json README.md 2>/dev/null || echo "  ⚠️  Algum arquivo está faltando!"
	@echo ""
	@echo "🤖 Artefatos do modelo:"
	@if [ -f "artifacts/amzn_lstm_model.keras" ]; then \
		echo "  ✅ amzn_lstm_model.keras encontrado"; \
	else \
		echo "  ❌ amzn_lstm_model.keras NÃO encontrado!"; \
	fi
	@if [ -f "artifacts/scaler.save" ]; then \
		echo "  ✅ scaler.save encontrado"; \
	else \
		echo "  ❌ scaler.save NÃO encontrado!"; \
	fi
	@echo ""
	@echo "🐍 Python:"
	@python --version || echo "  ⚠️  Python não encontrado!"
	@echo ""

