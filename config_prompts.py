import uuid

class ConfigPrompt:

    def __init__(self, csv_path, images_folder, plot_words_dict):
        self.dataframe_features_info = None
        self.summarise_prompt = None
        self.summarise_system_prompt = None
        self.instructions_output = None
        self.csv_path=csv_path
        self.images_folder = images_folder
        self.personalize = False
        self.explain_system_prompt = None
        self.sql_system_prompt = None
        self.plot_words_dict = plot_words_dict
        self.initialize()

    def initialize(self,):
        self.dataframe_features_info = self.get_dataframe_features_info()
        self.summarise_system_prompt = self.get_base_summarise_system_prompt()
        self.instructions_output = self.get_instructions_output_prompt()
        self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, self.instructions_output)
        self.summarise_prompt_direct_plot = self.get_base_summarise_with_plot_system_prompt()
        self.sql_system_prompt = self.get_base_sql_system_prompt()
        self.explain_system_prompt = self.get_base_explain_system_prompt()

    def update_summary_personal_instructions(self, personalize, personal_information):
        self.personalize = personalize
        if self.personalize:
            self.instructions_output = self.get_instructions_output_prompt(personal_information = personal_information)
            self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, self.instructions_output)
        else:
            self.instructions_output = self.get_instructions_output_prompt()
            self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, self.instructions_output)

    def update_output_instructions_and_personal_information(self, instructions_output, personalize, personal_information):
        self.personalize = personalize
        if self.personalize:
            self.instructions_output = self.get_instructions_output_prompt(personal_information = personal_information, context_prompt=instructions_output)
            self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, self.instructions_output)
        else:
            self.instructions_output = self.get_instructions_output_prompt(context_prompt=instructions_output)
            self.summarise_prompt = self.prepare_system_prompt(self.summarise_system_prompt, self.instructions_output)
        
    def get_instructions_output_prompt(self, personal_information = "", context_prompt = ""):
        """
        Please only add instructions that refines the answer. (Do not add instructions that require additional code generation)
        """

        output_format = """
Output format (Return a JSON object as follows):
{
"summary" : ```Summary of the output based on the above mentioned points. (Remember to bold out words in summary)```
"insight" : ```A compelling insight is related to the question asked, but can use all other variables in the data. (Remember to bold out words in insight)```
"next_questions" : ```List of 3 next most relevant questions to ask based on the question asked.```
}
"""
        if context_prompt == "":
            context_prompt = """
Please consider the following points for summarizing the output:
- The answers you provide should be concise, but also give explanation and elaborate on why the answers are so.
- The answers you provide should give a good narrative.
- Ensure you are specific with the analysis. For example, Instead of just saying improved, ensure you specify the percentage by which it improved by.
- When referring to the volume metrics, ensure you are mostly communicating percentages as opposed to the volume number.
- Ensure that the narrative is easy for the marketer to understand
- Ensure that you are providing actionable insights
- When you find that there are bottlenecks or areas for improvement as suggested by the data, dig deeper into the other data variables to provide more explanation or reason behind the bottleneck. For example, if you find that there is a peak of MQLs that were not dispositioned in a specific time frame, look into the buyer segment variable to find which buyer segment was driving the peak. Look into other variables as well.
- You should always provide another compelling insight that is related to the question asked, but uses other variables in the dataset. This insight should come after the first narrative.

"""     
        personal_information = f"""You are provided with the Personal Information / Objectives and Key Results (OKRs) about end-user. 
You need to use the following personal information / OKRs to phrase the summary.

{personal_information}

"""
        if self.personalize:
            return f"{context_prompt}\n{personal_information}\n{output_format}"

        return f"{context_prompt}\n{output_format}"



    def prepare_system_prompt(self, summarise_system_prompt, instructions_output):
        return f"{summarise_system_prompt}\n\n{instructions_output}"

    def get_base_sql_system_prompt(self,):
        return f"""You are a data science assistant. You will be provided with python code.
You need to convert the queries executed in the python code to SQL queries.
You can ignore data loading to dataframe, and consider loading a table "MQL" instead.
You need to understand that this SQL code is just to show the non-technical people queries being executed on "MQL" table.
Make sure there are no comments or explaination in the SQL code. 
"""




# Python code uses the followind data.
# ---
# {self.dataframe_features_info}
# ---

    def get_base_explain_system_prompt(self,):
        return f"""You are a data science assistant. You will be provided with python code that answers a specific question.
You will need to explain the python code step by step for understanding of non-technical people.
Do not mention the word "Python Code" in the explaination, instead use "Code".
"""



    def get_base_summarise_system_prompt(self,):
        return f"""You are an assistant for summarising output from a python code.
We had a generated python code to answer a question and we grabbed the output from that code to summarise it.

The code can print calculations with descriptions.
You need to provide a concise summary of the output, If the output includes any numbers, make sure to summarise them.
Try to make the output in nice looking format, but be as concise as possible. 
Do not, add full form of abbreviations in the summary.
Make sure, output is well structured and lines are properly separated.

Make sure to bold out some important words / numbers / percentages. 
You can use html bold tag for example <b>word</b>.

```
**MAKE SURE TO NOT MENTION ANYTHING ABOUT CODE. 
**MAKE SURE TO NOT MENTION ANYTHING ABOUT OUTPUT. 
**Instead phrase it like 'Based on the Analysis,`
**Phrase it like you did some analysis for the question asked and you are answer that. So do not mention about Code or Output, instead you can say `Based on the Analysis,`.
```

"""

    def get_base_summarise_with_plot_system_prompt(self,):
        return """You are an assistant to help in suggesting next questions to ask.
You need to analyze the question, and suggest questions in the following format.


Output format (Return a JSON object as follows):
{
"next_questions" : ```List of 3 next most relevant questions to ask based on the question asked.```
}
"""
    def get_dataframe_features_info(self,):
        return """Data Explaination Format is as follows:
~ Column Name: [`Data Type`] ~ [If categorical then unique values] ~ [`description`]

The dataframe `df` has the following Categorical columns:

    ~ MQL_Status: [Categorical] ~ [Dispositioned in SLA/Dispositioned out of SLA/Not Dispositioned (Auto Closed)/Still in New - Past 48 hours SLA/Still in New - Within 48 hours SLA] ~ [Description: Represents Status of MQL, to help marketers understand the status of Marketing Qualified Leads (MQL)]
    
    ~ SLA_Status: [Categorical] ~ [Accepted/Rejected/Missing SLA Status] ~ [Description: Represents if MQL Dispositioned in Service Level Agreement (SLA) is Accepted or Rejected.]
    
    ~ SLA_Offer: [Categorical] ~ [LTO/ATO/Missing SLA Offer] ~ [Description: Represents if we made Last Time Offer (LTO) or All Time Offer (ATO) to the Accepted SLA.]
    
    ~ MQL_Priority: [Categorical] ~ [B1/B2] ~ [Description: Represents priority status of MQL if its is B1 or B2]
    
    ~ MQL_Routing_Teams: [Categorical] ~ [BDR/FSR/Specialist/Partner/Unknown/Other] ~ [Description: Represents the team where this MQL is assigned]
    
    ~ MQL_Buyer_Segment: [Categorical] ~ [CxO-Chief/CxO-VP/Director/CxO-Others/ITDM/Other/Practioner] ~ [Description: Represents the buyer segment for the MQL]
    
    ~ MQL_Score_Priority: [Categorical] ~ [A1/A2/A3] ~ [Description: Represents the Priority Score of MQL]

The dataframe `df` has the following Date columns:

    ~ Date: [date, format: yyyy/mm/dd] ~ [] ~ []
"""

    def get_code_prompt(self, question):
        
        plot_check = False
        for each_word in self.plot_words_dict:
            if each_word in question.lower():
                plot_check = True

        if plot_check:
            unique_filename = str(uuid.uuid4())
            return self.plot_based_prompt(question, unique_filename), unique_filename
        else:
            return self.code_based_prompt(question), None

    def plot_based_prompt(self, question, unique_filename):
        
        return f"""You are a Sales and Marketing Data Science Assistant which has access to dataset "{self.csv_path}".
---
{self.dataframe_features_info}
---

As you are working on marketing data, you might need to know about some marketing terms like SAL (Sales Accepted Lead) and other terms as well.

Follow the steps below to write python code to answer the question that will be asked for the dataset:

**1. Imports**:
   - Make sure to have all imports required for the code like import pandas as pd, import numpy as np, sciket-learn or matplotlib

**2. Print Statement**:
   - Make sure, to print the answer to the question asked.

**3. Plot (If asked)**:
   - Make sure, to save the plot image as "{self.images_folder}{unique_filename}.png".
   - Make sure to use blue color palette and make the palette range beautiful. 
   - Mak sure the plot title follows good Data Storytelling convention.
   - Make sure to rotate the xticks of the plot to adjust text in the image. One of the way is to use something like plt.xticks(rotation = 70)
   - Make sure to do the following to fit everythin with in the figure. plt.tight_layout()

**4. Output**:
   - Clearly print the results, rounding off values to 3 decimals. Ensure the printed output has meaningful explanations to aid in summarizing the final answer.


The assistant's response must contain the Python code that makes the above steps.
Python```
your code here
```
The assistant's Response should be only the code without any explanations. 

"""

    def code_based_prompt(self, question):
        
        return f"""You are a Sales and Marketing Data Science Assistant which has access to dataset "{self.csv_path}".
---
{self.dataframe_features_info}
---

As you are working on marketing data, you might need to know about some marketing terms like SAL (Sales Accepted Lead) and other terms as well.

Follow the steps below to write python code to answer the question that will be asked for the dataset:

**1. Imports**:
   - Make sure to have all imports required for the code like import pandas as pd, import numpy as np, sciket-learn etc.

**2. Print Statement**:
   - Make sure, to print the answer to the question asked.

**3. Output**:
   - Clearly print the results, rounding off values to 3 decimals. Ensure the printed output has meaningful explanations to aid in summarizing the final answer.


The assistant's response must contain the Python code that makes the above steps.
Python```
your code here
```
The assistant's Response should be only the code without any explanations. 

"""



    def insight_based_prompt(self):
        unique_filename = str(uuid.uuid4())
        
        return f"""You are a Sales and Marketing Data Science Assistant which has access to dataset "{self.csv_path}".
---
{self.dataframe_features_info}
---

As you are working on marketing data, you might need to know about some marketing terms like SAL (Sales Accepted Lead) and other terms as well.

You will be provided with an insight about the data, you need to write python code that will generate a plot related to that insight.
Follow the steps below to write python code to generate the plot based on the insight that will be provided:

**1. Imports**:
   - Make sure to have all imports required for the code like import pandas as pd, import numpy as np, sciket-learn or matplotlib

**2. Plot**:
   - Make sure, to save the plot image as "{self.images_folder}{unique_filename}.png".
   - Make sure to use the following color palette (available in hex code).
   - palette = ["#eb4336", "#fbbd04", "#34a853", "#4385f4", "#9aa0a6"]
   - Make sure to rotate the xticks of the plot to adjust text in the image. One of the way is to use something like plt.xticks(rotation = 70)
   - Make sure to do the following to fit everythin with in the figure. plt.tight_layout()

**3. Do not print any output**:


The assistant's response must contain the Python code that makes the above steps.
Python```
your code here
```
The assistant's Response should be only the code without any explanations. 

""", unique_filename
