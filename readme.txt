# HOW TO USE 

1. pip install -r requirements.txt
2. To build our index, make sure you have the DEV folder inside our corpus folder and make sure that it is named DEV.
3. Next, you have to write "python launch.py --restart true" in command line.
4. Add your OpenAI API key in the file app.py line 25

After everything is done running, you should see main_index.txt in indexes folder. 

### TO RUN ###

- Make sure that the 'indexes' folder is present and contains the id_index.json, index_of_index.txt, main_index.txt, and so on
- for web client search interface: python app.py
- for terminal search: python search_launch2.py