from flask import Flask, request, render_template
import retrieval

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('ZotSearchHome.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    page = int(request.args.get('page', 1))  # Get current page number, default to 1
    results_per_page = 10  # Number of results per page

    # Call your retrieval.search() function to get the search results, summary, and speed
    results, summary, speed = retrieval.search(query)

    # Determine the start and end indices of the results to display for the current page
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    # Subset the results based on the current page
    results_subset = results[start_index:end_index]

    # Determine previous and next page URLs
    previous_page = None
    if page > 1:
        previous_page = request.base_url + f"?query={query}&page={page - 1}"

    next_page = None
    if end_index < len(results):
        next_page = request.base_url + f"?query={query}&page={page + 1}"

    return render_template('ZotSearchResult.html', results=results_subset, summary=summary, speed=speed,
                           previous_page=previous_page, next_page=next_page)

if __name__ == '__main__':
    app.run(debug=True)
