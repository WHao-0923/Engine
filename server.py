from flask import Flask, request, render_template
import retrieval

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('ZotSearchHome.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    results,summary,speed = retrieval.search(query)
    return render_template('ZotSearchResult.html', results=results, summary=summary, speed=speed)

if __name__ == '__main__':
    app.run(debug=True)
