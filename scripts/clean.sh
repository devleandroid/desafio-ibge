#!/bin/bash
# Limpa arquivos temporários

echo "🧹 Limpando arquivos temporários..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.log" -delete

echo "✅ Limpeza concluída!"
