# HOW TO USE 

1. pip install -r requirements.txt
2. To build our index, make sure you have the DEV folder inside our corpus folder and make sure that it is named DEV.
3. Next, you have to write "python launch.py --restart true" in command line.
4. Add your OpenAI API key in the file app.py line 25

After everything is done running and you see main_index.txt in indexes folder. 

### TO RUN ###
# Make sure that the 'indexes' folder is present and contains the id_index.json, index_of_index.txt, main_index.txt, and so on
# for web client search interface: python app.py
# for terminal search: python search_launch2.py


# TEST QUERIES
1. Cybersecurity
2. Hackathon
3. Cs122a
4. Software Engineering
5. Master of Software Engineering
6. Professors in Computer Science
7. Girls who code
8. Honors Program
9. Cybersecurity
10. Computer science research
11. Computer networks
12. information retrieval
13. database management systems
14. virtual reality
15. app development
16. data science internships
17. Informatics 
18. Computer science research
19. Mixer at UCI
20. Computer science and data science

Queries from 10-20 were showing very off results at first. We realized it was because we were taking into consideration important text and pagerank.
Because of this, we decided to implement important text like h1, strong, tile, as well as, Page Rank and HITS. Additionally, some of the queries from 10-15 
were really bad in terms of performance. To fix this, we implemented a index of index look up for our main index and sorted our posting lists such that 
we look at the posting with fewests postings first and used that in order to remove as many irrelavant pages as possible in the first iteration. 