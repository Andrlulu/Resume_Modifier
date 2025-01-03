ANALYSIS_TEMPLATE = {
    "overallAnalysis": {
        "comment": "",
        "score": 0  # 0-100
    },
    "workExperience": [
        # Will match each work experience in resume
        {
            "companyName": "",  # To identify which experience
            "jobTitle": "",     # To identify which role
            "comment": "",
            "score": 0
        }
    ],
    "education": [
        # Will match each education entry in resume
        {
            "institutionName": "",  # To identify which education
            "degree": "",          # To identify which degree
            "comment": "",
            "score": 0
        }
    ],
    "achievements": {
        "comment": "",
        "score": 0
    },
    "project": [
        # Will match each project in resume
        {
            "title": "",  # To identify which project
            "comment": "",
            "score": 0
        }
    ]
}