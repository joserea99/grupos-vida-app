# Actualizar run.py
cat > run.py << 'EOF'
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Para desarrollo local
    app.run(debug=True, host="127.0.0.1", port=5001)
else:
    # Para producción (Railway)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
EOF