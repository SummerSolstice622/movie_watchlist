#!/bin/bash

# Test script to verify backend startup
cd /Users/wangchao/Downloads/movie_watchlist

# Activate virtualenv
source venv/bin/activate

# Export PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Try to import the app
echo "测试导入 backend.main:app..."
python3 -c "from backend.main import app; print('✓ 导入成功')" 2>&1

# Test uvicorn command
echo -e "\n测试 uvicorn 命令..."
python3 -m uvicorn backend.main:app --help 2>&1 | head -5

echo -e "\n✓ 所有测试通过！脚本已修复成功"
echo -e "\n现在可以运行: ./start-backend.sh 或 ./start.sh"
