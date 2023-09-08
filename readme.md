Procedure to run streamlit application locally on device using any Code editor like VS Code.


VS Code installation: 
     https://code.visualstudio.com/download

Python installation:
    (Python must be installed on your Laptop for this Purpose .
    If not installed already go to this link : 
                            https://www.python.org/downloads/  
    and click on the download button .

    Then go to the location where Python is installed , probably Program files by Default.

        Go in the Python folder then find "bin" folder else "scripts" folder and then copy path of that folder.
        Then search "Edit the System variables". 
        click on Environment Variables option. 
        Then click on Path option by dragging in System variables option.
        click on New then paste that Path here.

)

1. First of all Download all the required libraries in Code editor (VS Code) in the terminal or CMD . Write following commands one by one:

pip install streamlit
pip install langchain
pip install python-dotenv
pip install openai

2. After installing libraries Use the app.py and api.env file as it is.

3. Then click on the Terminal option from Menu and click on New   Terminal . the  just write "streamlit run app.py" and click enter and the app will run locally on your default browser.

4. Questions list of 27 questions is from Line no. 31 to 56. 

5. First API calling prompt is in line 71

6. Final API call prompt is from line 138 to 164
