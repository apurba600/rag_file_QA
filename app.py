from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from reliable_rag import encode_pdf, get_retriever
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

app = Flask(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variable to store the QA chain
qa_chain = None

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global qa_chain
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Save the file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Process the PDF and create QA chain
            vectorstore = encode_pdf(filepath)
            retriever = get_retriever(vectorstore)
            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0),
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'redirect': url_for('qa_page')
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/qa')
def qa_page():
    return render_template('qa.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    global qa_chain
    
    if not qa_chain:
        return jsonify({'error': 'No document has been uploaded yet'}), 400
    
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        result = qa_chain({"query": question})
        return jsonify({
            'answer': result['result'],
            'sources': [doc.metadata for doc in result.get('source_documents', [])]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
