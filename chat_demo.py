import os
import openai
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from joblib import Parallel, delayed
from time import time
import cv2
from code_executor import CodeExecutor, CodeExecutionStatus
from config_prompts import ConfigPrompt

class DemoGoogle:
    def __init__(self, csv_path, images_folder, plot_words_dict, api_key = None):
        if api_key:
            openai.api_key = api_key
        self.csv_path = csv_path
        self.images_folder = images_folder
        self.version = "Demo Version"
        self.CodeExecutor = CodeExecutor()
        self.ConfigPrompt = None
        self.plot_words_dict = plot_words_dict
        self.initialize_config(self.csv_path, self.images_folder, self.plot_words_dict)

    def initialize_config(self, csv_path, images_folder, plot_words_dict):
        self.ConfigPrompt = ConfigPrompt(csv_path=csv_path, images_folder=images_folder, plot_words_dict=plot_words_dict)

    def prepare_insight_question(self, insight):
        insight_prompt, filename = self.ConfigPrompt.insight_based_prompt()
        messages = [{"role": "system", "content": insight_prompt}] + [
                    {"role": "user", "content": f"Insight: {insight}"}]
        return messages, filename

    def prepare_question(self, question):
        question_prompt, filename = self.ConfigPrompt.get_code_prompt(question)
        messages = [{"role": "system", "content": question_prompt}] + [
                    {"role": "user", "content": f"Question: {question}"}]
        return messages, filename

    def prepare_python_to_sql(self, python_code):
        python_to_sql_prompt = self.ConfigPrompt.sql_system_prompt
        messages = [{"role": "system", "content": python_to_sql_prompt}] + [
                    {"role": "user", "content": f"Python Code: {python_code}"}]
        return messages

    def prepare_python_explain(self, python_code):
        python_explain_prompt = self.ConfigPrompt.explain_system_prompt
        messages = [{"role": "system", "content": python_explain_prompt}] + [
                    {"role": "user", "content": f"Python Code: {python_code}"}]
        return messages

    def prepare_summary(self, question, output, direct_plot):
        if direct_plot:
            messages = [{"role": "system", "content": self.ConfigPrompt.summarise_prompt_direct_plot}] + [
                            {"role": "user", "content": f"Question: [{question}]"}]
        else:
            messages = [{"role": "system", "content": self.ConfigPrompt.summarise_prompt}] + [
                        {"role": "user", "content": f"Question: [{question}], Code output: [{output}]."}]
        return messages
    
    def execute_prompt(self, prompt):
        completion = openai.ChatCompletion.create(model="gpt-4", temperature=0, messages=prompt)
        response = completion.choices[0].message.content
        return response

    def get_summary(self, question, code_output, direct_plot):
        question = self.prepare_summary(question, code_output, direct_plot)
        return self.execute_prompt(question)

    def get_exe_output(self, question):
        # time_sec = time() 
        response = self.execute_prompt(question)
        # print ("GPT-4 Response", time() - time_sec)
        # time_sec = time() 
        output = self.CodeExecutor.execute(response)
        # print ("Executed Code", time() - time_sec)
        status = output["status"]
        output = output["output"]
        return response, status, output

    def get_output(self, question, n=5):
        for i in range(0, n):
            response, status, output = self.get_exe_output(question)
            if status == CodeExecutionStatus.SUCCESS:
                return response, status, output
        return response, status, output

    def clear_plot(self, unique_filename):
        if os.path.isfile(unique_filename):
            os.remove(unique_filename)

    def parse_summary_direct_plot_output(self, output):
        next_questions = ["What was the conversion rate of MQLs to SALs in the ITDM segment last quarter?", "What marketing strategies were used to engage the ITDM segment last quarter?", "How does the performance of the ITDM segment compare to other segments in the same period?"]
        output = eval(output)
        isDictionary = type(output) == dict
        if "next_questions" in output.keys():
            try:
                next_questions = eval(output["next_questions"])
            except:
                next_questions = output["next_questions"]
        
        return "", "", next_questions

    def parse_summary_output(self, output):
        insight = "This insight suggests that our marketing strategies and campaigns are resonating well with the ITDM segment. Therefore, we should continue to tailor our marketing initiatives to cater to this segment's needs and preferences to maintain or even increase their engagement level."
        next_questions = ["What was the conversion rate of MQLs to SALs in the ITDM segment last quarter?", "What marketing strategies were used to engage the ITDM segment last quarter?", "How does the performance of the ITDM segment compare to other segments in the same period?"]
        summary = ""
        
        output = eval(output)
        isDictionary = type(output) == dict
        if isDictionary:
            if "summary" in output.keys():
                summary = output["summary"]
            if "insight" in output.keys():
                insight = output["insight"]
            if "next_questions" in output.keys():
                try:
                    next_questions = eval(output["next_questions"])
                except:
                    next_questions = output["next_questions"]
        else:
            summary = str(output)
        
        return summary, insight, next_questions
            
    def check_if_direct_plot_created(self, filename):
        if filename and os.path.isfile(f"{self.images_folder}{filename}.png"):
            return True
        return False

    def refine_summary_based_on_plot_output(self, summary, code, insight, output, direct_plot):
        if output:
            if direct_plot:
                return None, False, code, None
            if (output == ""):
                return """Question might be too broad or not phrased correctly. 
    Please rephrase the question and ask again.""", False, None, None
            if ("error" in output.lower()) or ("error" in summary.lower()):
                return None, False, None, None
            return summary, True, code, insight
        return None, False, None, None

    def process_output(self, question, filename, response, status, output):
        if status == CodeExecutionStatus.SUCCESS:
            direct_plot = self.check_if_direct_plot_created(filename)
            if direct_plot:
                filename = f"{filename}.png"

            summary = self.get_summary(question, output, direct_plot)
            if direct_plot:
                summary, insight, next_questions = self.parse_summary_direct_plot_output(summary)
            else:
                summary, insight, next_questions = self.parse_summary_output(summary)
            return summary, insight, next_questions, filename, direct_plot, output

        return "", "", [], None, False, ""

    def chat_stage_1(self, question):
        # time_sec = time() 
        _question, filename = self.prepare_question(question)
        # print ("Prepare Que", time() - time_sec)
        # print (_question)
        response, status, output = self.get_output(_question)
        # print (response)
        # print (status)
        # print (output)
        # time_sec = time()
        summary, insight, next_questions, filename, direct_plot, output = self.process_output(question, filename, response, status, output)
        # print ("Process Answer in Summary", time() - time_sec)
        summary, isInsight, response, insight = self.refine_summary_based_on_plot_output(summary, response, insight, output, direct_plot)
        
        if filename:
            if summary:
                summary = summary
            else:
                summary = "Here is the plot you inquired about."

        output_stage_1 = {
        "question" : question,
        "status" : status,
        "code" : response,
        "code_print_output" : output,
        "direct_plot" : direct_plot,
        "filename" : filename,
        "summary" : summary,
        "insight" : insight,
        "isInsight" : isInsight,
        "next_questions" : next_questions,
        }

        return output_stage_1

    def process_insight(self, insight):
        if insight != "":
            _insight, filename = self.prepare_insight_question(insight)
            # print (_insight)
            # print (filename)
            response, status, output = self.get_output(_insight)
            # print (status)
            # print (response)
            # print (output)
            insight_plot = self.check_if_direct_plot_created(filename)
            # print (insight_plot)
            if insight_plot:
                filename = f"{filename}.png"
                return response, filename
            return None, None
        return None, None

    def chat_stage_2(self, input_stage_2):
        insight = input_stage_2["insight"]
        if input_stage_2["isInsight"]:
            insight_code, filename = self.process_insight(insight)
        else:
            insight_code, filename = None, None
        output_stage_2 = {
        "insight_plot_filename" : filename,
        "insight_code" : insight_code
        }
        return output_stage_2

    def chat(self, question):
        # time_sec = time()
        output_stage_1 = self.chat_stage_1(question)
        # print ("Summary Exec", time() - time_sec)
        # time_sec = time()
        output_stage_2 = self.chat_stage_2(input_stage_2 = output_stage_1)
        # print ("Insight Exec", time() - time_sec)
        for each in output_stage_2.keys():
            output_stage_1[each] = output_stage_2[each]
        return output_stage_1

    def python_to_sql(self, python_code):
        _python_code = self.prepare_python_to_sql(python_code)
        response = self.execute_prompt(_python_code)
        return response

    def python_explain(self, python_code):
        _python_code = self.prepare_python_explain(python_code)
        response = self.execute_prompt(_python_code)
        return response











