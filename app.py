from flask import Flask, request, render_template, jsonify
from search2 import SearchEngine  # switched to search2
from configparser import ConfigParser, ExtendedInterpolation
from utils.config import Config
from utils import get_logger
import time
import openai


app = Flask(__name__)

# Initialize logging
logger = get_logger("Engine")

# Setup configuration using ConfigParser
cparser = ConfigParser(interpolation=ExtendedInterpolation())
cparser.read("config.ini")
config = Config(cparser, False)

# Initialize SearchEngine with the loaded index and ID-to-URL mapping
search_engine = SearchEngine(config, logger, 15)


# Correctly initialize OpenAI with the API key
openai.api_key = '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'

@app.route('/summarize', methods=['POST'])
def summarize():
    content = request.json.get('content')

    # Default summary message in case of an error
    default_summary = "Expected summary - Unable to fetch."

    try:
        summary = generate_summary_with_openai(content)
        return jsonify({'summary': summary})
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Failed to generate summary: {e}")
        # Return the default summary message
        return jsonify({'summary': default_summary})


## https://platform.openai.com/docs/deprecations
    ## https://platform.openai.com/docs/api-reference/models
def generate_summary_with_openai(content):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Specify the model 
            prompt=f"Summarize this text in 50 words: {content}",
            max_tokens=100,  # Adjust accordingly
            temperature=0.5,  # Adjust creativity of the response
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        # Extract summary text from the API response
        summary = response.choices[0].text.strip()
        return summary
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return "Summary generation failed."




@app.route('/', methods=['GET', 'POST'])
def home():
    # Get the query parameter from the request
    query = request.args.get('query', '')
    results = []
    query_time = 0
    summaries = []  # Placeholder for summaries

    if query:
        start_time = time.time()
        results = search_engine.search(query)[:5]  # return top 5 results
        end_time = time.time()
        query_time = (end_time - start_time) * 1000  # time of response in milliseconds

        # Placeholder for summarization
        # for result in results:
        #     #summarization code
        #     pass

    #return render_template('index.html', query=query, results=results, query_time=query_time)
    return render_template('index.html', query=query, results=results, query_time=query_time, summaries=summaries)

if __name__ == "__main__":
    app.run(debug=True)  #