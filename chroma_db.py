import chromadb

client = chromadb.CloudClient(
    api_key='ck-6Zjno7A9e53HXsUvS3uUbTYFpqtrRjzhbGkvkMt5UzZH',
    tenant='661221e6-8dc8-4645-b23c-0d1f18f72511',
    database='vector'
)

def create_portfolio_collection():
    # Create or get the portfolio collection
    collection = client.get_or_create_collection(name="portfolio")
    return collection

def insert_portfolio_data(collection):
    # Portfolio sections with their content
    portfolio_data = {
        "documents": [
            # Introduction & Personal Info
            """🤖 Hi there! I'm SolAI, a friendly chatbot created by Solai Rajan to help you with portfolio questions, tech topics, or just to have a fun chat! I can tell you all about Solai's experience, skills, and achievements.""",

            # Education section
            """🎓 Education Background:
            • BSc graduate with strong foundation in cloud computing and DevOps
            • AWS Solution Architect Associate Certification
            • Microsoft Certified: Azure Fundamentals""",

            # Skills section
            """🛠️ Technical Skills:
            • Cloud: AWS (API Gateway, Lambda, DynamoDB, VPC)
            • IaC: Terraform (infrastructure automation)
            • Programming: Python (serverless applications, automation)
            • DevOps: GitLab CI/CD, BDD testing, Pytest
            • Tools: Scalr, Redis, AWS Secrets Manager""",

            # Experience section
            """💼 Professional Experience:
            1. HTC Global Services - AWS Developer (2022 - present)
               • Developed and deployed scalable applications on AWS
               • Implemented CI/CD pipelines using GitLab and Terraform
               • Automated infrastructure provisioning
               • Integrated security scans in pipelines
               
            Total Experience: 5 years in IT industry focusing on cloud engineering and automation""",
            
            # Projects section
            """🚀 Notable Projects:
            1. Mainframe to AWS Modernization
               • Migrated legacy mainframe applications to AWS cloud infrastructure
               • Technologies: AWS, Terraform, Python, GitLab, Scalr, BDD
               • Successfully handled DB2 to DynamoDB migration

            2. High-Availability API Development
               • Built RESTful APIs using serverless architecture
               • Technologies: Python, AWS Lambda, API Gateway, DynamoDB
               • Implemented caching with Redis and secrets management""",
            
            # Security & DevOps
            """🔒 Cloud Security & DevOps Practices:
            • Implemented IAM policies and VPC security groups
            • Enforced encryption and compliance using AWS security tools
            • Automated CI/CD pipelines for cloud deployments
            • Followed infrastructure-as-code best practices""",

            # Contact Information
            """📬 Contact Information:
            • Portfolio Website: https://solairajan.online/
            • LinkedIn: https://www.linkedin.com/in/solai-rajan/
            • Email: solai13kamaraj@gmail.com
            • GitHub: https://github.com/Solairajan18""",

            # Fun Facts & Hobbies
            """🎮 Fun Facts & Hobbies:
            • Avid Clash of Clans player (Town Hall 15)
            • Favorite attack strategy: Hybrid Army (Hog Riders + Miners)
            • Enjoys learning new cloud technologies
            • Passionate about infrastructure optimization"""
        ],
        "metadatas": [
            {"section": "introduction", "type": "personal"},
            {"section": "education", "type": "qualifications"},
            {"section": "skills", "type": "technical"},
            {"section": "experience", "type": "professional"},
            {"section": "projects", "type": "portfolio"},
            {"section": "security", "type": "technical"},
            {"section": "contact", "type": "personal"},
            {"section": "hobbies", "type": "personal"}
        ],
        "ids": ["intro_001", "edu_001", "skills_001", "exp_001", "proj_001", "sec_001", "contact_001", "hobbies_001"]
    }
    
    # Add the data to the collection
    collection.add(
        documents=portfolio_data["documents"],
        metadatas=portfolio_data["metadatas"],
        ids=portfolio_data["ids"]
    )

def query_portfolio(collection, query_text):
    # Query the portfolio collection
    results = collection.query(
        query_texts=[query_text],
        n_results=2
    )
    return results

if __name__ == "__main__":
    # Create the collection
    portfolio_collection = create_portfolio_collection()
    
    # Insert portfolio data
    insert_portfolio_data(portfolio_collection)
    
    # Test query
    print("Testing portfolio query:")
    result = query_portfolio(portfolio_collection, "What are your technical skills?")
    print(result)