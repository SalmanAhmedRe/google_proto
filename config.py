import os
class Config:

    def __init__(self):
        self.csv_path = "data/MQL_dummy.csv"
        self.image_folder = "images/" #(Make sure to put / at the end)
        os.makedirs(self.image_folder, exist_ok=True)
        self.default_output_keys = ["summary", "code", "insight", "isInsight", "insight_code", "next_questions", "filename", "insight_plot_filename"]
        self.plot_words_dict = ["plot", "chart", "draw"]
        self.python_to_sql_convert_key = "sql_code"
        self.python_explain_key = "explaination"
        self.max_ = 3
        self.explore = {
            "insights" : ["Insight provides the count of each MQL Buyer Segment, with 'ITDM' being the most common segment with 273713 counts.",
                          "Insight displays the count of each MQL Routing Teams, with 'BDR' being the most common team with 328094 counts",
                          "Insight reveals the count of each MQL Priority, with 'B1' being the most common with 410014 counts.",
                          "While the ITDM segment led in generating MQLs, it would be beneficial to analyze the conversion rates of these leads to sales. This will provide a more comprehensive understanding of the effectiveness of marketing strategies targeted towards this segment."
,
                          "Insight shows the count of each MQL Status, with 'Dispositioned in SLA' having the highest count of 273442.",
                         ],
            "file_names" : ["8c589ca9-0baa-4a63-9112-0482ddd6953c.png",
                            "5b5c1a96-4a6d-43ed-9c81-e5a0175459bb.png",
                            "ae6659ff-9c50-4668-9077-54735cd148d8.png",
                            "40a3aa3f-da63-4baf-b413-18d2f7893329.png",
                            "1c3fe77c-f20e-405d-b2be-d1bc11525f58.png",
            ]
        }
        
