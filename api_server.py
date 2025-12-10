from flask import Flask, jsonify
from modules import data, stats

app = Flask(__name__)

@app.route('/api/products', methods=['GET'])
def api_products():
    return jsonify(data.get_products())

@app.route('/api/stats', methods=['GET'])
def api_stats():
    prods = data.get_products()
    return jsonify(stats.calculate_stats(prods))

if __name__ == '__main__':
    print("API REST lancée sur http://127.0.0.1:5000")
    print("Gardez cette fenêtre ouverte pour que l'API fonctionne.")
    app.run(port=5000)
