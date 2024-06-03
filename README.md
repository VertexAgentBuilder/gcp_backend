## Inspiration
The inspiration behind this project stemmed from the pervasive challenges customers face everyday with the products they have bought. We all know how frustrating it is to deal with complex privacy policies and user agreements packed with legal jargon and ambiguity. Trying to resolve issues related to warranty, technical support, billing, and payments feels like an endless battle, with notoriously slow and unpredictable results. The coordination between users and support teams can be a nightmare, and it doesn't help that customer care agents are often unavailable or unable to fully understand and address our concerns. This often leads to a dead end, where users are forced to seek other brand alternatives of their product, due to pent up user dissatisfaction. Also companies struggle to keep track of all the issue analytics over time, to estimate their customer care performance. 

By using advanced AI technologies like the Vertex AI Agent builder, RAG architecture and Gemini Pro models, we’re aiming to revolutionize customer support. Our goal is to offer a comprehensive, efficient, and user-friendly solution that ensures timely and accurate resolutions, ultimately enhancing our overall experience.

## How we built it

### Teams and Scopes

<!-- Add image from google drive -->
![image](https://drive.google.com/uc?export=view&id=1ns3OuQYeb7_INAuuC-TKIGYnWExhheSx)

We consider there are several teams for customer care support with their respective scopes of work. The schema of the team looks like this:
    
    ```
    {
        "teams":[
             {
                "teamName": "Warranty and Returns",
                "Members": [
                    "John Doe",
                    "Jane Doe"
                ],
                "Scope": [
                    "If user is not satisfied with the product, then they may ask for a refund or exchange or return",
                    "It checks the warranty of the product and then decides if the product is eligible for return or exchange",
                    "Advise the user on the return and exchange policy",
                    "Tells the user about the procedure to return the product"
                ]
            },
            ...
        ]
    }
    ```

### Agent Builder

![image](https://drive.google.com/uc?export=view&id=1jILGLpavwTFYavw63NEnjwtU-uKCYXVW)

Coming to the Agent Builder Part, firstly we create a `MainChat` agent which analyzes the Customer's issue and routes to the specialized agent.
It routes the context to these agents:

1. `WarrantyReturns` : This agent is responsible for handling the warranty and returns of the product. It checks the warranty of the product and then decides if the product is eligible for return or exchange. It advises the user on the return and exchange policy and tells the user about the procedure to return the product.

2. `TechnicalIssues`: This agent is responsible for handling the technical issues and software glitches of the product.

3. `ProductEnquiry`: This agent is responsible for handling the product enquiry of the product. It tells the user about the product details and the availability of the product.

4. `BillingPayment`: This agent is responsible for handling the billing and payment issues of the product. It tells the user about the payment methods and the billing details.

When the user asks a question, the `MainChat` agent analyzes the user's question and routes the context to the specialized agent. The specialized agent then answers the user's question. Each specialized agent has its own scope of work. It tries to answer the user's question based on its scope of work. It resolves the user's query and provides the user with the necessary information. When the chat conversation is over, the flow is handed back to the `MainChat` agent. It asks the user if he/she is satisfied with answer. It sends the `resolution_status` along with `issue_category` and `conversation` to a gcp function.

![image](https://drive.google.com/uc?export=view&id=1qNAHAlF8WtXHgNT44R0zGRVBe5DsYD9f)

Separately there is `PolicyHelperMain` agent which is responsible for handling the policy and agreement related queries. It tells the user about the company's policies and agreements. 

### Tools

`WarrantyReturns` and `TechnicalIssues` agents asks customer his/her `customer_id` in the beginning of the conversation. This is then passed to `gcp_function` via `customerlogs` tool to fetch the customer's previous logs and activities. This helps the agent to understand the customer's previous issues and provide better support.

`WarrantyReturns` and `TechnicalIssues` agents also uses `similarconv` tool to fetch the conversations from the database which are similar to the current conversation. This helps the agent to understand the past resolutions to the user's query and provide better support. In order to do this tool invokes a GCP function endpoint which runs an 'elastic search' to fetch the similar conversations. We use `cohere` embeddings and use `qdrant` vector search engine to fetch the similar conversations.


`MainChat` agent uses `sessionend` tool to send the `resolution_status` along with `issue_category` and `conversation` to a GCP function. This helps to keep track of the user's conversation and the resolution status of the conversation.

`PolicyHelperMain` agent uses `policyhelper` tool to fetch the company's policies and agreements from the database. It uses Vertex AI Agent builder's `Datastores` to store embeddings of chunks generated from the policies and agreements pdfs.

So, the tools are:
- `customerlogs`: Fetches the customer's previous logs and activities. Input is `customer_id`. Output is `Logs`.
- `similarconv`: Fetches the similar conversations from the database. Input is `query`. Output is `Similar Conversations`.
- `sessionend`: Sends the `resolution_status` along with `issue_category` and `conversation` to a GCP function. Returns `Success` if the data is sent successfully.
- `policyhelper`: Fetches the company's policies and agreements from the database. It is built using vertex ai agent builder's `Datastores`.


### Visualization and Dashboard

We store the data when `sessionend` tool is invoked. We maintain a `mongoDB` database to store `issue_category` and `resolution_status` along with current date and time. This data is then visualized in admin dashboard. It's a one-stop analytics page that shows the no. of resolved vs unresolved issues, issues in each category, and time-wise analysis in form of pie, bar and line charts. This helps the teams to take better decisions and improve the customer support. 

## Challenges we ran into

1. Routing of Issues:
Users can ask for a variety of queries. If we try to handle all the queries in a single agent, it will be difficult to manage the conversation. So we need to create specialized agents for each type of query. This will help to manage the conversation better. We thus create a `MainChat` agent which analyzes the user's query and routes the context to the specialized agent.

2. Handling Repeated Queries:
Some queries are commonly reported by the users. Instead of completing the entire conversation flow, we can simply provide the solutions that worked for others in the past. So we need to fetch the similar conversations from the database and provide the user with the past resolutions to the query. This will help the agent to understand the user's query better and provide better support.

3. Better Understanding of Policies and Agreements:
Some queries are related to the company's policies and agreements. If we try to answer the query without understanding the policies and agreements, it will be difficult to manage the conversation. Thus we fetch the company's policies and agreements from the database and provide the user with the necessary information. This will help the agent to understand the user's query better and provide better support.


## Accomplishments that we're proud of

1. More Personalized Customer Support:
We use `customerlogs` tool to fetch the customer's previous logs and activities stored in our database. This helps the agent to understand the customer's previous activity on our website.

3. Handling Repeated Queries:
We use `similarconv` tool to fetch the conversations of other users that occurred in the past and have been resolved, from the database which are similar to the current conversation. This helps the agent to understand the past resolutions to the user's query and provide solutions that actually work.

4. Better Understanding of Policies and Agreements:
We use `policyhelper` tool to fetch the company's policies and agreements from the database. It uses Vertex AI Agent builder's `Datastores` to store embeddings of chunks generated from the policies and agreements PDFs. It answers user queries regarding the privacy policies, user agreements of products bought, in a simple and easy-to-understand language.

5. Admin Dashboard And Visualization:
We visualize the data of `issue_category` and `resolution_status` of the user's conversation in admin dashboard. It's a one-stop analytics page that shows the no. of resolved vs unresolved issues, issues in each category, and time-wise analysis in form of pie, bar and line charts. This helps the teams to take better decisions and improve the customer support. 


## What we learned
- We learnt how easy it is to build complex GenAI-based chatbots using Vertex AI Agent builder in a low-code fashion. 
- We discovered the ease of integrating Data stores for Retrieval-Augmented Generation (RAG) models, enhancing the chatbot's ability to provide accurate and grounded responses to user queries. It created vector store for all the PDF files in few minutes and offered a no-code way to integrate that to the chatbot.
- Additionally, leveraging Tools to call OpenAPI cloud functions proved instrumental in seamlessly integrating external functionalities, enabling the chatbot to perform complex tasks such as retrieving or sending real-time data. 

## What's next for IssueVertexpert.AI
- Adding multi-modal support using Gemini Pro Vision models.
- Deploying the agent publicly so that anyone can access it.



## Environment Setup And Endpoints

### Requirement

- Python 3.9+

### Installation

- `pip install -r requirements.txt`

### Setting up the environment

```
COHERE_API_KEY=
QUDRANT_API_KEY=jFl_
QUDRANT_URL=https://2e76fa6d-
MONGO_URL="mongodb+srv:"
MONGO_DB="vertex"
SESSION_COLLECTION="session_collection"
```

### Endpoints

'main.py' contains the endpoints for the tools. It is hosted on `https://us-central1-agentbuilderhackathon.cloudfunctions.net/process_text`

1. `https://us-central1-agentbuilderhackathon.cloudfunctions.net/process_text/logs`

Sample Input payload:

```
{
    "customer":"9p0q1r2s3t4u5v6w"
}
```

2. `https://us-central1-agentbuilderhackathon.cloudfunctions.net/process_text/simsolution`

Sample Input payload:

```
{
    "query":"Yes but on the warranty portal its showing not activated, but I have activated it"
}
```

3. `https://us-central1-agentbuilderhackathon.cloudfunctions.net/process_text/sessionend`

Sample Input payload:

```
[
    {
        "issue_category":"Warranty and Returns Issues",
        "resolution_status":false,
        "conversation":"The user is satisfied with the answer"
    }
]
```

## UI Hosted at : [issue-vertex-bot](https://issue-vertex-bot.vercel.app/)



## Sample Test Cases

List of valid customer_ids: `3f4e5d6f7g8h9i0j`, `7h8i9j0k1l2m3n4o`, `5x6y7z8a9b0c1d2e`, `9p0q1r2s3t4u5v6w`


Visit our UI at [issue-vertex-bot](https://issue-vertex-bot.vercel.app/). In the bottom right corner, you can see the chatbot. You can ask the Type 1 queries on clicking it. On clicking 'Policy' button at top right corner, you enter 'https://issue-vertex-bot.vercel.app/policies' page where you can ask the Type 2 queries.

<img src="https://drive.google.com/uc?export=view&id=10SFEyW7fWMUZ4bFQltljwi4NekpTr7jr" alt="Description" width="700" />

<img src="https://drive.google.com/uc?export=view&id=19tG9ohZhDugIO4e-cJJAv1let2hJPbKm" alt="Description" width="700" />


### Type 1: 

**User**: "Hi, I have a problem with my product. Can you help me?"

- `MainChat` agent treats this as a general query. So no routing is done. It asks the user to provide more details about the issue.

**User**: "I have availed the warranty for my product. But, I am facing some issues with it."

- `MainChat` agent routes the context to `WarrantyReturns` agent.

- `WarrantyReturns` agent asks for the `customer_id`

**User**: "Yeah sure! My ID is 3f4e5d6f7g8h9i0j"

- `WarrantyReturns` agent fetches the customer's previous logs and activities using `customerlogs` tool.
- From the logs, it is found that the user has availed the warranty for the product.

**User**: "But in the warranty portal it is showing that the warranty is yet to be activated. But, I have already activated it."

- `WarrantyReturns` agent fetches the similar conversations from the database using `similarconv` tool.
- `WarrantyReturns` agent provides the user with the necessary information.

**User**: "Thank you for your assistance."

- `WarrantyReturns` asks for if there is anything else the user wants to know

**User**: "No, that's all. Thank you for your help."

- Handover to `MainChat` agent. `MainChat` agent asks if the user is satisfied with the answer.

**User**: "Yes, I am satisfied with the answer"

- `MainChat` agent sends the `resolution_status` along with `issue_category` and `conversation` to a GCP function using `sessionend` tool.

**User**: "I have another query regarding some recently launched products"

- `MainChat` agent routes the context to `ProductEnquiry` agent.
- `ProductEnquiry` agent asks for exact product name or category.

**User**: "I want to know about Poco X4"

- `ProductEnquiry` agent fetches the product details from the database using `productcatalog` tool which is built upon `Datastores`.
- `ProductEnquiry` agent provides the user with the necessary information.

**User**: "Does it support 5G?"

- `ProductEnquiry` agent provides the user with the necessary information.

**User**: "What colors are available?"

- `ProductEnquiry` agent provides the user with the necessary information.

**User**: "What is the price of it?"

- `ProductEnquiry` agent provides the user with the necessary information.

**User**: "Could you suggest which spec would be the most budget friendly option?"

- `ProductEnquiry` agent provides the user with the necessary information.

**User**: "Thank you for the information"

- Handover to `MainChat` agent. `MainChat` agent asks if the user is satisfied with the answer.

**User**: "Yes, I am satisfied with the answer"

- `MainChat` agent sends the `resolution_status` along with `issue_category` and `conversation` to a GCP function using `sessionend` tool.


### Type 2:

**User**: "Hi"

- `PolicyHelperMain` agent treats this as a general query. 

**User**: "I want to know if Xiaomi will leak my personal data, according to the privacy policy of my POCO phone."

- `PolicyHelperMain` agent fetches the company's policies and agreements from the database using `policyhelper` tool.
- `PolicyHelperMain` agent provides the user with the necessary information.

**User**: "Oh that's reassuring! Btw can you explain the rules and obligations I have towards POCO?"

- `PolicyHelperMain` agent fetches the company's privacy policies from the database using `policyhelper` tool.
- `PolicyHelperMain` agent provides the user with the necessary information.

**User**: "Ok that's nice to know!"

- 'PolicyHelperMain' agent asks for if there is anything else the user wants to know

**User**: "No, that's all. Thank you for your help."
