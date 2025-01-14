# HOW TO USE 

1. pip install -r requirements.txt
2. Download the Developer zip file "[Developer.zip](https://drive.google.com/file/d/1GDDU2OshdlImYM9uMD31_XRj2uWYEySq/view?usp=sharing)" and extract its contents
3. To build our index, make sure you have the DEV folder inside the corpus folder and make sure that it is named DEV
4. Write "python launch.py --restart true" in command line and wait for process to end. After everything is done running, you should see main_index.txt in indexes folder. 
5. Add your OpenAI API key in the file app.py line 25

### TO RUN ###

Make sure that the 'indexes' folder is present and contains the id_index.json, index_of_index.txt, main_index.txt, and so on

#### Web client search interface: python app.py
#### terminal search: python search_launch2.py